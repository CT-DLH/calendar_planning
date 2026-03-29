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
    
    @staticmethod
    def save_config(api_key, model):
        """保存配置（API Key 和模型）"""
        config = {
            "api_key": api_key,
            "model": model
        }
        Storage.save("config", config)
    
    @staticmethod
    def load_config():
        """加载配置"""
        config = Storage.load("config", {})
        return config.get("api_key", ""), config.get("model", "")
