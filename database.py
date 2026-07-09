# -*- coding: utf-8 -*-
"""数据库初始化和管理"""
import sqlite3
import os
from config import DATABASE_PATH
import sqlite3
_db = None
def get_db():
    global _db
    if _db is None:
        _db = sqlite3.connect(":memory:", check_same_thread=False)
        _db.row_factory = sqlite3.Row
        _db.execute("PRAGMA foreign_keys = ON")
    return _db
def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            type TEXT NOT NULL, sort_order INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL,
            title TEXT NOT NULL, content TEXT NOT NULL,
            answer_outline TEXT, difficulty INTEGER DEFAULT 3,
            is_active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS simulation_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL, mode TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP, preparation_seconds INTEGER,
            answer_seconds INTEGER, notes TEXT);
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL, dimension TEXT NOT NULL,
            score REAL NOT NULL, max_score REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL UNIQUE, type TEXT DEFAULT 'bookmark',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS study_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL UNIQUE,
            reviewed_count INTEGER DEFAULT 0,
            last_reviewed TIMESTAMP, confidence INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date TEXT UNIQUE NOT NULL,
            simulations_done INTEGER DEFAULT 0,
            questions_reviewed INTEGER DEFAULT 0,
            total_score REAL DEFAULT 0, max_score REAL DEFAULT 0);""")
