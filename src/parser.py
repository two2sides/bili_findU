"""数据解析"""
import datetime
from .constants import DYNAMIC_TYPE_DICT, MAJOR_TYPE_DICT
class DynamicParser:
    def __init__(self, client=None):
        self.count = 0
        self.client = client
    @staticmethod
    def _split_major_type(text):
        """Do slice and lowercase the string 'MAJOR_TYPE_LIVE_RCMD' -> 'live_rcmd'"""
        parts = text.split('_')
        if len(parts) > 2:
            return '_'.join(parts[2:]).lower()
        return ""
    @staticmethod
    def get_username(data):
        items = data.get("data", {}).get("items", [])
        if items:
            return items[0].get("modules", {}).get("module_author", {}).get("name", "不发动态的人")
        return "不发动态的人"
    def _parse_major(self, major):
        if major is None:
            return "-", "-"
        major_type = major.get("type")
        if major_type is None:
            return "-", "-"
        major_key = self._split_major_type(major_type)
        ref_major_type = MAJOR_TYPE_DICT.get(major_key, "-")
        if major_key not in ('draw', 'live_rcmd', 'none'):
            major_value = major.get(major_key)
            ref_title = major_value.get("title", "-") if major_value else "-"
        else:
            ref_title = "*无标题*"
        return ref_major_type, ref_title.replace('\n', ' ')
    def _extract_detail_text_deprecated(self, detail):
        """[已弃用] 旧版detail接口解析"""
        try:
            nodes = detail.get("data", {}).get("item", {}).get("modules", {}).get("module_dynamic", {}).get("desc", {}).get("rich_text_nodes", [])
            texts = [node.get("orig_text", "") for node in nodes if node.get("orig_text")]
            return "".join(texts).replace("\n", " ") if texts else None
        except (AttributeError, TypeError):
            return None
    def _extract_detail_text(self, detail):
        try:
            modules = detail.get("data", {}).get("item", {}).get("modules", [])
            texts = []
            for module in modules:
                if module.get("module_type") == "MODULE_TYPE_CONTENT":
                    paragraphs = module.get("module_content", {}).get("paragraphs", [])
                    for para in paragraphs:
                        nodes = para.get("text", {}).get("nodes", [])
                        for node in nodes:
                            if "word" in node and "words" in node["word"]:
                                texts.append(node["word"]["words"])
            return "".join(texts).replace("\n", " ") if texts else None
        except (AttributeError, TypeError, KeyError):
            return None
    def _parse_item(self, item):
        module = item.get("modules", {})
        author = module.get("module_author")
        pub_ts = author.get("pub_ts") if author else None
        pub_time = datetime.datetime.fromtimestamp(int(pub_ts)) if pub_ts else "-"
        item_type = item.get("type")
        pub_type = DYNAMIC_TYPE_DICT.get(item_type, "-")
        detail_text = None
        if item_type == "DYNAMIC_TYPE_DRAW" and self.client:
            id_str = item.get("id_str")
            if id_str:
                detail = self.client.get_detail(id_str)
                if detail:
                    print(f"获取带图动态详情: {id_str}")
                    detail_text = self._extract_detail_text(detail)
        dynamic = module.get("module_dynamic")
        if dynamic is None:
            text = detail_text if detail_text else "-"
            return [pub_time, pub_type, text, "-", "-", "-"]
        desc = dynamic.get("desc")
        text = desc.get("text", "-") if desc else "-"
        text = text.replace("\n", " ")
        if detail_text:
            text = detail_text
        major = dynamic.get("major")
        orig = item.get("orig")
        if orig is None and major is None:
            return [pub_time, pub_type, text, "-", "-", "-"]
        if major is not None:
            ref_type = "投稿/更新"
        else:
            ref_type = "转发"
            major = orig.get("modules", {}).get("module_dynamic", {}).get("major")
        try:
            ref_major_type, ref_title = self._parse_major(major)
        except AttributeError as e:
            print(f"Error: {e}")
            return [pub_time, pub_type, text, ref_type, "N/A", "N/A"]
        return [pub_time, pub_type, text, ref_type, ref_major_type, ref_title]
    def parse(self, data, skip_empty_forward=False):
        items = data.get("data", {}).get("items", [])
        results = []
        for item in items:
            row = self._parse_item(item)
            if skip_empty_forward and row[3] == "转发" and row[2] in ("转发动态", "-"):
                continue
            results.append(row)
            self.count += 1
            print(f"{datetime.datetime.now()}:\033[32m[INFO]\033[0m Successfully get the data of >>{row[2]}")
        return results
