"""
日期格式化
对应原Java的Formatter接口和DefaultFormatter类
"""
from abc import ABC, abstractmethod
from datetime import date

from .calendar_unit import CalendarType


class Formatter(ABC):
    """日期格式化接口"""

    @abstractmethod
    def get_day_name(self, date_obj: date) -> str:
        """获取星期名称"""
        pass

    @abstractmethod
    def get_header_text(
        self,
        calendar_type: CalendarType,
        from_date: date,
        to_date: date,
        selected: date
    ) -> str:
        """获取头部标题文本"""
        pass


class DefaultFormatter(Formatter):
    """默认日期格式化器"""

    # 星期名称
    WEEK_DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    def get_day_name(self, date_obj: date) -> str:
        """获取星期名称"""
        return self.WEEK_DAYS[date_obj.weekday()]

    def get_header_text(
        self,
        calendar_type: CalendarType,
        from_date: date,
        to_date: date,
        selected: date
    ) -> str:
        """
        获取头部标题文本

        规则：
        - 如果选中日期在范围内，显示选中日期的月份
        - 周视图默认显示结束日期的月份
        - 月视图默认显示开始日期的月份
        """
        # 如果选中日期在范围内，显示选中日期的月份
        if from_date <= selected <= to_date:
            return f"{selected.year}年{selected.month}月"

        # 根据类型决定显示
        if calendar_type == CalendarType.WEEK:
            return f"{to_date.year}年{to_date.month}月"
        else:  # MONTH
            return f"{from_date.year}年{from_date.month}月"
