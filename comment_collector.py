"""评论区UID收集器"""
import csv
import time
import requests
from src.config import Config
COMMENT_API = "https://api.bilibili.com/x/v2/reply"
def bv_to_av(bv: str) -> int:
    """通过API获取AV号"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        resp = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bv}", headers=headers, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("aid")
    except:
        pass
    return None
class CommentCollector:
    def __init__(self, config_path="config.json"):
        self.config = Config(config_path)
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        self._proxies = {"http": None, "https": None}
        self.collected = {}
    @property
    def max_fans(self): return self.config._config.get("max_fans", 1000)
    @property
    def min_level(self): return self.config._config.get("min_level", 4)
    @property
    def sex_filter(self): return self.config._config.get("sex_filter", ["女", "保密"])
    @property
    def crawl_all_comments(self): return self.config._config.get("crawl_all_comments", False)
    @property
    def comment_pages(self): return self.config._config.get("comment_pages", 5)
    @property
    def comments_per_page(self): return self.config._config.get("comments_per_page", 20)
    @property
    def comment_sorts(self): return self.config._config.get("comment_sorts", [1])
    @property
    def request_interval(self): return self.config._config.get("request_interval", 0.5)
    def _build_cookies(self):
        return self.config.cookies
    def _fetch_comments(self, oid: int, pn: int = 1, sort: int = 1):
        params = {
            'type': 1,
            'oid': oid,
            'sort': sort,
            'ps': self.comments_per_page,
            'pn': pn,
            'nohot': 1
        }
        try:
            resp = requests.get(COMMENT_API, params=params, cookies=self._build_cookies(),
                                headers=self._headers, timeout=15, proxies=self._proxies)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == -352:
                    print(f"  风控触发(-352), 等待5秒后重试...")
                    import time
                    time.sleep(5)
                    return self._fetch_comments(oid, pn)
                return data
            else:
                print(f"  HTTP {resp.status_code}")
        except requests.RequestException as e:
            print(f"请求失败: {e}")
        return None
    def _filter_reply(self, reply: dict) -> tuple:
        member = reply.get("member", {})
        sex = member.get("sex", "")
        level = member.get("level_info", {}).get("current_level", 0)
        if sex in self.sex_filter and level >= self.min_level:
            return True, sex, level
        return False, sex, level
    def _get_fans_count(self, mid: int) -> int:
        try:
            resp = requests.get(f"https://api.bilibili.com/x/web-interface/card?mid={mid}",
                                headers=self._headers, timeout=8, proxies=self._proxies)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    return data.get("data", {}).get("card", {}).get("fans", 999999)
        except:
            pass
        return 999999
    def collect_from_video(self, bv: str, skip_count: int = 0):
        av = bv_to_av(bv)
        if not av:
            print(f"无法获取AV号: {bv}")
            return 0
        print(f"处理视频: {bv} -> av{av}")
        total_count = 0
        for sort in self.comment_sorts:
            sort_name = "按点赞" if sort == 1 else "按时间" if sort == 0 else f"排序{sort}"
            print(f"  [{sort_name}]")
            pn = 1
            while True:
                if not self.crawl_all_comments and pn > self.comment_pages:
                    break
                data = self._fetch_comments(av, pn=pn, sort=sort)
                if not data or data.get("code") != 0:
                    msg = data.get("message") if data else "No response"
                    if "offset" in msg.lower():
                        print(f"    已到达末尾 (本轮{pn-1}页)")
                    else:
                        print(f"    获取评论失败: {msg}")
                    break
                replies = data.get("data", {}).get("replies") or []
                if not replies:
                    break
                for reply in replies:
                    total_count += 1
                    if total_count <= skip_count:
                        continue
                    passed, sex, level = self._filter_reply(reply)
                    if passed:
                        uid = str(reply.get("member", {}).get("mid"))
                        uname = reply.get("member", {}).get("uname", "")
                        if uid and uid not in self.collected:
                            fans = self._get_fans_count(int(uid))
                            if fans < self.max_fans:
                                self.collected[uid] = {"uname": uname, "sex": sex, "level": level, "fans": fans}
                                print(f"      +{uname} (UID:{uid}, 性别:{sex}, 等级:{level}, 粉丝:{fans})")
                pn += 1
                time.sleep(self.request_interval)
            print(f"  {sort_name}完成, 已收集{len(self.collected)}个UID")
        return total_count
    def run(self, input_file="target_video.txt", output_file="collected_uids.csv", skip_comments=0):
        try:
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                bvs = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"文件不存在: {input_file}")
            return
        if not bvs:
            print("没有找到BV号")
            return
        if skip_comments > 0:
            print(f"跳过前{skip_comments}条评论")
        print(f"筛选条件: 性别{self.sex_filter}, 等级>={self.min_level}, 粉丝<{self.max_fans}")
        print(f"每视频{self.comment_pages}页, 每页{self.comments_per_page}条\n")
        remaining_skip = skip_comments
        for i, bv in enumerate(bvs):
            print(f"[视频{i + 1}] ", end="")
            processed = self.collect_from_video(bv, skip_count=remaining_skip)
            remaining_skip = max(0, remaining_skip - processed)
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["UID", "昵称", "性别", "等级", "粉丝数"])
            for uid, info in self.collected.items():
                writer.writerow([uid, info["uname"], info["sex"], info["level"], info["fans"]])
        print(f"\n完成! 共收集{len(self.collected)}个UID, 保存到{output_file}")
if __name__ == "__main__":
    import sys
    skip = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    CommentCollector().run(skip_comments=skip)
