"""
Calendar Bridge 模块
集成 python_calendar 核心功能
"""
from .adapter import ScheduleAdapter
from .widget_manager import widget_manager, WidgetManager

__all__ = ['ScheduleAdapter', 'widget_manager', 'WidgetManager']
