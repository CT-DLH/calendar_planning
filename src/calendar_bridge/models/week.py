"""
周模型
对应原Java的Week类
"""
from datetime import date, timedelta
from typing import List, Optional

try:
    from .day import Day
    from ..utils.range_unit import RangeUnit
    from ..utils.calendar_unit import CalendarType
except ImportError:
    from day import Day
    from utils.range_unit import RangeUnit
    from utils.calendar_unit import CalendarType


class Week(RangeUnit):
    """周类，表示一周（周一到周日）"""

    def __init__(
        self,
        date_obj: date,
        today: date,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ):
        # 计算该周的周一和周日
        monday = date_obj - timedelta(days=date_obj.weekday())
        sunday = monday + timedelta(days=6)

        super().__init__(monday, sunday, today, min_date, max_date)
        self._days: List[Day] = []
        self.build()

    @property
    def days(self) -> List[Day]:
        return self._days

    def has_next(self) -> bool:
        """是否有下一周"""
        if self.max_date is None:
            return True
        return self.max_date > self._days[-1].date

    def has_prev(self) -> bool:
        """是否有前一周"""
        if self.min_date is None:
            return True
        return self.min_date < self._days[0].date

    def next(self) -> bool:
        """切换到下一周"""
        if has_next := self.has_next():
            self.from_date = self.from_date + timedelta(weeks=1)
            self.to_date = self.to_date + timedelta(weeks=1)
            self.build()
        return has_next

    def prev(self) -> bool:
        """切换到前一周"""
        if has_prev := self.has_prev():
            self.from_date = self.from_date - timedelta(weeks=1)
            self.to_date = self.to_date - timedelta(weeks=1)
            self.build()
        return has_prev

    def get_type(self) -> CalendarType:
        return CalendarType.WEEK

    def deselect(self, date_obj: date):
        """取消选择日期"""
        if self.from_date <= date_obj <= self.to_date:
            self.is_selected = False
            for day in self._days:
                day.is_selected = False

    def select(self, date_obj: date) -> bool:
        """选择日期"""
        if self.from_date <= date_obj <= self.to_date:
            self.is_selected = True
            for day in self._days:
                day.is_selected = day.date == date_obj
            return True
        return False

    def build(self):
        """构建周的日期列表"""
        self._days.clear()

        current_date = self.from_date
        while current_date <= self.to_date:
            day = Day(current_date, current_date == self.today)
            day.is_enabled = self.is_day_enabled(current_date)
            self._days.append(day)
            current_date = current_date + timedelta(days=1)

    def get_first_date_of_current_month(self, current_month: date) -> Optional[date]:
        """
        获取当前月份在该周中的第一个日期

        Args:
            current_month: 当前月份的第一天

        Returns:
            该周中属于当前月份的第一个日期，如果没有则返回None
        """
        year = current_month.year
        month = current_month.month

        current_date = self.from_date
        while current_date <= self.to_date:
            if current_date.year == year and current_date.month == month:
                return current_date
            current_date = current_date + timedelta(days=1)

        return None
