"""WBI签名"""
from functools import reduce
from hashlib import md5
import urllib.parse
import time
import requests
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]
def get_mixin_key(orig: str):
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, '')[:32]
def enc_wbi(params: dict, img_key: str, sub_key: str):
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time
    params = dict(sorted(params.items()))
    params = {
        k: ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v in params.items()
    }
    query = urllib.parse.urlencode(params)
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = wbi_sign
    return params
class WbiSigner:
    def __init__(self, headers=None):
        self._headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        self._img_key = None
        self._sub_key = None
    def _fetch_wbi_keys(self):
        try:
            resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=self._headers)
            resp.raise_for_status()
            data = resp.json()
            img_url = data['data']['wbi_img']['img_url']
            sub_url = data['data']['wbi_img']['sub_url']
            self._img_key = img_url.rsplit('/', 1)[1].split('.')[0]
            self._sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
            print(f"获取WBI密钥成功")
        except Exception as e:
            print(f"获取WBI密钥失败: {e}")
    def sign(self, params: dict) -> dict:
        if not self._img_key or not self._sub_key:
            self._fetch_wbi_keys()
        if self._img_key and self._sub_key:
            return enc_wbi(params.copy(), self._img_key, self._sub_key)
        return params
