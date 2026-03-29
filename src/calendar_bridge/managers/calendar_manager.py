"""
日历管理器
对应原Java的CalendarManager类
"""
from datetime import date, timedelta
from enum import Enum
from typing import Optional, Callable

try:
    from ..models.month import Month
    from ..models.week import Week
    from ..utils.calendar_unit import CalendarType
    from ..utils.formatter import Formatter, DefaultFormatter
    from ..utils.range_unit import RangeUnit
except ImportError:
    from models.month import Month
    from models.week import Week
    from utils.calendar_unit import CalendarType
    from utils.formatter import Formatter, DefaultFormatter
    from utils.range_unit import RangeUnit


class State(Enum):
    """日历状态枚举"""
    MONTH = "month"
    WEEK = "week"


class CalendarManager:
    """日历管理器类"""

    def __init__(
        self,
        selected: date,
        state: State,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        formatter: Optional[Formatter] = None
    ):
        self._today = date.today()
        self._state = state
        self._formatter = formatter or DefaultFormatter()
        self._min_date = min_date
        self._max_date = max_date
        self._selected = selected
        self._active_month = selected.replace(day=1)
        self._unit: Optional[RangeUnit] = None
        self._month_str = ""

        # 回调函数
        self._month_change_listener: Optional[Callable[[str, date], None]] = None
        self._week_change_listener: Optional[Callable[[str, date], None]] = None

        self.init(selected, min_date, max_date)

    @property
    def today(self) -> date:
        return self._today

    @property
    def state(self) -> State:
        return self._state

    @property
    def selected_day(self) -> date:
        return self._selected

    @property
    def active_month(self) -> date:
        return self._active_month

    @property
    def unit(self) -> Optional[RangeUnit]:
        return self._unit

    @property
    def min_date(self) -> Optional[date]:
        return self._min_date

    @min_date.setter
    def min_date(self, value: Optional[date]):
        self._min_date = value

    @property
    def max_date(self) -> Optional[date]:
        return self._max_date

    @max_date.setter
    def max_date(self, value: Optional[date]):
        self._max_date = value

    def set_month_change_listener(self, listener: Callable[[str, date], None]):
        """设置月份切换监听器"""
        self._month_change_listener = listener

    def set_week_change_listener(self, listener: Callable[[str, date], None]):
        """设置周切换监听器"""
        self._week_change_listener = listener

    def init(
        self,
        selected: date,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ):
        """初始化日历管理器"""
        self._selected = selected
        self._active_month = selected.replace(day=1)
        self._min_date = min_date
        self._max_date = max_date
        self._init_unit()

    def _init_unit(self):
        """初始化日历单元"""
        if self._state == State.MONTH:
            self._unit = Month(self._selected, self._today, self._min_date, self._max_date)
        else:
            self._unit = Week(self._selected, self._today, self._min_date, self._max_date)
        self._unit.select(self._selected)

    def select_day(self, date_obj: date) -> bool:
        """选择日期"""
        if self._selected != date_obj:
            self._unit.deselect(self._selected)
            self._selected = date_obj
            self._unit.select(self._selected)

            if self._state == State.WEEK:
                self._set_active_month(date_obj)
            return True
        return False

    def has_next(self) -> bool:
        """是否有下一项"""
        return self._unit.has_next()

    def has_prev(self) -> bool:
        """是否有前一项"""
        return self._unit.has_prev()

    def next(self) -> bool:
        """切换到下一项"""
        if not self._unit.next():
            return False

        if self._state == State.MONTH:
            # 月份模式：选中日期加一个月
            if self._selected.month == 12:
                self._selected = self._selected.replace(
                    year=self._selected.year + 1, month=1
                )
            else:
                self._selected = self._selected.replace(month=self._selected.month + 1)
        else:
            # 周模式：选中日期加一周
            self._selected = self._selected + timedelta(weeks=1)

        self._unit.select(self._selected)
        self._set_active_month(self._unit.from_date)
        return True

    def prev(self) -> bool:
        """切换到前一项"""
        if not self._unit.prev():
            return False

        if self._state == State.MONTH:
            # 月份模式：选中日期减一个月
            if self._selected.month == 1:
                self._selected = self._selected.replace(
                    year=self._selected.year - 1, month=12
                )
            else:
                self._selected = self._selected.replace(month=self._selected.month - 1)
        else:
            # 周模式：选中日期减一周
            self._selected = self._selected - timedelta(weeks=1)

        self._unit.select(self._selected)
        self._set_active_month(self._unit.to_date)
        return True

    def toggle_view(self):
        """切换视图（月视图/周视图）"""
        if self._state == State.MONTH:
            self._toggle_from_month()
        else:
            self._toggle_from_week()

    def _toggle_from_month(self):
        """从月视图切换到周视图"""
        # 如果选中日期在当前月视图中
        if self._unit.is_in_view(self._selected):
            self._toggle_to_week(self._selected)
            self._set_active_month(self._selected)
        else:
            self._set_active_month(self._unit.from_date)
            first_date = self._unit.get_first_date_of_current_month(self._active_month)
            if first_date:
                self._toggle_to_week(first_date)

    def _toggle_from_week(self):
        """从周视图切换到月视图"""
        self._unit = Month(self._active_month, self._today, self._min_date, self._max_date)
        self._unit.select(self._selected)
        self._state = State.MONTH

    def _toggle_to_week(self, date_obj: date):
        """切换到指定日期的周视图"""
        self._unit = Week(date_obj, self._today, self._min_date, self._max_date)
        self._unit.select(self._selected)
        self._state = State.WEEK

    def _set_active_month(self, active_month: date):
        """设置当前活动月份"""
        self._active_month = active_month.replace(day=1)

    def get_header_text(self) -> str:
        """获取头部标题文本"""
        header_text = self._formatter.get_header_text(
            CalendarType.MONTH if self._state == State.MONTH else CalendarType.WEEK,
            self._unit.from_date,
            self._unit.to_date,
            self._selected
        )

        if self._month_str != header_text:
            self._month_str = header_text
            if self._month_change_listener:
                self._month_change_listener(header_text, self._selected)

        return self._month_str

    def week_changed(self):
        """周切换时调用"""
        self._month_str = self._formatter.get_header_text(
            CalendarType.WEEK,
            self._unit.from_date,
            self._unit.to_date,
            self._selected
        )
        if self._week_change_listener:
            self._week_change_listener(self._month_str, self._selected)

    def get_current_month_date(self) -> date:
        """获取当前月份日期"""
        if self._unit is None or self._unit.from_date is None:
            return date.today()
        return self._unit.from_date

    def get_week_of_month(self) -> int:
        """获取选中日期在当前月的周数"""
        if self._unit.is_in_view(self._selected):
            if self._unit.is_in(self._selected):
                return self._unit.get_week_in_month(self._selected)
            elif self._unit.from_date > self._selected:
                return self._unit.get_week_in_month(self._unit.from_date)
            else:
                return self._unit.get_week_in_month(self._unit.to_date)
        else:
            first_date = self._unit.get_first_date_of_current_month(self._active_month)
            if first_date:
                return self._unit.get_first_week(first_date)
            return 0

    def change_date(self, new_date: date) -> bool:
        """切换到指定日期"""
        if new_date > self._selected:
            # 向后切换
            pass
        elif new_date < self._selected:
            # 向前切换
            pass

        self._selected = new_date
        self._active_month = new_date.replace(day=1)
        self.init(new_date, self._min_date, self._max_date)
        return True
