# src/lifetime.py
"""生命周期与流失预警模块：严格按照 notebook 模块四代码实现"""

import pandas as pd
from src.config import ANALYSIS_END_DATE, LOST_DAYS_THRESHOLD


def compute_ltv_top10(user_detail: pd.DataFrame) -> pd.DataFrame:
    """
    计算用户生命周期价值（LTV）粗估，输出前10名（模块四第10题）
    user_detail 需包含列：user_id, first_order_date, last_order_date,
                         total_amount, avg_order_value
    返回 DataFrame 列：user_id, LTV, active_days, avg_daily_spend
    """
    ltv = user_detail[['first_order_date', 'last_order_date', 'total_amount', 'avg_order_value']].copy()
    # 活跃天数
    ltv['active_days'] = (ltv['last_order_date'] - ltv['first_order_date']).dt.days
    # 日均消费
    ltv['avg_daily_spend'] = ltv['total_amount'] / ltv['active_days']
    # 选取前十，按 total_amount 即 LTV 降序
    ltv_top10_df = (
        ltv[['total_amount', 'active_days', 'avg_daily_spend']]
        .rename(columns={'total_amount': 'LTV'})
        .reset_index()
        .sort_values('LTV', ascending=False)
        .head(10)
    )
    return ltv_top10_df


def identify_lost_users(user_detail: pd.DataFrame, users_orders: pd.DataFrame) -> pd.DataFrame:
    """
    识别流失用户并汇总特征（模块四第11题）
    user_detail 需包含列：user_id, last_order_date, total_orders, total_amount
    users_orders 需包含列：user_id, product_category
    返回 DataFrame 包含：lost_user, lost_rate, avg_total_orders, avg_total_amount, main_product_category
    """
    end_date = pd.Timestamp(ANALYSIS_END_DATE)
    lost_df = user_detail.reset_index().copy()
    lost_df['is_lost'] = ((end_date - lost_df['last_order_date']).dt.days) > LOST_DAYS_THRESHOLD

    lost_rate = lost_df['is_lost'].sum() * 100 / len(user_detail)

    # 提取流失用户
    lost_users = lost_df.query('is_lost == 1')
    # 平均总订单数和平均总金额
    avg_total_orders = lost_users['total_orders'].mean()
    avg_total_amount = lost_users['total_amount'].mean()

    # 合并商品类别，找出流失用户中最偏好的类别（众数）
    lost_users_with_cat = lost_users.merge(users_orders[['user_id', 'product_category']], on='user_id')
    # 统计每个类别下的流失用户数（去重用户）
    cat_counts = lost_users_with_cat.groupby('product_category')['user_id'].nunique().sort_values(ascending=False)
    main_category = cat_counts.head(1).index[0] if len(cat_counts) > 0 else None

    result = pd.DataFrame({
        'lost_user': [lost_users['is_lost'].sum()],
        'lost_rate': [lost_rate],
        'avg_total_orders': [avg_total_orders],
        'avg_total_amount': [avg_total_amount],
        'main_product_category': [main_category]
    }, index=[0])
    return result