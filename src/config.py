# 配置文件

API_SYNC = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL_LIST = [
    "glm-4.7-flash", "glm-4v-flash", "glm-4.6v-flash",
    "glm-4.1v-thinking-flash", "glm-4-flash-250414"
]
AI_PROMPT = """你是专业的日程管理助手，只返回标准JSON格式，禁止任何解释、文字、markdown。
支持的指令类型：
1. add：添加日程 → {"type":"add","data":{"content":"日程内容","time":"14:00","tag":"normal","subtasks":[{"content":"子任务1"},{"content":"子任务2"}]}}
2. delete：删除日程 → {"type":"delete","keyword":"关键词"} 或 {"type":"delete","id":"日程ID"}
3. complete：标记完成 → {"type":"complete","id":"日程ID"} 或 {"type":"complete"}(全部完成)
4. clear：清空所有 → {"type":"clear"}
标签选项：normal(一般), important(重要), urgent(紧急), important_urgent(重要且紧急)
严格按照格式返回纯JSON！"""

# 存储路径
DATA_PATH = "schedule_data"

# 默认样式配置
DEFAULT_STYLE = {
    "theme": "dark",  # dark, light
    "colors": {
        "primary": "#3b82f6",
        "secondary": "#10b981",
        "background": "#121212",
        "surface": "#1e1e1e",
        "text": "#e0e0e0",
        "text_secondary": "#9ca3af",
        "border": "#333333",
        "today": "#3b82f6",
        "card": "#1f2937"
    },
    "fonts": {
        "family": "Arial",
        "size": {
            "small": 10,
            "normal": 12,
            "medium": 14,
            "large": 16,
            "xlarge": 18
        }
    },
    "sizes": {
        "card_radius": 8,
        "button_radius": 6,
        "padding": 8,
        "spacing": 2
    }
}

# 预设样式
PRESET_STYLES = {
    "dark": DEFAULT_STYLE,
    "light": {
        "theme": "light",
        "colors": {
            "primary": "#2563eb",
            "secondary": "#059669",
            "background": "#ffffff",
            "surface": "#f3f4f6",
            "text": "#1f2937",
            "text_secondary": "#6b7280",
            "border": "#e5e7eb",
            "today": "#3b82f6",
            "card": "#ffffff"
        },
        "fonts": DEFAULT_STYLE["fonts"],
        "sizes": DEFAULT_STYLE["sizes"]
    },
    "blue": {
        "theme": "dark",
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#60a5fa",
            "background": "#0f172a",
            "surface": "#1e293b",
            "text": "#f8fafc",
            "text_secondary": "#cbd5e1",
            "border": "#334155",
            "today": "#3b82f6",
            "card": "#1e293b"
        },
        "fonts": DEFAULT_STYLE["fonts"],
        "sizes": DEFAULT_STYLE["sizes"]
    },
    "green": {
        "theme": "dark",
        "colors": {
            "primary": "#10b981",
            "secondary": "#34d399",
            "background": "#064e3b",
            "surface": "#065f46",
            "text": "#ecfdf5",
            "text_secondary": "#94a3b8",
            "border": "#134e4a",
            "today": "#10b981",
            "card": "#065f46"
        },
        "fonts": DEFAULT_STYLE["fonts"],
        "sizes": DEFAULT_STYLE["sizes"]
    }
}
