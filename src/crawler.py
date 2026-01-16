"""爬虫主逻辑"""
import time
from .constants import BASE_URL
from .config import Config
from .http_client import BiliClient
from .parser import DynamicParser
from .storage import CsvStorage, save_raw_json
class DynamicCrawler:
    def __init__(self, config_path="config.json"):
        self.config = Config(config_path)
        self.client = BiliClient(self.config)
        self.parser = DynamicParser(self.client)
    def run(self, uid: str):
        self.parser.count = 0
        data = self.client.get_dynamics(BASE_URL, uid)
        if not data:
            print(f"  获取数据失败")
            return 0, False
        if data.get("code") != 0:
            print(f"  API返回错误: {data.get('code')} - {data.get('message')}")
            return 0, False
        username = self.parser.get_username(data)
        storage = CsvStorage(username, uid)
        self._process_page(data, storage, 0)
        has_more = data.get("data", {}).get("has_more", False)
        offset = data.get("data", {}).get("offset", "")
        if has_more:
            self._crawl_pages(storage, offset, uid)
        if storage.count < self.config.min_dynamics:
            print(f"  动态数({storage.count})少于{self.config.min_dynamics}, 放弃保存")
            return storage.count, False
        storage.save()
        return storage.count, True
    def _process_page(self, data, storage, index):
        datapage = self.parser.parse(data, skip_empty_forward=self.config.skip_empty_forward)
        storage.append(datapage)
        return datapage
    def _crawl_pages(self, storage, offset, uid):
        page = 0
        while True:
            if not self.config.crawl_all and page >= self.config.depth:
                break
            data = self.client.get_dynamics(BASE_URL, uid, offset)
            if not data:
                print("  获取数据失败")
                return
            self._process_page(data, storage, page + 1)
            has_more = data.get("data", {}).get("has_more", False)
            offset = data.get("data", {}).get("offset", "")
            if not has_more:
                break
            page += 1
            time.sleep(self.config.request_interval)
