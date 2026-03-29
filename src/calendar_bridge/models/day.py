"""
日期模型
对应原Java的Day类
"""
from datetime import date


class Day:
    """日期类，表示日历中的某一天"""

    def __init__(self, date_obj: date, is_today: bool = False):
        self._date = date_obj
        self._is_today = is_today
        self._is_selected = False
        self._is_enabled = True
        self._is_current = True

    @property
    def date(self) -> date:
        return self._date

    @property
    def is_today(self) -> bool:
        return self._is_today

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value: bool):
        self._is_enabled = value

    @property
    def is_current(self) -> bool:
        return self._is_current

    @is_current.setter
    def is_current(self, value: bool):
        self._is_current = value

    def get_text(self) -> str:
        """获取日期文本（如：1, 2, 3...）"""
        return str(self._date.day)

    def __eq__(self, other):
        if not isinstance(other, Day):
            return False
        return (
            self._date == other._date and
            self._is_today == other._is_today and
            self._is_selected == other._is_selected and
            self._is_enabled == other._is_enabled
        )

    def __hash__(self):
        return hash((self._date, self._is_today, self._is_selected, self._is_enabled))

    def __repr__(self):
        return f"Day({self._date}, today={self._is_today}, selected={self._is_selected})"
