# src/data_loader.py
"""数据加载模块：严格按照 notebook 读取 CSV 并转换 order_date 为 datetime"""

import pandas as pd
from src.config import ORDERS_FILE


def load_orders() -> pd.DataFrame:
    """读取用户订单数据，并将 order_date 转换为 datetime 类型"""
    df = pd.read_csv(ORDERS_FILE)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df