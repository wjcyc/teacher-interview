# -*- coding: utf-8 -*-
"""教师考编面试系统 - 配置文件"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite 数据库文件路径
DATABASE_PATH = os.path.join(BASE_DIR, "data", "interview.db")

# 面试计时默认值（秒）
STRUCTURED_PREP_TIME = 60       # 结构化面试准备时间：1分钟
STRUCTURED_ANSWER_TIME = 300    # 结构化面试答题时间：5分钟
TRIAL_PREP_TIME = 600           # 试讲备课时间：10分钟（合肥经开区通常备课30分钟，模拟时设为10分钟练习版）
TRIAL_ANSWER_TIME = 900         # 试讲时间：15分钟（合肥经开区通常15分钟）

# 评分维度
STRUCTURED_DIMENSIONS = [
    {"id": "logic", "name": "逻辑清晰度", "max": 25, "desc": "观点明确、条理清晰、论证充分"},
    {"id": "education", "name": "教育理念", "max": 25, "desc": "体现素质教育理念、以学生为中心"},
    {"id": "language", "name": "语言表达", "max": 25, "desc": "普通话标准、表达流畅、有感染力"},
    {"id": "mentality", "name": "心理素质", "max": 25, "desc": "情绪稳定、应变能力强、自信大方"},
]

TRIAL_DIMENSIONS = [
    {"id": "objective", "name": "教学目标", "max": 20, "desc": "目标明确、符合课标和学情"},
    {"id": "design", "name": "教学设计", "max": 25, "desc": "环节完整、重点突出、方法得当"},
    {"id": "implementation", "name": "教学实施", "max": 30, "desc": "讲授清晰、互动有效、板书规范"},
    {"id": "quality", "name": "教师素养", "max": 25, "desc": "教态自然、语言规范、专业功底扎实"},
]

# 笔试排名信息
USER_INFO = {
    "name": "考生",
    "subject": "初中音乐",
    "district": "合肥经济技术开发区",
    "recruit_count": 11,
    "interview_count": 22,
    "written_rank": 15,
    "written_total": 22,
}
