# 电商用户复购与生命周期分析

## 项目简介

本项目对电商平台用户订单数据进行深度分析，涵盖数据清洗、用户分层（RFM）、复购行为分析、留存曲线、生命周期价值（LTV）粗估及流失预警。输出可视化图表和格式化 Excel 报告，为精细化运营提供数据支持。

**分析指标包括**：
- 用户基础统计（首购/末购日期、订单数、消费金额、客单价）
- RFM 分层（高/中/低价值用户）
- 商品类别偏好（用户消费最多的品类）
- 整体复购率 + 按月复购率
- 复购周期分布（直方图 + 中位数/均值）
- 用户留存曲线（按月 cohort，前6个月）
- 生命周期价值（LTV）前十用户
- 流失用户识别与特征汇总（流失率、平均订单数/金额、偏好品类）

**技术特点**：
- 严格复现原始 Jupyter Notebook 的所有业务逻辑
- 采用混合模式：核心函数封装为 `.py` 模块，主流程保留在 Notebook 中，兼顾复用性与可读性
- 支持 Excel 自动导出（多 Sheet、列宽自适应、标题加粗、数字两位小数）
- 关键参数（日期范围、流失阈值、直方图 bins 等）集中在 `config.py` 中管理

## 项目结构
### user_lifecycle_analysis/
### │
### ├── data/ # 原始数据（需自行放置）
#### │ └── YYYYMMDDuser_orders.csv
### │
### ├── src/ # Python 核心模块
#### │ ├── config.py # 配置（路径、参数）
#### │ ├── data_loader.py # 数据加载
#### │ ├── preprocessing.py # 清洗、时间特征提取
#### │ ├── metrics.py # 用户基础统计、RFM、类别偏好
#### │ ├── repurchase_retention.py # 复购率、复购周期、留存曲线
#### │ ├── lifetime.py # LTV、流失用户识别
#### │ └── report_exporter.py # Excel 报告生成
#### │
### ├── main_analysis.ipynb # 主 Notebook（执行完整分析）
#### │
### ├── outputs/ # 运行后自动生成
#### │ └── user_lifecycle_YYYYMMDD.xlsx
#### │
### ├── requirements.txt # Python 依赖
#### ├── README.md # 本文件

## 环境要求

- Python 3.12+
- 依赖库：pandas, numpy, matplotlib, seaborn, xlsxwriter, openpyxl

## 快速开始

### 1. 克隆或下载项目
### 2. 安装依赖
### 3. 准备数据
将原始订单数据 20260511user_orders.csv 放入 data/ 目录。

数据需包含以下列（列名必须一致）：

user_id：用户ID

order_id：订单ID（唯一）

order_date：订单日期（格式 YYYY-MM-DD）

amount：订单金额

payment_method：支付方式

product_category：商品类别


### 4. 运行分析
打开 main_analysis.ipynb，依次执行所有单元格（或点击 “Run All”）。

### 5. 查看结果
控制台输出各分析步骤的中间结果。

复购周期分布直方图会弹出显示。

Excel 报告保存在 outputs/ 目录下，文件名格式 user_lifecycle_YYYYMMDD.xlsx。

### Excel 报告说明
用户基础统计：每个用户的首购/末购日期、订单数、总金额、客单价

RFM 分层结果：R/F/M 得分、总分、用户分层（高/中/低价值）

商品类别偏好：每个用户消费金额最高的品类及该品类总消费额

月复购率：当月购买用户在下个月再次购买的比例（按月）

用户留存透视表：按首购月份分组的 1~6 个月留存率

流失用户特征汇总：流失用户数量、流失率、平均订单/金额、偏好品类

### 参数配置
所有可调参数集中在 src/config.py 中：

ANALYSIS_END_DATE：分析截止日期（用于 R 指标和流失判定）

LOST_DAYS_THRESHOLD：流失阈值（末购超过此天数即流失）

MAX_RETENTION_MONTHS：留存曲线展示的最大月数

REPURCHASE_HIST_BINS：复购周期直方图 bins 数量

FLOAT_DECIMALS：Excel 数字小数位数

### 扩展与定制
新增指标：在对应模块（如 metrics.py）中添加函数，并在主 Notebook 中调用。

修改 RFM 分箱方式：将 pd.qcut 改为自定义分箱。

自动化运行：可编写 run.py 脚本，导入模块并执行，配合定时任务（cron/任务计划）实现定期报表生成。

### 注意事项
原始数据文件名必须与代码中一致（或修改 config.py 中的 ORDERS_FILE）。

数据清洗严格遵循 notebook 规则：删除 amount 缺失或 ≤0、payment_method 填充“未知”、删除日期范围外的记录、删除重复订单。

复购周期分析仅针对至少购买 2 次的用户。

留存曲线以用户首次购买月份作为“注册”月份（无独立注册时间列）。

### 许可证
本项目仅供学习与交流使用。
