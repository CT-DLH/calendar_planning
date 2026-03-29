"""
适配器层
将现有日程数据结构与 python_calendar 模型进行适配
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional

try:
    from .models.event import Event
    from .models.day import Day
    from .managers.calendar_manager import CalendarManager, State
except ImportError:
    from models.event import Event
    from models.day import Day
    from managers.calendar_manager import CalendarManager, State


class ScheduleAdapter:
    """日程数据适配器"""

    @staticmethod
    def schedule_to_event(schedule: Dict[str, Any]) -> Event:
        """将现有日程转换为 Event 模型"""
        event = Event()
        
        # 解析日期
        if "date" in schedule:
            try:
                date_parts = schedule["date"].split("-")
                if len(date_parts) == 3:
                    event.year = int(date_parts[0])
                    event.month = int(date_parts[1])
                    event.day = int(date_parts[2])
            except (ValueError, AttributeError):
                pass
        
        # 设置其他属性
        event.name = schedule.get("content", "")
        event.start_time = schedule.get("time", "")
        
        # 设置标签对应的颜色
        tag = schedule.get("tag", "normal")
        color_map = {
            "normal": "#9ca3af",
            "important": "#f59e0b",
            "urgent": "#ef4444",
            "important_urgent": "#dc2626"
        }
        event.color = color_map.get(tag, "#9ca3af")
        
        event.id = str(schedule.get("id", ""))
        event.module_name = "schedule"
        
        return event

    @staticmethod
    def event_to_schedule(event: Event) -> Dict[str, Any]:
        """将 Event 模型转换为现有日程格式"""
        schedule = {
            "id": event.id or str(int(datetime.now().timestamp() * 1000)),
            "content": event.name,
            "time": event.start_time,
            "date": f"{event.year}-{event.month:02d}-{event.day:02d}" if event.year and event.month and event.day else "",
            "completed": False,
            "tag": "normal",
            "subtasks": []
        }
        
        # 根据颜色反推标签
        color_tag_map = {
            "#f59e0b": "important",
            "#ef4444": "urgent",
            "#dc2626": "important_urgent"
        }
        if event.color in color_tag_map:
            schedule["tag"] = color_tag_map[event.color]
        
        return schedule

    @staticmethod
    def schedules_to_events(schedules: List[Dict[str, Any]]) -> List[Event]:
        """批量转换日程列表为 Event 列表"""
        return [ScheduleAdapter.schedule_to_event(s) for s in schedules]

    @staticmethod
    def events_to_schedules(events: List[Event]) -> List[Dict[str, Any]]:
        """批量转换 Event 列表为日程列表"""
        return [ScheduleAdapter.event_to_schedule(e) for e in events]
