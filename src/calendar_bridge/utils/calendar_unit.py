"""
日历单元基类
对应原Java的CalendarUnit类
"""
from abc import ABC, abstractmethod
from datetime import date
from enum import IntEnum


class CalendarType(IntEnum):
    """日历类型枚举"""
    WEEK = 1
    MONTH = 2


class CalendarUnit(ABC):
    """日历单元抽象基类"""

    def __init__(self, from_date: date, to_date: date, today: date):
        self._today = today
        self._from = from_date
        self._to = to_date
        self._is_selected = False

    @property
    def today(self) -> date:
        return self._today

    @property
    def from_date(self) -> date:
        return self._from

    @from_date.setter
    def from_date(self, value: date):
        self._from = value

    @property
    def to_date(self) -> date:
        return self._to

    @to_date.setter
    def to_date(self, value: date):
        self._to = value

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value

    @abstractmethod
    def has_next(self) -> bool:
        """是否有下一项"""
        pass

    @abstractmethod
    def has_prev(self) -> bool:
        """是否有前一项"""
        pass

    @abstractmethod
    def next(self) -> bool:
        """切换到下一项"""
        pass

    @abstractmethod
    def prev(self) -> bool:
        """切换到前一项"""
        pass

    @abstractmethod
    def get_type(self) -> CalendarType:
        """获取日历类型"""
        pass

    def is_in(self, check_date: date) -> bool:
        """检查日期是否在当前范围内"""
        return self._from <= check_date <= self._to

    def is_in_view(self, check_date: date) -> bool:
        """检查日期是否在当前视图中（扩展到周边界）"""
        from datetime import timedelta

        # 获取周一和周日
        from_weekday = self._from.weekday()  # 0=周一, 6=周日
        to_weekday = self._to.weekday()

        # 调整到周一开始（使用timedelta避免day out of range错误）
        view_from = self._from
        if from_weekday != 0:
            view_from = self._from - timedelta(days=from_weekday)

        # 调整到周日结束
        view_to = self._to
        if to_weekday != 6:
            view_to = self._to + timedelta(days=(6 - to_weekday))

        return view_from <= check_date <= view_to

    @abstractmethod
    def deselect(self, date_obj: date):
        """取消选择日期"""
        pass

    @abstractmethod
    def select(self, date_obj: date) -> bool:
        """选择日期"""
        pass

    @abstractmethod
    def build(self):
        """构建日历单元"""
        pass

    def __eq__(self, other):
        if not isinstance(other, CalendarUnit):
            return False
        return (
            self._from == other._from and
            self._to == other._to and
            self._today == other._today and
            self._is_selected == other._is_selected
        )

    def __hash__(self):
        return hash((self._from, self._to, self._today, self._is_selected))
