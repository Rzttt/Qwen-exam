import json
import re
import os
from PIL import Image, ImageDraw, ImageFont
from seat import assign_seats_no_same_class_adjacent
import os

# 获取脚本所在目录
project_root = os.path.dirname(os.path.abspath(__file__))


def create_exam_hall_background(columns, exam_name, exam_room_number, total_students=30, students_data=None,grade=None,exam_location=None):
    """
    创建考场背景图像并添加考试信息和学生座位（放大版）
    """
    # 计算宽度：取2560和列数*400+300中的最大值
    width = max(2560, columns * 400 + 300)
    height = 2000  # 固定高度为2000像素

    # 创建白色背景图像
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # 放大字体
    font_exam = ImageFont.truetype('ai.ttf', 72)  # 考试名称字体大小 - 增大50%
    font_room = ImageFont.truetype('ai.ttf', 60)  # 考场序号字体大小 - 增大50%
    font_lecture = ImageFont.truetype('ai.ttf', 48)  # 讲台文字字体大小 - 增大33%
    font_seat_name = ImageFont.truetype('ai.ttf', 36)  # 座位姓名字体 - 增大50%
    font_seat_id = ImageFont.truetype('ai.ttf', 32)  # 座位考号字体 - 增大60%
    font_foot = ImageFont.truetype('ai.ttf', 48)  # 讲台文字字体大小 - 增大33%
    # 第一行：考试名称（放大）
    exam_text = exam_name
    exam_bbox = draw.textbbox((0, 0), exam_text, font=font_exam)
    exam_width = exam_bbox[2] - exam_bbox[0]
    exam_x = (width - exam_width) // 2
    exam_y = 80  # 距离顶部80像素（增大间距）

    # 第二行：考场序号（放大）
    room_text = exam_room_number
    room_bbox = draw.textbbox((0, 0), room_text, font=font_room)
    room_width = room_bbox[2] - room_bbox[0]
    room_x = (width - room_width) // 2
    room_y = exam_y + 120  # 距离考试名称120像素（增大间距）

    # 绘制考试名称和考场序号
    draw.text((exam_x, exam_y), exam_text, fill='red', font=font_exam)
    draw.text((room_x, room_y), room_text, fill='blue', font=font_room)

    # 第三部分：讲台矩形（放大）
    lecture_y = room_y + 120  # 增大间距

    # 矩形尺寸（大幅放大）
    lecture_width = 600  # 从400增大到600
    lecture_height = 120  # 从80增大到120

    # 矩形居中位置
    lecture_x = (width - lecture_width) // 2

    # 绘制矩形边框（加粗）
    draw.rectangle(
        [(lecture_x, lecture_y), (lecture_x + lecture_width, lecture_y + lecture_height)],
        outline='black',
        width=3  # 边框加粗
    )

    # 讲台文字（放大）
    lecture_text = "讲台"
    lecture_bbox = draw.textbbox((0, 0), lecture_text, font=font_lecture)
    lecture_text_width = lecture_bbox[2] - lecture_bbox[0]
    lecture_text_height = lecture_bbox[3] - lecture_bbox[1]

    # 文字在矩形内居中
    lecture_text_x = lecture_x + (lecture_width - lecture_text_width) // 2
    lecture_text_y = lecture_y + (lecture_height - lecture_text_height) // 2

    # 绘制讲台文字
    draw.text((lecture_text_x, lecture_text_y), lecture_text, fill='black', font=font_lecture)

    # 第四部分：学生座位（大幅放大）
    # 生成默认学生数据
    if students_data is None:
        students_data = []
        for i in range(total_students):
            students_data.append({
                'name': f'学生{i + 1:02d}',
                'class': f'{(i % 12) + 1:02d}',
                'exam_id': f'625301{(i + 1):04d}'
            })
    print(len(students_data))
    seat_distribution, arranged_students = assign_seats_no_same_class_adjacent(columns, total_students, students_data)
    print(f"座位分布: {seat_distribution}")
    for i in arranged_students:
        print(i)
    print(len(arranged_students))
    # 座位区域起始位置（讲台下方150像素，增大间距）
    seats_start_y = lecture_y + lecture_height + 150

    # 每个座位的尺寸（大幅放大）
    seat_width = 300  # 从180增大到300
    seat_height = 120  # 从80增大到120
    seat_padding = 40  # 从20增大到40（间距加倍）

    # 计算每列的起始x坐标
    total_seats_width = columns * seat_width + (columns - 1) * seat_padding
    start_x = (width - total_seats_width) // 2



    students_data = students_data[:total_students]
    footer_y = 0
    # 绘制座位
    current_student_index = 0
    getnum=1
    for col in range(columns):
        col_students = seat_distribution[col]
        col_x = start_x + col * (seat_width + seat_padding)

        for row in range(col_students):
            if current_student_index >= len(arranged_students):
                break

            student = arranged_students[current_student_index]
            seat_y = seats_start_y + row * (seat_height + seat_padding)

            # 绘制座位矩形（加粗边框）
            draw.rectangle(
                [(col_x, seat_y-100), (col_x + seat_width, seat_y + seat_height-100)],
                outline='black',
                width=2  # 边框加粗
            )

            # 绘制学生信息
            name_text = f"{student['name']}({student['class']})"
            id_text = student['exam_id']

            # 姓名文字（第一行，放大）
            name_bbox = draw.textbbox((0, 0), name_text, font=font_seat_name)
            name_width = name_bbox[2] - name_bbox[0]
            name_x = col_x + (seat_width - name_width) // 2
            name_y = seat_y + 25  # 顶部间距

            # 考号文字（第二行，放大）
            id_bbox = draw.textbbox((0, 0), id_text, font=font_seat_id)
            id_width = id_bbox[2] - id_bbox[0]
            id_x = col_x + (seat_width - id_width) // 2
            id_y = seat_y + 65

            draw.text((name_x, name_y-100), name_text, fill='black', font=font_seat_name)
            draw.text((id_x, id_y-100), id_text, fill='black', font=font_seat_id)
            footer_y=max(footer_y,id_y-100)
            current_student_index += 1
            # print(current_student_index)

    # footer_info = [
    #     f"考场地点：{exam_location}",
    #     f"考试年级：{exam_grade}",
    #     f"考场人数：{total_students}人"
    # ]
    print(footer_y)
    footer = f"考场地点： {exam_location} 年级：{grade}   人数：{total_students}人"
    exam_footer = footer
    exam_footer_bbox = draw.textbbox((0, 0), footer, font=font_foot)
    exam_width = exam_footer_bbox[2] - exam_footer_bbox[0]
    footer_x = (width - exam_width) // 2
    # footer_y = 80  # 距离顶部80像素（增大间距）
    draw.text((footer_x, footer_y+80), exam_footer, fill='red', font=font_foot)
    # self._draw_center_text(draw, footer, width, max_y, self.f_body, "red")

    print(f"创建图像尺寸: {width}x{height} 像素")
    print(f"考场列数: {columns}")
    print(f"总学生人数: {total_students}")
    print(f"座位分布: {seat_distribution}")

    return img

def main():
    # 1. 读取 JSON 文件
    # 注意：请确保 exam_arrangement.json 在当前工作目录，或者填写完整路径
    try:
        with open('exam_arrangement.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("错误：draw找不到 exam_arrangement.json 文件，请检查文件路径。")
        return
    except json.JSONDecodeError as e:
        print(f"错误：JSON 文件格式不正确。{e}")
        return

    # 2. 提取全局考试信息
    exam_info = data.get("exam_info", {})
    global_exam_name = exam_info.get("exam_name", "未知考试")

    # 3. 遍历考场列表 (rooms)
    rooms = data.get("rooms", [])


    print(f"开始处理 {len(rooms)} 个考场...")
    index=1
    for room in rooms:
        grade = exam_info.get("grade", "未知年级")
        exam_location=room.get("location", "")
        # 提取单个考场的参数
        sub = room.get("subjects", [])
        grade = str(grade) + str(sub[0])
        exam_room_number = room.get("room_id", "未知考场")
        total_students = room.get("total_seats", 0)
        columns = room.get("columns", 4)  # 默认4列

        # 整理学生数据列表
        students_data = []
        for student in room.get("students", []):
            class_match = re.search(r'(\d+)', student.get('class', ''))
            class_num = class_match.group(1) if class_match else '未知'
            students_data.append({
                'name': student.get('name', '匿名'),
                'class': class_num,
                'exam_id': str(student.get('exam_number', '0')),  # 确保是字符串
                # 如果需要更多字段可以在这里添加
                'seat_number': student.get('seat_number')
            })
        print(exam_room_number)
        print(len(students_data))
        image = create_exam_hall_background(columns=columns,exam_name=global_exam_name,exam_room_number=exam_room_number,
            total_students=total_students,
            students_data=students_data,grade=grade,exam_location=exam_location)
        image.save('temp/image/'+str(index)+'.jpg')
        index=index+1
        # 4. 调用绘制函数
        # 这里会传入从 JSON 读取的真实数据
    return global_exam_name

# # 示例使用
# if __name__ == "__main__":
#
#     main()
