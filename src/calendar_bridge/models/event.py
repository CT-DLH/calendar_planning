"""
日程事件模型
对应原Java的EventModel类
"""
from datetime import datetime
from typing import Optional


class Event:
    """日程事件类"""

    def __init__(
        self,
        name: str = "",
        start_time: str = "",
        end_time: str = "",
        color: str = "",
        year: int = 0,
        month: int = 0,
        day: int = 0,
        event_id: str = None,
        module_name: str = "",
        position: str = ""
    ):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.color = color
        self.year = year
        self.month = month
        self.day = day
        self.id = event_id or str(int(datetime.now().timestamp() * 1000))
        self.module_name = module_name
        self.position = position
        self.date: Optional[datetime] = None

    def get_date_key(self) -> str:
        """获取日期键，用于按日期查询"""
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

    def __repr__(self):
        return f"Event(name='{self.name}', date={self.year}-{self.month:02d}-{self.day:02d})"
