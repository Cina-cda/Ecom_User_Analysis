# src/repurchase_retention.py
"""复购与留存分析模块：严格按照 notebook 模块三代码实现"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.config import REPURCHASE_HIST_BINS


def compute_repeat_purchase_rate(user_detail: pd.DataFrame) -> str:
    """
    计算整体复购率（模块三第7题前部分）
    user_detail 需包含 total_orders 列
    返回字符串，格式如 'xx.xx%'
    """
    fugou_user = user_detail.query('total_orders >= 2')
    rate = f"{len(fugou_user) * 100 / len(user_detail):.2f}%"
    return rate


def compute_monthly_repeat_rate(users_orders: pd.DataFrame) -> pd.DataFrame:
    """
    计算按月复购率（当月购买的用户在下个月再次购买的比例）（模块三第7题后部分）
    返回 DataFrame 包含 order_month, month_fugou_rate
    """
    # 提取用户购买的月份（去重）
    user_month = (
        users_orders.loc[:, ['user_id', 'order_month']]
        .sort_values(['user_id', 'order_month'])
        .drop_duplicates()
    )
    # 计算每个用户下一次购买的月份
    user_month['next_purchase'] = user_month.groupby('user_id')['order_month'].shift(-1)
    # 判断是否为下月复购（月份差为1）
    user_month['is_monthfugou'] = (user_month['next_purchase'] == user_month['order_month'] + 1)
    # 按月汇总
    month_fugou = (
        user_month
        .groupby('order_month')
        .agg(
            fugou_user=('is_monthfugou', 'sum'),
            total_user=('user_id', 'nunique')
        )
        .reset_index()
    )
    month_fugou['month_fugou_rate'] = month_fugou['fugou_user'] * 100 / month_fugou['total_user']
    month_fugou_df = month_fugou[['order_month', 'month_fugou_rate']]
    return month_fugou_df


def compute_repurchase_cycle(users_orders: pd.DataFrame, user_detail: pd.DataFrame) -> pd.DataFrame:
    """
    计算复购周期（模块三第8题）
    user_detail 需包含 total_orders 列，用于筛选至少2次订单的用户
    返回 DataFrame 包含 user_id, median, avg (复购周期中位数和均值，保留一位小数)
    """
    # 提取至少2次订单的用户
    fugou_user_index = user_detail.query('total_orders >= 2').index
    # 过滤这些用户的订单日期
    user_month = (
        users_orders
        .set_index('user_id')
        .loc[fugou_user_index, ['order_date']]
        .sort_values(['user_id', 'order_date'])
    )
    # 计算相邻订单间隔（天）
    user_month['next_purchase'] = user_month.groupby('user_id')['order_date'].shift(-1)
    user_month['chazhi'] = (user_month['next_purchase'] - user_month['order_date']).dt.days
    # 按用户汇总中位数和均值
    fugou_zhouqi = (
        user_month
        .groupby('user_id')
        .agg(median=('chazhi', 'median'), avg=('chazhi', 'mean'))
        .reset_index()
    )
    # 保留一位小数
    fugou_zhouqi_df = fugou_zhouqi.round(1)
    return fugou_zhouqi_df


def plot_repurchase_cycle_distribution(fugou_zhouqi_df: pd.DataFrame) -> None:
    """
    绘制复购周期分布直方图（模块三第8题可选，但 notebook 中有）
    参数 fugou_zhouqi_df 需包含 avg 列
    """
    sns.set_style('whitegrid')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常显示中文
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(12, 6))
    sns.histplot(fugou_zhouqi_df['avg'], bins=REPURCHASE_HIST_BINS, kde=True, color='skyblue')
    plt.title('用户平均复购周期分布', fontsize=14)
    plt.xlabel('平均复购周期（天）', fontsize=12)
    plt.ylabel('用户数', fontsize=12)
    plt.tight_layout()
    plt.show()


def compute_retention_matrix(users_orders: pd.DataFrame) -> pd.DataFrame:
    """
    计算用户留存曲线（按首次购买月份分组）（模块三第9题）
    返回透视表：行=首次购买月份，列=偏移月数（1~6），值=留存率
    """
    # 去重 user_id + order_month
    users_orders_liucun = (
        users_orders[['user_id', 'order_month']]
        .drop_duplicates(['user_id', 'order_month'])
        .sort_values('user_id')
    )
    # 每个用户的首购月份（cohort）
    users_orders_liucun['first_cohort'] = users_orders_liucun.groupby('user_id')['order_month'].transform('min')
    # 计算偏移量（月份差）
    users_orders_liucun['pianyi_liang'] = (users_orders_liucun['order_month'] - users_orders_liucun['first_cohort']).apply(lambda x: x.n)
    # 计算每个 cohort 每个偏移量的用户数
    cohort_counts = (
        users_orders_liucun
        .groupby(['first_cohort', 'pianyi_liang'])['user_id']
        .nunique()
        .reset_index(name='user_count')
    )
    # 每个 cohort 的总用户数（偏移为0）
    per_cohort_user = (
        cohort_counts[cohort_counts['pianyi_liang'] == 0][['first_cohort', 'user_count']]
        .rename(columns={'user_count': 'total_cohort_user'})
    )
    cohort_counts = cohort_counts.merge(per_cohort_user, on='first_cohort', how='left')
    cohort_counts['liucun_rate'] = cohort_counts['user_count'] * 100 / cohort_counts['total_cohort_user']
    # 透视表，仅取偏移1~6
    liucun_df = (
        cohort_counts[cohort_counts['pianyi_liang'].between(1, 6)]
        .pivot_table(index='first_cohort', columns='pianyi_liang', values='liucun_rate', fill_value=0)
    )
    return liucun_df