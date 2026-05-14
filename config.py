# src/config.py
"""配置文件：路径、参数、常量，并自动创建所需目录"""

import os
from pathlib import Path

# ---------- 路径配置 ----------
# 项目根目录（config.py 位于 src 目录下，取父目录）
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
ORDERS_FILE = DATA_DIR / "20260511user_orders.csv"

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "outputs"
EXCEL_FILE_PREFIX = "user_lifecycle"   # 文件名会加上日期

# 自动创建目录
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- 分析参数 ----------
# 数据日期范围（用于R指标、流失定义等）
ANALYSIS_END_DATE = '2022-12-31'

# 流失定义：末次购买距结束日期超过此天数视为流失
LOST_DAYS_THRESHOLD = 60

# RFM 打分分位数（默认四分位，不改）
# 留存曲线展示的最大月数
MAX_RETENTION_MONTHS = 6

# 复购周期直方图 bins
REPURCHASE_HIST_BINS = 30

# ---------- Excel 格式 ----------
FLOAT_DECIMALS = 2
MAX_COL_WIDTH = 30
EXCEL_INCLUDE_INDEX = False