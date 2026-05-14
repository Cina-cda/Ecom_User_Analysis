# src/preprocessing.py
"""数据预处理模块：缺失值填充、异常值删除、时间特征提取"""

import pandas as pd


def preprocess_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
        1. 转换 order_date 为 datetime
        2. 删除 amount 缺失或 <=0 的行
        3. payment_method 缺失填充为 '未知'
        4. 删除 order_date 不在 2022-01-01 至 2022-12-31 之间的行
        5. 删除重复的 order_id（保留第一条）
        6. 提取时间特征：order_year, order_month, order_dayofweek, order_quarter
    """
    df = df.copy()
    # 日期列转换
    df['order_date'] = pd.to_datetime(df['order_date'])
    # 清洗数据
    df = df.query('amount > 0')
    df['payment_method'] = df['payment_method'].fillna('未知')
    df = df.query('"2022-01-01" <= order_date <= "2022-12-31"')
    df = df.drop_duplicates('order_id')
    # 提取特征
    df['order_year'] = df['order_date'].dt.to_period('Y')
    df['order_month'] = df['order_date'].dt.to_period('M')
    df['order_dayofweek'] = df['order_date'].dt.weekday
    df['order_quarter'] = df['order_date'].dt.to_period('Q')
    return df