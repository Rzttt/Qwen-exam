import os
from PIL import Image
import os

# 获取脚本所在目录
project_root = os.path.dirname(os.path.abspath(__file__))

def images_to_pdf_with_cleanup(folder_path, output_pdf):
    """
    将文件夹内的所有图片合并为一个PDF，并删除原始图片。

    :param folder_path: 包含图片的文件夹路径
    :param output_pdf: 输出的PDF文件路径
    """
    # 1. 获取文件夹内所有图片文件的路径，并按文件名排序
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]

    # 按文件名排序，确保拼接顺序正确
    image_files.sort()

    if not image_files:
        print("❌ 在指定文件夹中未找到任何图片。")
        return

    full_image_paths = [os.path.join(folder_path, file) for file in image_files]
    images = []

    print(f"📄 正在处理 {len(full_image_paths)} 张图片...")

    # 2. 打开所有图片并转换为RGB模式 (PDF不支持某些格式如RGBA)
    try:
        for path in full_image_paths:
            img = Image.open(path).convert('RGB')
            images.append(img)
    except Exception as e:
        print(f"❌ 读取图片时出错: {e}")
        return

    # 3. 将所有图片保存为一个PDF文件
    try:
        # 保存第一张图片，并将后续图片作为附加页面
        images[0].save(
            output_pdf,
            "PDF",
            save_all=True,
            append_images=images[1:]
        )
        print(f"✅ PDF创建成功: {output_pdf}")
    except Exception as e:
        print(f"❌ 创建PDF时出错: {e}")
        return

    # 4. PDF创建成功后，删除原始图片文件
    print("🗑️  正在删除原始图片...")
    for path in full_image_paths:
        try:
            os.remove(path)
            print(f"   已删除: {path}")
        except Exception as e:
            print(f"   删除失败 {path}: {e}")

    print("🎉 全部完成！")


