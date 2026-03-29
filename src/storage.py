# 数据存储工具
import os
import json
from src.config import DATA_PATH

# 创建存储目录
os.makedirs(DATA_PATH, exist_ok=True)

class Storage:
    @staticmethod
    def save(file, data):
        with open(f"{DATA_PATH}/{file}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(file, default=[]):
        path = f"{DATA_PATH}/{file}.json"
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
