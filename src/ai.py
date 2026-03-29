# AI功能模块
import requests
import json
from src.config import API_SYNC, AI_PROMPT

class AIClient:
    @staticmethod
    def run_command(api_key, model, prompt):
        try:
            res = requests.post(API_SYNC, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }, json={
                "model": model,
                "temperature": 0.1,
                "messages": [{"role": "system", "content": AI_PROMPT}, {"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }, timeout=10)
            data = res.json()
            content = data["choices"][0]["message"]["content"].replace("```json", "").replace("```", "")
            return json.loads(content)
        except Exception as e:
            raise e

    @staticmethod
    def get_suggestion(api_key, model, schedules, prompt):
        try:
            res = requests.post(API_SYNC, headers={
                "Authorization": f"Bearer {api_key}", 
                "Content-Type": "application/json"
            }, json={
                "model": model,
                "messages": [{"role": "user", "content": f"当前日程：{json.dumps(schedules)}，需求：{prompt}"}]
            }, timeout=10)
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise e
