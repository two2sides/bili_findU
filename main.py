"""bili_dynamic_spy"""
import csv
import sys
import time
from src.crawler import DynamicCrawler

def load_uids(filepath="collected_uids.csv"):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return [row["UID"] for row in reader]
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return []

def run_single(uid):
    print(f"分析单个UID: {uid}")
    crawler = DynamicCrawler()
    count, saved = crawler.run(uid)
    print(f"\n完成! 动态数: {count}, {'已保存' if saved else '未保存(动态数不足)'}")

def main(start_index=0):
    uids = load_uids()
    if not uids:
        print("没有找到UID")
        return
    if start_index > 0:
        print(f"从第{start_index}个开始, 跳过前{start_index}个UID")
        uids = uids[start_index:]
    crawler = DynamicCrawler()
    start_time = time.time()
    total_count = 0
    saved_count = 0
    for i, uid in enumerate(uids):
        print(f"[{start_index + i + 1}/{start_index + len(uids)}] 处理UID: {uid}")
        count, saved = crawler.run(uid)
        total_count += count
        if saved:
            saved_count += 1
        time.sleep(crawler.config.request_interval)
    end_time = time.time()
    print(f"\n爬取完毕\n总耗时: {end_time - start_time:.2f}秒")
    print(f"处理UID: {len(uids)}个, 保存: {saved_count}个, 总动态: {total_count}条")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-u":
        if len(sys.argv) > 2:
            run_single(sys.argv[2])
        else:
            print("用法: python main.py -u <UID>")
    else:
        start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
        main(start)
