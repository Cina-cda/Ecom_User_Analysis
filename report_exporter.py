# src/report_exporter.py
"""Excel 报告导出模块：严格按照 notebook 最后一个单元格的代码实现"""

import pandas as pd
from datetime import datetime
from src.config import OUTPUT_DIR, EXCEL_FILE_PREFIX, FLOAT_DECIMALS, MAX_COL_WIDTH, EXCEL_INCLUDE_INDEX


def export_user_lifecycle_report(sheets_dict: dict, filename: str = None) -> None:
    """
    将多个 DataFrame 写入 Excel 的不同 Sheet，并自动调整格式。
    完全复现 notebook 中的函数定义及内部逻辑。

    参数：
        sheets_dict: dict, 键为 sheet 名称，值为 DataFrame。
        filename: str, 输出文件名（可选，默认为 user_lifecycle_YYYYMMDD.xlsx）。
    """
    if filename is None:
        filename = f"{EXCEL_FILE_PREFIX}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename

    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({'bold': True, 'text_wrap': True})
        float_format = workbook.add_format({'num_format': f'0.{FLOAT_DECIMALS}'})

        for sheet_name, df in sheets_dict.items():
            if df is None or df.empty:
                print(f"警告：{sheet_name} 的 DataFrame 为空，跳过写入。")
                continue

            # 写入数据，不包含行索引（与 notebook 一致）
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0, startcol=0)
            worksheet = writer.sheets[sheet_name]

            # 设置标题行加粗
            worksheet.set_row(0, None, header_format)

            # 遍历每一列，设置列宽和数字格式
            for col_idx, col_name in enumerate(df.columns):
                # 计算列宽（列名长度与内容最大长度取较大值，加2边距，限制最大宽度30）
                max_len = max(
                    df[col_name].astype(str).map(len).max(),
                    len(str(col_name))
                ) + 2
                worksheet.set_column(col_idx, col_idx, min(max_len, MAX_COL_WIDTH))

                # 如果该列是数值类型，应用两位小数格式
                if pd.api.types.is_numeric_dtype(df[col_name]):
                    worksheet.set_column(col_idx, col_idx, None, float_format)

    print(f"用户生命周期报告已保存为: {filepath}")