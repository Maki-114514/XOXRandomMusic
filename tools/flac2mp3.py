import os
import argparse
import logging
import shutil
from pathlib import Path
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def setup_logging():
    """配置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("flac_to_mp3.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def convert_flac_to_mp3(flac_path, mp3_path, bitrate="320k", dry_run=False, delete_original=False):
    """
    将单个FLAC文件转换为MP3格式

    参数:
    flac_path (str): FLAC文件路径
    mp3_path (str): 输出MP3文件路径
    bitrate (str): MP3比特率，例如 "320k", "192k"
    dry_run (bool): 是否执行干运行（只显示操作不实际转换）
    delete_original (bool): 是否删除原始FLAC文件
    """
    try:
        if dry_run:
            logging.info(f"[干运行] 将 '{flac_path}' 转换为 '{mp3_path}' (比特率: {bitrate})")
            return True

        # 检查目标目录是否存在
        os.makedirs(os.path.dirname(mp3_path), exist_ok=True)

        # 加载FLAC文件
        audio = AudioSegment.from_file(flac_path, format="flac")

        # 导出为MP3格式
        audio.export(mp3_path, format="mp3", bitrate=bitrate)

        # 验证输出文件大小
        flac_size = os.path.getsize(flac_path)
        mp3_size = os.path.getsize(mp3_path)
        space_saved = flac_size - mp3_size
        savings_percent = (1 - mp3_size / flac_size) * 100

        logging.info(f"成功转换: '{flac_path}' -> '{mp3_path}'")
        logging.info(f"空间优化: 节省 {space_saved / 1024 / 1024:.2f} MB ({savings_percent:.1f}%)")

        # 删除原始文件
        if delete_original:
            if dry_run:
                logging.info(f"[干运行] 删除原始文件: {flac_path}")
            else:
                os.remove(flac_path)
                logging.info(f"已删除原始文件: {flac_path}")

        return True
    except Exception as e:
        logging.error(f"转换失败: {flac_path}, 错误: {e}")
        return False


def batch_convert_flac_to_mp3(target_dir, output_dir=None, bitrate="320k",
                              recursive=False, dry_run=False, delete_original=False,
                              threads=4):
    """
    批量将目标目录下的所有FLAC文件转换为MP3格式

    参数:
    target_dir (str): 目标目录路径
    output_dir (str, optional): 输出目录路径，默认为None表示替换原文件
    bitrate (str): MP3比特率
    recursive (bool): 是否递归处理子目录
    dry_run (bool): 是否执行干运行
    delete_original (bool): 是否删除原始FLAC文件
    threads (int): 并发线程数
    """
    # 验证目标目录是否存在
    if not os.path.exists(target_dir):
        logging.error(f"目标目录不存在: {target_dir}")
        return

    # 构建FLAC文件列表
    flac_files = []
    for root, dirs, files in os.walk(target_dir):
        # 如果不递归处理，只处理根目录
        if not recursive and root != target_dir:
            continue

        for filename in files:
            if filename.lower().endswith('.flac'):
                flac_path = os.path.join(root, filename)

                # 确定输出路径
                if output_dir:
                    # 使用指定的输出目录
                    rel_path = os.path.relpath(root, target_dir)
                    mp3_subdir = os.path.join(output_dir, rel_path)
                    os.makedirs(mp3_subdir, exist_ok=True)
                    mp3_filename = os.path.splitext(filename)[0] + ".mp3"
                    mp3_path = os.path.join(mp3_subdir, mp3_filename)
                else:
                    # 替换原文件（在同一目录下生成MP3）
                    mp3_path = os.path.splitext(flac_path)[0] + ".mp3"

                flac_files.append((flac_path, mp3_path))

        # 如果不递归，跳过子目录
        if not recursive:
            break

    if not flac_files:
        logging.info("未找到FLAC文件")
        return

    # 显示统计信息
    total_flac_size = sum(os.path.getsize(f[0]) for f in flac_files)
    estimated_mp3_size = total_flac_size * (int(bitrate[:-1]) / 8) / 1411  # 粗略估计
    estimated_savings = total_flac_size - estimated_mp3_size

    logging.info(f"找到 {len(flac_files)} 个FLAC文件，总大小: {total_flac_size / 1024 / 1024:.2f} MB")
    logging.info(f"估计转换后MP3大小: {estimated_mp3_size / 1024 / 1024:.2f} MB")
    logging.info(
        f"估计节省空间: {estimated_savings / 1024 / 1024:.2f} MB ({estimated_savings / total_flac_size * 100:.1f}%)")

    # 使用线程池并行处理
    success_count = 0
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(tqdm(
            executor.map(lambda f: convert_flac_to_mp3(
                f[0], f[1], bitrate, dry_run, delete_original
            ), flac_files),
            total=len(flac_files),
            desc="转换进度"
        ))
        success_count = sum(results)

    logging.info(f"处理完成！总FLAC文件数: {len(flac_files)}, 成功转换: {success_count}")

    # 清理空目录（如果删除了原始文件）
    if delete_original and not dry_run:
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    if not os.listdir(dir_path):  # 目录为空
                        os.rmdir(dir_path)
                        logging.info(f"删除空目录: {dir_path}")
                except Exception as e:
                    logging.warning(f"无法删除目录 {dir_path}: {e}")


if __name__ == "__main__":
    setup_logging()

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="批量将FLAC文件转换为MP3格式，优化空间利用率")
    parser.add_argument("target_dir", help="目标文件夹路径")
    parser.add_argument("-o", "--output_dir", help="输出文件夹路径，默认为替换原文件")
    parser.add_argument("-b", "--bitrate", default="320k", help="MP3比特率，例如 '320k', '192k' (默认: 320k)")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子文件夹")
    parser.add_argument("-d", "--delete", action="store_true", help="转换后删除原始FLAC文件")
    parser.add_argument("--dry-run", action="store_true", help="执行干运行，只显示操作不实际转换")
    parser.add_argument("-t", "--threads", type=int, default=4, help="并发线程数 (默认: 4)")

    args = parser.parse_args()

    # 规范化目录路径
    target_dir = os.path.abspath(args.target_dir)
    output_dir = os.path.abspath(args.output_dir) if args.output_dir else None

    logging.info(f"开始处理目录: {target_dir}")
    logging.info(f"输出目录: {output_dir if output_dir else '替换原文件'}")
    logging.info(f"MP3比特率: {args.bitrate}")
    logging.info(f"递归模式: {args.recursive}")
    logging.info(f"删除原始文件: {args.delete}")
    logging.info(f"干运行模式: {args.dry_run}")
    logging.info(f"并发线程数: {args.threads}")

    batch_convert_flac_to_mp3(
        target_dir, output_dir, args.bitrate,
        args.recursive, args.dry_run, args.delete,
        args.threads
    )