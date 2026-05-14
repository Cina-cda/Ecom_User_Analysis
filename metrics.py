# src/metrics.py
"""用户基础指标与分层模块：严格按照 notebook 模块二代码实现，保持 user_id 为索引"""

import pandas as pd
from src.config import ANALYSIS_END_DATE


def compute_user_stats(users_orders: pd.DataFrame) -> pd.DataFrame:
    """
    计算每个用户的基础统计指标（模块二第4题）
    返回 DataFrame，索引为 user_id，列包含：
        first_order_date, last_order_date, total_orders, total_amount, avg_order_value
    """
    user_detail = (
        users_orders
        .groupby('user_id')
        .agg(
            first_order_date=('order_date', 'min'),
            last_order_date=('order_date', 'max'),
            total_orders=('order_id', 'nunique'),
            total_amount=('amount', 'sum'),
            avg_order_value=('amount', 'mean')
        )
    )
    # 不 reset_index，保持 user_id 作为索引（与 notebook 完全一致）
    return user_detail


def compute_rfm(user_detail: pd.DataFrame) -> pd.DataFrame:
    """
    计算 RFM 分层（模块二第5题）
    user_detail 索引为 user_id，包含列 last_order_date, total_orders, total_amount
    返回 DataFrame 包含列：user_id, R_score, F_score, M_score, RFM_total, segment
    """
    # 注意：user_detail 的索引是 user_id，但我们需要将其作为普通列输出
    user_detail_reset = user_detail.reset_index()  # 仅用于提取列，不改变原结构
    end_date = pd.Timestamp(ANALYSIS_END_DATE)
    R = (end_date - user_detail['last_order_date']).dt.days
    F = user_detail['total_orders']
    M = user_detail['total_amount']

    rfm = pd.DataFrame({'R': R, 'F': F, 'M': M})

    rfm['Rs'] = pd.qcut(rfm['R'], q=4, labels=[4, 3, 2, 1])
    rfm['Fs'] = pd.qcut(rfm['F'], q=4, labels=[1, 2, 3, 4])
    rfm['Ms'] = pd.qcut(rfm['M'], q=4, labels=[1, 2, 3, 4])

    rfm['RFM_T'] = rfm['Rs'].astype(int) + rfm['Fs'].astype(int) + rfm['Ms'].astype(int)
    rfm['segment'] = pd.cut(rfm['RFM_T'],
                            bins=[0, 7, 10, 999],
                            labels=['低价值', '中价值', '高价值'],
                            right=False)

    rfm_df = rfm[['Rs', 'Fs', 'Ms', 'RFM_T', 'segment']].rename(columns={
        'Rs': 'R_score', 'Fs': 'F_score', 'Ms': 'M_score', 'RFM_T': 'RFM_total'
    })
    rfm_df['user_id'] = user_detail_reset['user_id'].values
    rfm_df = rfm_df[['user_id', 'R_score', 'F_score', 'M_score', 'RFM_total', 'segment']]
    return rfm_df


def compute_category_preference(users_orders: pd.DataFrame) -> pd.DataFrame:
    """
    计算每个用户消费最多的商品类别（模块二第6题）
    返回 DataFrame 包含列：user_id, top_category, category_amount
    """
    user_category_amount = (
        users_orders
        .groupby(['user_id', 'product_category'])['amount']
        .sum()
        .reset_index()
    )
    user_category_amount['total_amount'] = user_category_amount.groupby('user_id')['amount'].transform('sum')
    user_category_amount['rate'] = user_category_amount['amount'] / user_category_amount['total_amount']
    user_top1category = (
        user_category_amount
        .sort_values(['user_id', 'rate'])
        .groupby('user_id')
        .last()
        .reset_index()
    )
    user_prefer_category = (
        user_top1category[['user_id', 'product_category', 'amount']]
        .rename(columns={'product_category': 'top_category', 'amount': 'category_amount'})
    )
    return user_prefer_category