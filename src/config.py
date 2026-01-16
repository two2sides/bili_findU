"""配置加载"""
import json
from pathlib import Path
class Config:
    def __init__(self, config_path="config.json"):
        config_file = Path(config_path)
        if not config_file.exists():
            config_file = Path(__file__).parent.parent / config_path
        with open(config_file, "r", encoding="utf-8") as f:
            self._config = json.load(f)
    @property
    def depth(self):
        return self._config.get("crawl_deepth", 0)
    @property
    def crawl_all(self):
        return self._config.get("crawl_all", False)
    @property
    def min_dynamics(self):
        return self._config.get("min_dynamics", 50)
    @property
    def request_interval(self):
        return self._config.get("request_interval", 0.3)
    @property
    def skip_empty_forward(self):
        return self._config.get("skip_empty_forward", False)
    @property
    def cookies(self):
        return self._config.get("cookies", {})
