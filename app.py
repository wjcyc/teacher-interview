# -*- coding: utf-8 -*-
"""Teacher Interview Practice System - Flask Main Application"""
import json, datetime, sqlite3, random, os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import *
from database import get_db, init_db
import seed_data_v3 as full_seed
import content_updater
app = Flask(__name__)
app.secret_key = "hefei_music_interview_2026"
@app.template_filter("date")
def date_filter(ts):
    if not ts: return ""
    return ts[:10] if isinstance(ts, str) else str(ts)[:10]
@app.template_filter("time")
def time_filter(secs):
    if not secs: return "0m00s"
    m = int(secs)//60; s = int(secs)%60
    return f"{m}m{s}s" if m else f"{s}s"

@app.context_processor
def inject_user():
    from config import USER_INFO
    return dict(user=USER_INFO)

@app.route("/")
def index():
    db = get_db()
    q_count = db.execute("SELECT COUNT(*) FROM questions WHERE is_active=1 AND category_id<=12").fetchone()[0]
    tip_count = db.execute("SELECT COUNT(*) FROM questions WHERE is_active=1 AND category_id>=13").fetchone()[0]
    record_count = db.execute("SELECT COUNT(*) FROM simulation_records").fetchone()[0]
    bookmark_count = db.execute("SELECT COUNT(*) FROM bookmarks").fetchone()[0]
    recent = db.execute("""SELECT s.*, q.title FROM simulation_records s
        JOIN questions q ON s.question_id=q.id
        ORDER BY s.started_at DESC LIMIT 5""").fetchall()
    today = datetime.date.today().isoformat()
    ds = db.execute("SELECT * FROM daily_stats WHERE stat_date=?", (today,)).fetchone()
    return render_template("index.html",
        question_count=q_count, tip_count=tip_count,
        record_count=record_count, bookmark_count=bookmark_count,
        recent=recent, daily=ds)
@app.route("/questions")
def questions():
    db = get_db()
    cat_type = request.args.get("type", "structured")
    cat_id = request.args.get("cat", "")
    search = request.args.get("q", "")
    cats = db.execute("SELECT * FROM categories WHERE type=? ORDER BY sort_order", (cat_type,)).fetchall()
    query = """SELECT q.*, c.name as cat_name FROM questions q
        JOIN categories c ON q.category_id=c.id
        WHERE c.type=? AND q.is_active=1"""
    params = [cat_type]
    if cat_id:
        query += " AND q.category_id=?"
        params.append(cat_id)
    if search:
        query += " AND (q.title LIKE ? OR q.content LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY q.category_id, q.id"
    qs = db.execute(query, params).fetchall()
    bm_ids = set(r["question_id"] for r in db.execute("SELECT question_id FROM bookmarks").fetchall())
    return render_template("questions.html", questions=qs, categories=cats,
        active_type=cat_type, active_cat=cat_id, search=search, bookmark_ids=bm_ids)
@app.route("/api/questions/random")
def random_question():
    mode = request.args.get("mode", "structured")
    db = get_db()
    q = db.execute("""SELECT q.*, c.name as cat_name FROM questions q
        JOIN categories c ON q.category_id=c.id
        WHERE c.type=? AND q.is_active=1 ORDER BY RANDOM() LIMIT 1""", (mode,)).fetchone()
    if q: return jsonify(dict(q))
    return jsonify({"error":"no questions"}), 404
@app.route("/api/questions/<int:qid>")
def get_question(qid):
    db = get_db()
    q = db.execute("""SELECT q.*, c.name as cat_name FROM questions q
        JOIN categories c ON q.category_id=c.id WHERE q.id=?""", (qid,)).fetchone()
    if q: return jsonify(dict(q))
    return jsonify({"error":"not found"}), 404
@app.route("/api/questions/<int:qid>/bookmark", methods=["POST"])
def toggle_bookmark(qid):
    data = request.get_json() or {}
    btype = data.get("type", "bookmark")
    db = get_db()
    existing = db.execute("SELECT id FROM bookmarks WHERE question_id=?", (qid,)).fetchone()
    if existing:
        db.execute("DELETE FROM bookmarks WHERE question_id=?", (qid,))
        msg = "Cancelled"
    else:
        db.execute("INSERT INTO bookmarks (question_id,type) VALUES (?,?)", (qid, btype))
        msg = "Collected"
    db.commit()
    return jsonify({"msg": msg, "bookmarked": not existing})
@app.route("/simulate")
def simulate():
    qid = request.args.get("qid", "")
    mode = request.args.get("mode", "structured")
    db = get_db()
    cats = db.execute("SELECT * FROM categories WHERE type=? ORDER BY sort_order", (mode,)).fetchall()
    cat_id = request.args.get("cat", "")
    if qid:
        q = db.execute("""SELECT q.*,c.name as cat_name FROM questions q
            JOIN categories c ON q.category_id=c.id
            WHERE q.id=?""", (qid,)).fetchone()
    else:
        params = [mode]
        query = """SELECT q.*,c.name as cat_name FROM questions q
            JOIN categories c ON q.category_id=c.id
            WHERE c.type=? AND q.is_active=1"""
        if cat_id:
            query += " AND q.category_id=?"
            params.append(cat_id)
        query += " ORDER BY RANDOM() LIMIT 1"
        q = db.execute(query, params).fetchone()
    if not q:
        return render_template("simulate.html", no_questions=True,
            prep_time=STRUCTURED_PREP_TIME, ans_time=STRUCTURED_ANSWER_TIME,
            mode=mode, categories=cats, active_cat=cat_id)
    if mode == "trial":
        pt, at = TRIAL_PREP_TIME, TRIAL_ANSWER_TIME
    else:
        pt, at = STRUCTURED_PREP_TIME, STRUCTURED_ANSWER_TIME
    return render_template("simulate.html", question=dict(q),
        prep_time=pt, ans_time=at, mode=mode, categories=cats, active_cat=cat_id)
@app.route("/api/simulate/complete", methods=["POST"])
def complete_simulation():
    data = request.get_json()
    db = get_db()
    db.execute("""INSERT INTO simulation_records(question_id,mode,ended_at,preparation_seconds,answer_seconds,notes)
        VALUES(?,?,datetime('now','localtime'),?,?,?)""",
        (data["question_id"],data["mode"],data.get("prep_secs",0),data.get("ans_secs",0),data.get("notes","")))
    record_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    for s in data.get("scores",[]):
        db.execute("INSERT INTO scores(record_id,dimension,score,max_score)VALUES(?,?,?,?)",
            (record_id, s["dimension"], s["score"], s["max"]))
    today = datetime.date.today().isoformat()
    ds = db.execute("SELECT * FROM daily_stats WHERE stat_date=?", (today,)).fetchone()
    if ds:
        db.execute("UPDATE daily_stats SET simulations_done=simulations_done+1 WHERE stat_date=?", (today,))
    else:
        db.execute("INSERT INTO daily_stats(stat_date,simulations_done)VALUES(?,1)", (today,))
    db.commit()
    return jsonify({"record_id": record_id})
@app.route("/tips")
def tips():
    db = get_db()
    tip_cats = db.execute("SELECT * FROM categories WHERE type='tip' ORDER BY sort_order").fetchall()
    pitfall_cats = db.execute("SELECT * FROM categories WHERE type='pitfall' ORDER BY sort_order").fetchall()
    cat_id = request.args.get("cat","")
    tab = request.args.get("tab","tip")
    qs = []
    if cat_id:
        qs = db.execute("""SELECT q.*,c.name as cat_name FROM questions q
            JOIN categories c ON q.category_id=c.id
            WHERE q.category_id=? AND q.is_active=1 ORDER BY q.id""",(cat_id,)).fetchall()
    else:
        fc = db.execute("SELECT id FROM categories WHERE type=? ORDER BY sort_order LIMIT 1",(tab,)).fetchone()
        if fc:
            qs = db.execute("""SELECT q.*,c.name as cat_name FROM questions q
                JOIN categories c ON q.category_id=c.id
                WHERE q.category_id=? AND q.is_active=1 ORDER BY q.id""",(fc["id"],)).fetchall()
    return render_template("tips.html", tip_categories=tip_cats, pitfall_categories=pitfall_cats,
        articles=qs, active_tab=tab, active_cat=cat_id)
@app.route("/records")
def records():
    db = get_db()
    recs = db.execute("""SELECT s.*,q.title,q.content,
        (SELECT SUM(score) FROM scores WHERE record_id=s.id) as total_score,
        (SELECT SUM(max_score) FROM scores WHERE record_id=s.id) as total_max
        FROM simulation_records s JOIN questions q ON s.question_id=q.id
        ORDER BY s.started_at DESC LIMIT 50""").fetchall()
    return render_template("records.html", records=recs)
@app.route("/api/records/<int:rid>")
def record_detail(rid):
    db = get_db()
    rec = db.execute("""SELECT s.*,q.title,q.content,q.answer_outline
        FROM simulation_records s JOIN questions q ON s.question_id=q.id
        WHERE s.id=?""",(rid,)).fetchone()
    scores = db.execute("SELECT * FROM scores WHERE record_id=?",(rid,)).fetchall()
    if not rec: return jsonify({"error":"not found"}),404
    return jsonify({"record":dict(rec),"scores":[dict(s) for s in scores]})
@app.route("/stats")
def stats():
    db = get_db()
    days30 = db.execute("SELECT * FROM daily_stats ORDER BY stat_date DESC LIMIT 30").fetchall()
    dim_scores = db.execute("""SELECT dimension,AVG(score)as avg_score,AVG(max_score)as avg_max,
        COUNT(*)as count FROM scores GROUP BY dimension ORDER BY avg_score DESC""").fetchall()
    return render_template("stats.html", days30=days30, dim_scores=dim_scores)
@app.route("/api/stats/timeline")
def stats_timeline():
    db = get_db()
    data = db.execute("SELECT stat_date,simulations_done,questions_reviewed FROM daily_stats ORDER BY stat_date ASC LIMIT 90").fetchall()
    return jsonify([dict(r) for r in data])
@app.route("/bookmarks")
def bookmarks():
    db = get_db()
    bm = db.execute("""SELECT b.*,q.title,q.content,c.name as cat_name
        FROM bookmarks b JOIN questions q ON b.question_id=q.id
        JOIN categories c ON q.category_id=c.id
        ORDER BY b.created_at DESC""").fetchall()
    return render_template("bookmarks.html", bookmarks=bm)
if __name__ == "__main__":
    init_db()
    full_seed.seed_all()
    content_updater.load_detailed_content()
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=False, host="0.0.0.0", port=port)
