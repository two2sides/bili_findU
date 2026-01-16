"""数据存储"""
import csv
import json
from pathlib import Path
from .constants import CSV_HEADERS
class CsvStorage:
    def __init__(self, username, uid=None):
        filename = f"{uid}_{username}的成分表.csv" if uid else f"{username}的成分表.csv"
        self.savepath = Path("saved") / filename
        self.savepath.parent.mkdir(exist_ok=True)
        self._rows = []
    def append(self, datapage):
        self._rows.extend(datapage)
    def save(self):
        with open(self.savepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar='\\', doublequote=False)
            writer.writerow(CSV_HEADERS)
            for row in self._rows:
                writer.writerow(row)
    @property
    def count(self):
        return len(self._rows)
def save_raw_json(data, index):
    with open(f'raw_data_{index}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
