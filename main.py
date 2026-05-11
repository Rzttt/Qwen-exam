import re

from data_reader import process_exam_data_for_display,display_exam_arrangement
from student_print import json_to_excel_final
from draw import create_exam_hall_background,main
from image_to_pdf import images_to_pdf_with_cleanup
import os

# 获取脚本所在目录
project_root = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":


    # 创建单层文件夹
    folder_path = "./temp"
    os.makedirs(folder_path, exist_ok=True)

    # 创建多层文件夹
    nested_path = "./temp/image"
    os.makedirs(nested_path, exist_ok=True)
    # 使用您上传的Excel文件路径
    file_path = "考试信息填写.xlsx"

    try:
        # 处理数据
        result = process_exam_data_for_display(file_path)

        if result is not None:
            # 显示考试安排信息
            # display_exam_arrangement(result)

            # 也可以单独访问某个考场的信息
            # print(f"\n第一个考场信息示例:")
            # if result['rooms']:
            #     first_room = result['rooms'][0]
            #     print(f"考场: {first_room['room_id']}")
            #     print(f"地点: {first_room['location']}")
            #     print(f"学生人数: {first_room['occupied_seats']}/{first_room['total_seats']}")
            #     print(f"列数: {first_room['columns']}")
            #     print(f"选科分布: {first_room['subjects']}")

            # 可选：保存为JSON格式
            import json


            def convert_numpy_types(obj):
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, list):
                    return [convert_numpy_types(item) for item in obj]
                elif isinstance(obj, dict):
                    return {key: convert_numpy_types(value) for key, value in obj.items()}
                else:
                    return obj


            result_converted = convert_numpy_types(result)
            with open('exam_arrangement.json', 'w', encoding='utf-8') as f:
                json.dump(result_converted, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: exam_arrangement.json")

        else:
            print("数据处理失败")

    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        print("请确保文件路径正确")
    except KeyError as e:
        print(f"错误：找不到列 {e}")
        print("请检查Excel文件中的列名是否与代码中的一致")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        import traceback

        traceback.print_exc()
    filename = main()
    print("文件为",filename)
    my_image_folder = "temp/image"
    # 输出的PDF文件名
    my_output_pdf = f"{filename}.pdf"
    #
    images_to_pdf_with_cleanup(my_image_folder, my_output_pdf)
    input_json = "exam_arrangement.json"
    output_xlsx = f"{filename}.xlsx"

    json_to_excel_final(input_json, output_xlsx)