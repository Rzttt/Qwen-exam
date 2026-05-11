import pandas as pd
import numpy as np
from collections import defaultdict
import os

# 获取脚本所在目录
project_root = os.path.dirname(os.path.abspath(__file__))

def process_exam_data_for_display(file_path, use_file_exam_name=True):
    """
    处理考试数据并返回适合生成考场分布图的数据结构

    Args:
        file_path: Excel文件路径
        use_file_exam_name: 是否使用文件中的考试名称

    Returns:
        dict: 包含考试名称、考试信息、考场信息和学生信息的嵌套字典
    """

    # 1. 读取考试信息
    print("正在读取考试信息...")
    exam_info_df = pd.read_excel(file_path, sheet_name="考试信息")

    # 提取考试信息
    exam_name = exam_info_df.iloc[0]['考试名称'] if use_file_exam_name else "高三第一次月考"
    exam_grade = exam_info_df.iloc[0]['考试年级（填写高一或高二或高三）']
    exam_class_count = exam_info_df.iloc[0]['考试班级数']
    is_gaokao_str = exam_info_df.iloc[0]['是否高考']
    is_gaokao = is_gaokao_str == '是'
    exam_rooms_df = pd.read_excel(file_path, sheet_name="考场信息")
    # 读取阶梯教室列数
    step_classroom_columns = exam_rooms_df.iloc[0]['阶梯教室列数（6或者8）']

    # 2. 读取上次考试学生信息
    print("正在读取上次考试学生信息...")
    last_exam_df = pd.read_excel(file_path, sheet_name="上次参加考试学生信息")

    # 根据实际Excel文件中的列名提取数据
    last_exam_df = last_exam_df[['班级(1-17)', '姓名', '校排名', '选科']].copy()

    # 3. 处理上次考试数据（去重与排序）
    # 基于"班级(1-17)"和"姓名"进行去重，保留最优排名（数值最小的）
    last_exam_df = last_exam_df.sort_values(['班级(1-17)', '姓名', '校排名']).drop_duplicates(
        subset=['班级(1-17)', '姓名'], keep='first')

    # 定义选科优先级映射
    subject_priority = {
        '物化生': 0,
        '物化地': 1,
        '物化政': 2,
        '政史地': 3
    }

    # 添加选科优先级列以便排序
    last_exam_df['选科优先级'] = last_exam_df['选科'].map(subject_priority)

    # 按选科优先级和校排名排序
    last_exam_df = last_exam_df.sort_values(['选科优先级', '校排名']).reset_index(drop=True)

    # 4. 读取本次考试学生信息
    print("正在读取本次考试学生信息...")
    current_exam_df = pd.read_excel(file_path, sheet_name="本次参加考试学生信息")

    # 根据实际数据推测，本次考试学生信息应该包含班级、姓名、选科、考号
    # 检查实际列名
    print(f"本次参加考试学生信息工作表的列名: {list(current_exam_df.columns)}")

    # 根据通常的数据结构，假设列名是班级(1-17), 姓名, 选科, 考号
    # 如果实际列名不同，请相应调整
    column_mapping = {}
    available_cols = list(current_exam_df.columns)

    # 查找对应的列
    for col in available_cols:
        if '班级' in str(col):
            column_mapping[col] = '班级(1-17)'
        elif '姓名' in str(col):
            column_mapping[col] = '姓名'
        elif '选科' in str(col):
            column_mapping[col] = '选科'
        elif '考号' in str(col):
            column_mapping[col] = '考号'

    # 如果找到了所有必需的列，就进行重命名
    required_cols = ['班级(1-17)', '姓名', '选科', '考号']
    found_cols = []
    for orig_col, new_col in column_mapping.items():
        if new_col in required_cols:
            found_cols.append(new_col)

    if set(required_cols).issubset(set(found_cols)):
        # 重命名列
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        selected_cols = [reverse_mapping[col] for col in required_cols]
        current_exam_df = current_exam_df[selected_cols].copy()
        current_exam_df.columns = required_cols
    else:
        print("警告：未能找到所有必需的列，正在使用前4列并手动重命名")
        # 假设前4列分别是班级、姓名、选科、考号
        if len(current_exam_df.columns) >= 4:
            current_exam_df = current_exam_df.iloc[:, :4].copy()
            current_exam_df.columns = ['班级(1-17)', '姓名', '选科', '考号']
        else:
            print(f"错误：本次参加考试学生信息表只有{len(current_exam_df.columns)}列")
            return None

    # 5. 合并排名信息
    # 为当前学生添加排名列，默认值为1000
    current_exam_df['校排名'] = 1000

    # 使用merge函数合并排名信息
    merged_df = current_exam_df.merge(
        last_exam_df[['班级(1-17)', '姓名', '校排名']],
        on=['班级(1-17)', '姓名'],
        how='left',
        suffixes=('', '_from_last')
    )

    # 更新校排名：如果从上次考试找到了排名，则使用该排名，否则保持默认值1000
    current_exam_df['校排名'] = merged_df['校排名_from_last'].fillna(1000).astype(int)

    # 6. 对本次考试学生进行最终排序（按选科优先级和校排名）
    # 添加选科优先级列
    current_exam_df['选科优先级'] = current_exam_df['选科'].map(subject_priority)

    # 按选科优先级和校排名排序
    current_exam_df = current_exam_df.sort_values(['选科优先级', '校排名']).reset_index(drop=True)

    # 7. 读取考场信息并分配考场及座位
    print("正在读取考场信息并分配考场...")
    exam_rooms_df = pd.read_excel(file_path, sheet_name="考场信息")

    # 使用考场信息中的数据来分配考场
    exam_rooms_list = exam_rooms_df['考场名称'].tolist()
    room_capacities = exam_rooms_df['限定人数'].tolist()
    room_numbers = exam_rooms_df['考场编号'].tolist()  # 假设考场编号是"01"这样的格式

    # 将考场编号转换为标准格式
    formatted_room_numbers = [f"第{num:03d}考场" if isinstance(num, (int, float)) else f"第{num}考场" for num in
                              room_numbers]

    # 为每个考场维护一个计数器
    room_student_counts = {room: 0 for room in exam_rooms_list}
    room_max_capacities = dict(zip(exam_rooms_list, room_capacities))
    room_numbers_map = dict(zip(exam_rooms_list, formatted_room_numbers))

    # 按照已排序的顺序（选科优先级和校排名）依次分配考场和座位号
    current_exam_df['考场'] = ''
    current_exam_df['座位号'] = 0

    for idx, row in current_exam_df.iterrows():
        # 寻找有空位的考场
        assigned = False
        for room_idx in range(len(exam_rooms_list)):
            room_name = exam_rooms_list[room_idx]
            if room_student_counts[room_name] < room_max_capacities[room_name]:
                # 分配到此考场
                current_exam_df.at[idx, '考场'] = room_name
                current_exam_df.at[idx, '座位号'] = room_student_counts[room_name] + 1
                room_student_counts[room_name] += 1
                assigned = True
                break

        # 如果没有找到空位，分配到第一个考场（理论上不应该发生，除非考场容量不够）
        if not assigned:
            current_exam_df.at[idx, '考场'] = exam_rooms_list[0]
            current_exam_df.at[idx, '座位号'] = room_student_counts[exam_rooms_list[0]] + 1
            room_student_counts[exam_rooms_list[0]] += 1

    # 8. 格式化班级名称（添加年级前缀）
    current_exam_df['班级'] = current_exam_df['班级(1-17)'].apply(lambda x: f"高三({x})班")

    # 9. 构建返回的嵌套字典结构
    result = {
        "exam_info": {
            "exam_name": exam_name,
            "grade": exam_grade,
            "class_count": exam_class_count,
            "is_gaokao": is_gaokao,
            "step_classroom_columns": int(step_classroom_columns) if pd.notna(step_classroom_columns) else 6  # 默认6列
        },
        "rooms": []
    }

    # 按考场分组构建数据
    grouped_by_room = current_exam_df.groupby('考场')

    for room_name, group in grouped_by_room:
        # 获取该考场的编号
        room_id = room_numbers_map.get(room_name,
                                       f"第{room_name}考场") if room_name in room_numbers_map else f"第{room_name}考场"

        # 确定考场列数
        room_type = room_name.lower()
        if is_gaokao:
            # 如果是高考，则所有考场均为4列
            columns = 4
        elif '阶梯' in room_type or '阶梯' in room_name:
            # 阶梯教室使用考试信息中指定的列数
            columns = int(step_classroom_columns) if pd.notna(step_classroom_columns) else 6
        elif '实验' in room_type or '实验' in room_name:
            # 实验室为4列
            columns = 4
        elif '小屋' in room_type or '小屋' in room_name:
            # 六楼小屋为3列
            columns = 3
        elif '西六楼' in room_type or '西六楼' in room_name:
            # 西六楼为5列
            columns = 5
        elif '高一' in room_name or '高二' in room_name or '高三' in room_name:
            # 高一、高二、高三考场为5列
            columns = 5
        else:
            # 默认为5列
            columns = 5

        # 获取该考场包含的选科
        subjects_in_room = sorted(list(group['选科'].unique()))

        # 构建学生列表
        students = []
        for _, student_row in group.iterrows():
            student_info = {
                "class": student_row['班级'],
                "name": student_row['姓名'],
                "subject": student_row['选科'],
                "rank": int(student_row['校排名']),
                "seat_number": int(student_row['座位号']),
                "exam_number": student_row['考号']  # 添加考号
            }
            students.append(student_info)

        # 按座位号排序学生
        students.sort(key=lambda x: x['seat_number'])

        # 构建考场信息
        room_info = {
            "room_id": room_id,
            "location": room_name,  # 考场名称即为地点
            "total_seats": room_max_capacities[room_name],
            "occupied_seats": len(students),
            "subjects": subjects_in_room,
            "columns": columns,  # 新增列数字段
            "students": students
        }

        result["rooms"].append(room_info)

    # 按照考场编号排序
    result["rooms"].sort(key=lambda x: x['room_id'])

    print(f"数据处理完成，共处理 {len(current_exam_df)} 名学生，分布在 {len(result['rooms'])} 个考场中")

    return result


def display_exam_arrangement(exam_data):
    """
    显示考试安排信息，用于调试
    """
    exam_info = exam_data['exam_info']
    print(f"\n考试名称: {exam_info['exam_name']}")
    print(f"考试年级: {exam_info['grade']}")
    print(f"考试班级数: {exam_info['class_count']}")
    print(f"是否高考: {'是' if exam_info['is_gaokao'] else '否'}")
    print(f"阶梯教室列数: {exam_info['step_classroom_columns']}")
    print(f"总考场数: {len(exam_data['rooms'])}")

    for room in exam_data['rooms']:
        print(f"\n--- {room['room_id']} ({room['location']}) ---")
        print(f"座位总数: {room['total_seats']}, 实到人数: {room['occupied_seats']}")
        print(f"列数: {room['columns']}")
        print(f"涉及选科: {', '.join(room['subjects'])}")
        print("学生名单:")
        for student in room['students']:
            print(
                f"  座位{student['seat_number']:2d}: {student['name']} ({student['class']}) - {student['subject']} (排名:{student['rank']})")


# 使用示例
