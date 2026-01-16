"""HTTP请求封装"""
import json
import time
import requests
from .wbi import WbiSigner
class BiliClient:
    def __init__(self, config):
        self._config = config
        self._headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-Encoding': 'gzip, deflate, br, zstd',
            'accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
            'origin': 'https://space.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        }
        self._proxies = {"http": None, "https": None}
        self._wbi = None
    def _get_wbi(self):
        if self._wbi is None:
            self._wbi = WbiSigner(self._headers)
        return self._wbi
    def _build_cookies(self):
        return self._config.cookies
    def get_dynamics(self, url, uid, offset="", retry=0):
        params = {'offset': offset, 'host_mid': uid}
        try:
            resp = requests.get(url, params=params, cookies=self._build_cookies(),
                                headers=self._headers, timeout=15, proxies=self._proxies)
            if resp.status_code == 200:
                data = json.loads(resp.text)
                if data.get("code") == -352:
                    if retry < 3:
                        wait = 5 * (retry + 1)
                        print(f"  风控触发(-352), 等待{wait}秒后重试({retry+1}/3)...")
                        time.sleep(wait)
                        return self.get_dynamics(url, uid, offset, retry + 1)
                    print("  风控重试次数已达上限")
                return data
        except requests.RequestException as e:
            print(f"请求失败: {e}")
        print("鉴权失败! 请检查Cookie")
        return None
    def get_detail(self, id_str, retry=0):
        url = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/detail'
        params = {'id': id_str}
        signed_params = self._get_wbi().sign(params)
        try:
            resp = requests.get(url, params=signed_params, cookies=self._build_cookies(),
                                headers=self._headers, timeout=15, proxies=self._proxies)
            if resp.status_code == 200:
                data = json.loads(resp.text)
                if data.get("code") == -352:
                    if retry < 3:
                        wait = 5 * (retry + 1)
                        print(f"  风控触发(-352), 等待{wait}秒后重试({retry+1}/3)...")
                        time.sleep(wait)
                        return self.get_detail(id_str, retry + 1)
                return data
        except requests.RequestException as e:
            print(f"获取动态详情失败: {e}")
        return None
