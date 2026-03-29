"""
月模型
对应原Java的Month类
"""
from datetime import date, timedelta
from typing import List, Optional

try:
    from .week import Week
    from ..utils.range_unit import RangeUnit
    from ..utils.calendar_unit import CalendarType
except ImportError:
    from week import Week
    from utils.range_unit import RangeUnit
    from utils.calendar_unit import CalendarType


class Month(RangeUnit):
    """月类，表示一个月"""

    def __init__(
        self,
        date_obj: date,
        today: date,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ):
        # 计算该月的第一天和最后一天
        first_day = date_obj.replace(day=1)
        if date_obj.month == 12:
            last_day = date_obj.replace(year=date_obj.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = date_obj.replace(month=date_obj.month + 1, day=1) - timedelta(days=1)

        super().__init__(first_day, last_day, today, min_date, max_date)
        self._weeks: List[Week] = []
        self._selected_index = -1
        self.build()

    @property
    def weeks(self) -> List[Week]:
        return self._weeks

    @property
    def selected_index(self) -> int:
        return self._selected_index

    def has_next(self) -> bool:
        """是否有下一月"""
        if self.max_date is None:
            return True

        to = self.to_date
        return (
            self.max_date.year > to.year or
            (self.max_date.year == to.year and self.max_date.month > to.month)
        )

    def has_prev(self) -> bool:
        """是否有前一月"""
        if self.min_date is None:
            return True

        from_date = self.from_date
        return (
            self.min_date.year < from_date.year or
            (self.min_date.year == from_date.year and self.min_date.month < from_date.month)
        )

    def next(self) -> bool:
        """切换到下一月"""
        if has_next := self.has_next():
            # 下个月的第一天
            if self.to_date.month == 12:
                next_month = self.to_date.replace(year=self.to_date.year + 1, month=1, day=1)
            else:
                next_month = self.to_date.replace(month=self.to_date.month + 1, day=1)

            # 下个月的最后一天
            if next_month.month == 12:
                next_month_last = next_month.replace(year=next_month.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                next_month_last = next_month.replace(month=next_month.month + 1, day=1) - timedelta(days=1)

            self.from_date = next_month
            self.to_date = next_month_last
            self.build()
        return has_next

    def prev(self) -> bool:
        """切换到前一月"""
        if has_prev := self.has_prev():
            # 上个月的第一天
            if self.from_date.month == 1:
                prev_month = self.from_date.replace(year=self.from_date.year - 1, month=12, day=1)
            else:
                prev_month = self.from_date.replace(month=self.from_date.month - 1, day=1)

            # 上个月的最后一天
            if prev_month.month == 12:
                prev_month_last = prev_month.replace(year=prev_month.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                prev_month_last = prev_month.replace(month=prev_month.month + 1, day=1) - timedelta(days=1)

            self.from_date = prev_month
            self.to_date = prev_month_last
            self.build()
        return has_prev

    def get_type(self) -> CalendarType:
        return CalendarType.MONTH

    def deselect(self, date_obj: date):
        """取消选择日期"""
        if date_obj is not None and self.is_selected and self.is_in_view(date_obj):
            for week in self._weeks:
                if week.is_selected and week.is_in(date_obj):
                    self._selected_index = -1
                    self.is_selected = False
                    week.deselect(date_obj)

    def select(self, date_obj: date) -> bool:
        """选择日期"""
        for i, week in enumerate(self._weeks):
            if week.select(date_obj):
                self._selected_index = i
                self.is_selected = True
                return True
        return False

    def build(self):
        """构建月的周列表"""
        self.is_selected = False
        self._weeks.clear()

        # 从该月第一周的周一开始
        first_monday = self.from_date - timedelta(days=self.from_date.weekday())

        current_date = first_monday
        week_index = 0
        while current_date <= self.to_date or week_index == 0:
            week = Week(current_date, self.today, self.min_date, self.max_date)
            self._weeks.append(week)
            current_date = current_date + timedelta(weeks=1)
            week_index += 1

    def get_first_date_of_current_month(self, current_month: date) -> Optional[date]:
        """
        获取当前月份在该月视图中的第一个可用日期

        Args:
            current_month: 当前月份的第一天

        Returns:
            第一个可用日期，如果没有则返回None
        """
        year = current_month.year
        month = current_month.month

        first_enabled = self.get_first_enabled()
        if first_enabled.year == year and first_enabled.month == month:
            return first_enabled

        return None
