"""
范围单元类
对应原Java的RangeUnit类
"""
from datetime import date, timedelta
from typing import Optional

from .calendar_unit import CalendarUnit


class RangeUnit(CalendarUnit):
    """范围单元基类，支持最小/最大日期限制"""

    def __init__(
        self,
        from_date: date,
        to_date: date,
        today: date,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ):
        super().__init__(from_date, to_date, today)

        if min_date and max_date and min_date > max_date:
            raise ValueError("Min date should be before max date")

        self._min_date = min_date
        self._max_date = max_date

    @property
    def min_date(self) -> Optional[date]:
        return self._min_date

    @property
    def max_date(self) -> Optional[date]:
        return self._max_date

    def get_first_week(self, first_day_of_month: Optional[date]) -> int:
        """
        获取第一个可用日期所在的周数

        Args:
            first_day_of_month: 当前月份的第一天

        Returns:
            周数，从0开始
        """
        if self._min_date and self._min_date > self._from:
            date_to_check = self._min_date
        else:
            date_to_check = first_day_of_month or self._from

        return self.get_week_in_month(date_to_check)

    def get_first_enabled(self) -> date:
        """获取第一个启用的日期"""
        if self._min_date and self._from < self._min_date:
            return self._min_date
        return self._from

    def get_week_in_month(self, date_obj: Optional[date]) -> int:
        """
        获取日期在月份中的周数

        Args:
            date_obj: 日期对象

        Returns:
            周数，从0开始
        """
        if date_obj is None:
            return 0

        # 获取该月第一天
        first_day = date_obj.replace(day=1)
        # 获取该月第一周的周一
        first_monday = first_day - timedelta(days=first_day.weekday())

        # 计算天数差
        days_diff = (date_obj - first_monday).days
        return days_diff // 7

    def is_day_enabled(self, check_date: date) -> bool:
        """检查日期是否可用（在最小/最大日期范围内）"""
        if self._min_date and check_date < self._min_date:
            return False
        if self._max_date and check_date > self._max_date:
            return False
        return True
