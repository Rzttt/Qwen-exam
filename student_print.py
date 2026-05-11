import json
import pandas as pd
import os

def json_to_excel_final(json_file_path, output_excel_path):
    # 1. 读取 JSON 文件
    if not os.path.exists(json_file_path):
        print(f"错误：找不到文件 {json_file_path}")
        return

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. 提取所有学生数据
    all_students = []
    
    for room in data['rooms']:
        room_id = room['location']
        for student in room['students']:
            student_record = {
                'class': student['class'],
                'name': student['name'],
                'subject': student['subject'],
                'exam_number': str(student['exam_number']), # 确保考号是字符串
                'room_id': room_id,                         # 新增：考场信息
                'seat_number': student['seat_number']
            }
            all_students.append(student_record)
    
    # 创建主 DataFrame
    df = pd.DataFrame(all_students)
    
    # 辅助：提取班级数字用于排序 (例如从 "高三(1)班" 提取 1)
    # 如果班级格式不统一，可能需要调整正则表达式
    df['class_sort_num'] = df['class'].str.extract(r'(\d+)').astype(int)

    # --- 准备中文列名映射 (已添加 '考场') ---
    column_mapping = {
        'class': '班级',
        'name': '姓名',
        'subject': '选科',
        'exam_number': '考号',
        'room_id': '考场'  # 新增列
    }

    # 3. 开始写入 Excel
    try:
        with pd.ExcelWriter(output_excel_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # === 任务 A：生成总表 (按考场和姓名排序) ===
            df_total = df.copy()
            df_total = df_total.loc[df_total.index.repeat(1)].reset_index(drop=True)
            # 排序：先按考场ID，再按姓名
            df_total = df_total.sort_values(by=['room_id', 'name']).reset_index(drop=True)
            
            # 选择需要的列并重命名
            df_total_cn = df_total[list(column_mapping.keys())].rename(columns=column_mapping)
            
            # 写入总表
            sheet_name_total = '考场总表'
            df_total_cn.to_excel(writer, sheet_name=sheet_name_total, index=False)
            
            # 格式化总表：设置"考号"列为文本格式
            _set_column_text_format(worksheet=writer.sheets[sheet_name_total], 
                                    workbook=workbook, 
                                    col_name='考号', 
                                    df=df_total_cn)

            # === 任务 B：按班级拆分工作簿 ===
            # 获取所有唯一的班级，并按班级数字排序 (保证 1班, 2班... 15班 的顺序)
            unique_classes = df.sort_values('class_sort_num')['class'].unique()
            
            for class_name in unique_classes:
                # 筛选当前班级的数据
                df_class = df[df['class'] == class_name].copy()
                
                # 每个学生重复6次 (用于答题卡或标签打印)
                df_class = df_class.loc[df_class.index.repeat(1)].reset_index(drop=True)
                
                # 重命名列
                df_class_cn = df_class[list(column_mapping.keys())].rename(columns=column_mapping)
                
                # 写入对应的 Sheet，Sheet 名即为班级名（Excel限制Sheet名最长31字符）
                safe_sheet_name = class_name[:31] 
                df_class_cn.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                
                # 格式化分表：设置"考号"列为文本格式
                _set_column_text_format(worksheet=writer.sheets[safe_sheet_name], 
                                        workbook=workbook, 
                                        col_name='考号', 
                                        df=df_class_cn)

        print(f"✅ 成功！文件已生成：{output_excel_path}")
        print(f"   - 包含 1 个总表和 {len(unique_classes)} 个班级分表。")
        
    except PermissionError:
        print(f"❌ 错误：无法保存文件。请确保 '{output_excel_path}' 没有被其他程序（如 Excel）打开。")

def _set_column_text_format(worksheet, workbook, col_name, df):
    """辅助函数：将指定列设置为文本格式，防止科学计数法"""
    try:
        col_idx = df.columns.get_loc(col_name)
        # 定义文本格式 ('@' 代表文本)
        text_format = workbook.add_format({'num_format': '@'})
        # 设置整列为文本格式
        worksheet.set_column(col_idx, col_idx, None, text_format)
    except KeyError:
        pass

