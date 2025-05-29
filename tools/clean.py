import os
import sys


def remove_book_titles(input_file, output_file=None):
    """
    去除txt文件中的所有书名号（《》）

    参数:
    input_file (str): 输入txt文件路径
    output_file (str, optional): 输出txt文件路径，默认为在原文件名后加"_cleaned"

    返回:
    str: 处理后的文件路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在: {input_file}")

    # 如果没有指定输出文件，自动生成输出文件名
    if output_file is None:
        base_name, ext = os.path.splitext(input_file)
        output_file = f"{base_name}_cleaned{ext}"

    try:
        # 读取文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 去除书名号
        cleaned_content = content.replace('《', '').replace('》', '')

        # 写入处理后的内容到新文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        return output_file

    except Exception as e:
        print(f"处理文件时出错: {e}")
        return None


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python remove_book_titles.py <输入文件> [输出文件]")
        sys.exit(1)

    input_file = sys.argv[1]

    # 如果提供了第二个参数，则作为输出文件
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # 执行去除书名号操作
    result = remove_book_titles(input_file, output_file)

    if result:
        print(f"处理完成! 已保存到: {result}")
    else:
        print("处理失败!")