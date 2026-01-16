"""查看动态详情"""
import sys
import json
import webbrowser
from src.config import Config
from src.http_client import BiliClient

def main():
    if len(sys.argv) < 2:
        print("用法: python view_dynamic.py <动态ID> [--json]")
        print("例如: python view_dynamic.py 693542870792011784")
        print("      python view_dynamic.py 693542870792011784 --json")
        return
    
    dynamic_id = sys.argv[1]
    show_json = "--json" in sys.argv
    
    url = f"https://t.bilibili.com/{dynamic_id}"
    print(f"动态链接: {url}")
    
    if show_json:
        config = Config()
        client = BiliClient(config)
        data = client.get_detail(dynamic_id)
        if data:
            print("\n动态JSON:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("获取动态详情失败")
    else:
        print("正在打开浏览器...")
        webbrowser.open(url)

if __name__ == "__main__":
    main()
