import os
import argparse
import logging
from pathlib import Path


def setup_logging():
    """配置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("rename_operation.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def remove_first_three_chars(filename):
    """移除文件名的前三个字符，保留扩展名"""
    name_part, ext_part = os.path.splitext(filename)
    if len(name_part) <= 17:
        logging.warning(f"文件名 '{filename}' 长度不足，跳过")
        return None
    return name_part[17:] + ext_part


def batch_rename_files(target_dir, recursive=False, dry_run=False):
    """
    批量重命名目标目录下的所有文件，移除文件名前三个字符

    参数:
    target_dir (str): 目标目录路径
    recursive (bool): 是否递归处理子目录
    dry_run (bool): 是否执行干运行（只显示操作不实际修改）
    """
    # 验证目标目录是否存在
    if not os.path.exists(target_dir):
        logging.error(f"目标目录不存在: {target_dir}")
        return

    # 遍历处理文件
    processed_count = 0
    renamed_count = 0

    for root, dirs, files in os.walk(target_dir):
        # 如果不递归处理，只处理根目录
        if not recursive and root != target_dir:
            continue

        for filename in files:
            original_path = os.path.join(root, filename)
            new_filename = remove_first_three_chars(filename)

            if new_filename is None:
                continue

            new_path = os.path.join(root, new_filename)

            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                logging.warning(f"新文件名已存在，跳过: {new_path}")
                continue

            # 执行重命名操作或仅显示日志
            if dry_run:
                logging.info(f"[干运行] 将 '{original_path}' 重命名为 '{new_path}'")
            else:
                try:
                    os.rename(original_path, new_path)
                    logging.info(f"已重命名: '{original_path}' -> '{new_path}'")
                    renamed_count += 1
                except Exception as e:
                    logging.error(f"重命名失败: {original_path} -> {new_path}, 错误: {e}")

            processed_count += 1

        # 如果不递归，跳过子目录
        if not recursive:
            break

    logging.info(f"处理完成！总文件数: {processed_count}, 成功重命名: {renamed_count}")


if __name__ == "__main__":
    setup_logging()

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="批量移除文件名的前三个字符")
    parser.add_argument("target_dir", help="目标文件夹路径")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子文件夹")
    parser.add_argument("-d", "--dry-run", action="store_true", help="执行干运行，只显示操作不实际修改")

    args = parser.parse_args()

    # 规范化目录路径
    target_dir = os.path.abspath(args.target_dir)

    logging.info(f"开始处理目录: {target_dir}")
    logging.info(f"递归模式: {args.recursive}")
    logging.info(f"干运行模式: {args.dry_run}")

    batch_rename_files(target_dir, args.recursive, args.dry_run)