# 界面模块
import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from src.storage import Storage
from src.ai import AIClient
from src.config import MODEL_LIST, DEFAULT_STYLE, PRESET_STYLES
from src.system_calendar import SystemCalendar
from src.calendar_bridge import widget_manager
from src.time_parser import TimeParser

from src.ui_widgets import AIChatWidget, ScheduleButton, ClickableDateCard
from src.ui_dialogs import ScheduleDialog, TodoScheduleBox, TagManagerDialog
from src.tag_manager import TagManager

class ScheduleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📅 AI日程管理器")
        self.setMinimumSize(900, 600)
        self.resize(1000, 650)

        # 全局状态
        self.schedules = Storage.load("schedules")
        self.recycle_bin = Storage.load("recycle_bin")
        self.habits = Storage.load("habits")
        self.todo_schedules = Storage.load("todo")
        self.current_date = datetime.now()
        self.current_view = "day"  # 默认显示日视图，避免周视图的问题
        self.hide_completed = False
        self.is_requesting = False
        self.current_tag_filter = "all"  # 标签筛选，"all"表示全部
        
        # 系统日历集成
        self.system_calendar = SystemCalendar()
        
        # 标签管理器
        self.tag_manager = TagManager()
        
        # 加载样式配置
        self.current_style = Storage.load("style", DEFAULT_STYLE)

        # 初始化UI
        self.init_ui()
        self.apply_style()
        
        # 初始化标签筛选
        self.update_tag_filter_options()
        
        self.render_calendar()

    def init_ui(self):
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 顶部拖拽栏
        self.drag_bar = QWidget()
        self.drag_bar.setStyleSheet("background:linear-gradient(to right,#2563eb,#4f46e5);")
        drag_layout = QHBoxLayout(self.drag_bar)
        drag_layout.setContentsMargins(10, 8, 10, 8)
        title = QLabel("📅 日程管理器")
        title.setStyleSheet("color:white;font-weight:bold;")
        self.min_btn = QPushButton("−")
        self.close_btn = QPushButton("×")
        self.settings_btn = QPushButton("设置")
        self.ai_toggle_btn = QPushButton("AI助手")
        self.add_schedule_btn = QPushButton("+ 日程")
        for btn in [self.min_btn, self.close_btn]:
            btn.setFixedSize(25, 25)
            btn.setStyleSheet("color:white;border:none;")
        for btn in [self.settings_btn, self.ai_toggle_btn, self.add_schedule_btn]:
            btn.setStyleSheet("color:white;border:none;padding:4px 8px;")
        drag_layout.addWidget(title)
        drag_layout.addStretch()
        drag_layout.addWidget(self.add_schedule_btn)
        drag_layout.addWidget(self.ai_toggle_btn)
        drag_layout.addWidget(self.settings_btn)
        drag_layout.addWidget(self.min_btn)
        drag_layout.addWidget(self.close_btn)
        main_layout.addWidget(self.drag_bar)

        # 3. 视图切换 + 日期导航
        self.nav_widget = QWidget()
        self.nav_widget.setStyleSheet("padding:8px;border-bottom:1px solid #374151;")
        nav_layout = QHBoxLayout(self.nav_widget)
        # 视图按钮
        self.view_btns = {
            "day": QPushButton("日"),
            "week": QPushButton("周"),
            "month": QPushButton("月"),
            "todo": QPushButton("待办")
        }
        for btn in self.view_btns.values():
            btn.setFixedSize(30, 25)
            nav_layout.addWidget(btn)
        nav_layout.addStretch()
        # 日期导航
        self.prev_btn = QPushButton("←")
        self.title_label = QLabel("日期")
        self.next_btn = QPushButton("→")
        self.hide_check = QCheckBox("隐藏已完成")
        self.tag_filter_input = QLineEdit()
        self.tag_filter_input.setPlaceholderText("输入标签名称")
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.title_label)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.hide_check)
        nav_layout.addWidget(QLabel("标签:"))
        nav_layout.addWidget(self.tag_filter_input)
        main_layout.addWidget(self.nav_widget)

        # 4. 主内容区（横板布局）
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 左侧：日历视图
        calendar_container = QWidget()
        calendar_layout = QVBoxLayout(calendar_container)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.setSpacing(0)

        # 星期栏
        self.week_bar = QWidget()
        week_layout = QHBoxLayout(self.week_bar)
        week_layout.setContentsMargins(5, 5, 5, 5)
        for w in ["日", "一", "二", "三", "四", "五", "六"]:
            lbl = QLabel(w)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight:bold;")
            week_layout.addWidget(lbl)
        calendar_layout.addWidget(self.week_bar)

        # 日历网格
        self.calendar_grid = QWidget()
        self.grid_layout = QGridLayout(self.calendar_grid)
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        calendar_layout.addWidget(self.calendar_grid)

        # 中间：日程列表和操作栏
        schedule_container = QWidget()
        schedule_layout = QVBoxLayout(schedule_container)
        schedule_layout.setContentsMargins(0, 0, 0, 0)
        schedule_layout.setSpacing(0)

        # 日程列表区域（添加滚动功能）
        self.schedule_scroll = QScrollArea()
        self.schedule_scroll.setWidgetResizable(True)
        self.schedule_list = QWidget()
        self.schedule_list_layout = QVBoxLayout(self.schedule_list)
        self.schedule_list_layout.setContentsMargins(10, 10, 10, 10)
        self.schedule_scroll.setWidget(self.schedule_list)
        schedule_layout.addWidget(self.schedule_scroll)

        # 右侧：AI 对话窗口
        self.ai_chat_widget = AIChatWidget(self)
        self.ai_chat_widget.setMinimumWidth(350)
        self.ai_chat_widget.setMaximumWidth(400)

        # 添加到主内容区
        content_layout.addWidget(calendar_container, 1)
        content_layout.addWidget(schedule_container, 1)
        content_layout.addWidget(self.ai_chat_widget, 0)
        main_layout.addWidget(content_widget, 1)

        # 绑定事件
        self.bind_events()
        
        # 拖拽功能变量
        self.drag_pos = None

    # ===================== 应用样式 =====================
    def apply_style(self):
        colors = self.current_style['colors']
        fonts = self.current_style['fonts']
        sizes = self.current_style['sizes']
        
        style = f"""
            QMainWindow, QWidget {{background:{colors['background']};color:{colors['text']};}}
            QLineEdit, QComboBox, QTextEdit, QGroupBox {{
                background:{colors['surface']};border:1px solid {colors['border']};border-radius:{sizes['button_radius']}px;
                padding:{sizes['padding']}px;color:{colors['text']};
                font-family:{fonts['family']};font-size:{fonts['size']['normal']}px;
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border:1px solid {colors['primary']};
            }}
            QPushButton {{
                background:{colors['surface']};border:1px solid {colors['border']};border-radius:{sizes['button_radius']}px;
                padding:{sizes['padding']}px 10px;color:{colors['text']};
                font-family:{fonts['family']};font-size:{fonts['size']['normal']}px;
            }}
            QPushButton:hover {{background:{colors['card']};}}
            QPushButton:pressed {{background:{colors['border']};}}
            QCheckBox {{color:{colors['text']};font-family:{fonts['family']};font-size:{fonts['size']['normal']}px;}}
            QLabel {{color:{colors['text']};font-family:{fonts['family']};font-size:{fonts['size']['normal']}px;}}
            QGroupBox {{font-family:{fonts['family']};font-size:{fonts['size']['medium']}px;font-weight:bold;}}
            QPushButton#green {{background:{colors['secondary']};color:white;}}
            QPushButton#green:hover {{background:{colors['secondary']};opacity:0.9;}}
            QPushButton#blue {{background:{colors['primary']};color:white;}}
            QPushButton#blue:hover {{background:{colors['primary']};opacity:0.9;}}
            QPushButton#red {{background:#ef4444;color:white;}}
            QPushButton#red:hover {{background:#dc2626;}}
            QPushButton#yellow {{background:#f59e0b;color:white;}}
            QPushButton#yellow:hover {{background:#d97706;}}
            QPushButton#purple {{background:#8b5cf6;color:white;}}
            QPushButton#purple:hover {{background:#7c3aed;}}
        """
        
        self.setStyleSheet(style)
        
        # 更新拖拽栏样式
        self.drag_bar.setStyleSheet(f"background:linear-gradient(to right,{colors['primary']},{colors['secondary']});")
        
        # 更新导航栏样式
        self.nav_widget.setStyleSheet(f"padding:{sizes['padding']}px;border-bottom:1px solid {colors['border']};")

    # ===================== 事件绑定 =====================
    def bind_events(self):
        self.close_btn.clicked.connect(self.close)
        self.min_btn.clicked.connect(self.showMinimized)
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        self.hide_check.clicked.connect(lambda: setattr(self, 'hide_completed', self.hide_check.isChecked()) or self.render_calendar())
        # 视图切换
        self.view_btns["day"].clicked.connect(lambda: self.switch_view("day"))
        self.view_btns["week"].clicked.connect(lambda: self.switch_view("week"))
        self.view_btns["month"].clicked.connect(lambda: self.switch_view("month"))
        self.view_btns["todo"].clicked.connect(lambda: self.switch_view("todo"))
        # 日期导航
        self.prev_btn.clicked.connect(self.prev_period)
        self.next_btn.clicked.connect(self.next_period)
        # 功能按钮
        self.add_schedule_btn.clicked.connect(self.add_schedule)
        # AI 助手按钮
        self.ai_toggle_btn.clicked.connect(self.toggle_ai_visibility)
        # 标签筛选
        self.tag_filter_input.textChanged.connect(self.on_tag_filter_changed)
    
    def update_tag_filter_options(self):
        # 移除标签筛选下拉框，改为输入框，不需要更新选项
        pass
    
    def on_tag_filter_changed(self):
        # 获取输入的标签名称
        tag_name = self.tag_filter_input.text().strip()
        # 如果输入为空，使用"all"表示全部
        self.current_tag_filter = tag_name if tag_name else "all"
        self.render_calendar()
    
    def filter_schedules_by_tag(self, schedules):
        if self.current_tag_filter == "all":
            return schedules
        # 根据输入的标签名称进行筛选
        tag_name = self.current_tag_filter
        return [s for s in schedules if s.get("tag", "normal") == tag_name]

    # ===================== 视图切换 =====================
    def switch_view(self, view):
        self.current_view = view
        self.render_calendar()

    def prev_period(self):
        if self.current_view == "day":
            self.current_date -= timedelta(days=1)
        elif self.current_view == "week":
            self.current_date -= timedelta(days=7)
        elif self.current_view == "month":
            self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.render_calendar()

    def next_period(self):
        if self.current_view == "day":
            self.current_date += timedelta(days=1)
        elif self.current_view == "week":
            self.current_date += timedelta(days=7)
        elif self.current_view == "month":
            # 先将日期设置为当月第一天，避免day值超出新月份的最大天数
            first_day = self.current_date.replace(day=1)
            # 计算下一个月
            month = first_day.month % 12 + 1
            year = first_day.year + (1 if month == 1 else 0)
            # 更新日期
            self.current_date = first_day.replace(year=year, month=month)
        self.render_calendar()

    # ===================== 日历渲染 =====================
    def render_calendar(self):
        try:
            # 更新标签筛选下拉框选项
            self.update_tag_filter_options()
            
            # 使用 widget_manager 安全清空网格和日程列表
            widget_manager.clear_layout(self.grid_layout)
            widget_manager.clear_layout(self.schedule_list_layout)

            if self.current_view == "day":
                self.render_day()
            elif self.current_view == "week":
                self.render_week()
            elif self.current_view == "month":
                self.render_month()
            elif self.current_view == "todo":
                self.render_todo()
        except Exception as e:
            print(f"Error in render_calendar: {e}")
            import traceback
            traceback.print_exc()

    def render_day(self):
        self.title_label.setText(self.current_date.strftime("%Y年%m月%d日"))
        self.week_bar.hide()

        day_str = self.current_date.strftime("%Y-%m-%d")
        day_schedules = [s for s in self.schedules if s["date"] == day_str]
        if self.hide_completed:
            day_schedules = [s for s in day_schedules if not s["completed"]]
        day_schedules = self.filter_schedules_by_tag(day_schedules)
        
        # 对日程进行排序
        day_schedules = self.sort_schedules(day_schedules)

        # 获取当前样式配置
        colors = self.current_style['colors']
        sizes = self.current_style['sizes']
        fonts = self.current_style['fonts']

        # 左侧：日历视图（水平布局优化）
        day_widget = QWidget()
        day_widget.setStyleSheet(f"background:{colors['card']};border-radius:{sizes['card_radius']}px;padding:{sizes['padding']}px;")
        day_lay = QVBoxLayout(day_widget)
        day_lay.setContentsMargins(sizes['padding'], sizes['padding'], sizes['padding'], sizes['padding'])
        
        # 日期标题
        date_label = QLabel(f"📅 {self.current_date.year}年{self.current_date.month}月{self.current_date.day}日")
        date_label.setStyleSheet(f"font-size:{fonts['size']['large']}px;font-weight:bold;margin-bottom:{sizes['padding']}px;")
        day_lay.addWidget(date_label)
        
        # 显示当天的日程概览
        if day_schedules:
            day_lay.addWidget(QLabel("今日日程："))
            for s in day_schedules[:3]:  # 只显示前3个日程
                # 优先使用 start_time 和 end_time，没有时回退到旧 time 字段
                display_time = s.get("start_time", "")
                if display_time and s.get("end_time", ""):
                    display_time = f"{display_time}-{s['end_time']}"
                elif not display_time:
                    display_time = s.get("time", "")
                time_label = QLabel(f"• {display_time} {s['content']}")
                time_label.setStyleSheet("margin-left:10px;")
                day_lay.addWidget(time_label)
            if len(day_schedules) > 3:
                day_lay.addWidget(QLabel(f"... 还有 {len(day_schedules) - 3} 个日程"))
        else:
            day_lay.addWidget(QLabel("今日暂无日程"))
        
        self.grid_layout.addWidget(day_widget, 0, 0)

        # 右侧：日程表格
        self.schedule_list_layout.addWidget(QLabel(f"📅 {self.current_date.day}日 日程"))

        # 习惯
        if self.habits:
            self.schedule_list_layout.addWidget(QLabel("🟣 每日习惯"))
            for h in self.habits:
                self.schedule_list_layout.addWidget(QLabel(f"◽ {h['time']} {h['content']}"))

        # 待办日程
        if self.todo_schedules:
            self.schedule_list_layout.addWidget(QLabel("🟢 待办日程"))
            for g in self.todo_schedules:
                self.schedule_list_layout.addWidget(QLabel(f"◽ {g['time']} {g['content']}"))

        # 当日日程表格
        self.schedule_list_layout.addWidget(QLabel("🔵 当日日程"))
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["✓", "时间", "内容", "标签", "操作"])
        
        # 设置表格样式
        table.setStyleSheet(f"""
            QTableWidget {{
                background:{colors['surface']};
                border:1px solid {colors['border']};
                color:{colors['text']};
                gridline-color:{colors['border']};
                font-family:{fonts['family']};
                font-size:{fonts['size']['normal']}px;
            }}
            QTableWidget::item {{
                padding:8px;
            }}
            QTableWidget::item:selected {{
                background:{colors['primary']};
                color:white;
            }}
            QHeaderView::section {{
                background:{colors['card']};
                color:{colors['text']};
                padding:8px;
                border:1px solid {colors['border']};
                font-weight:bold;
            }}
            QPushButton {{
                background:{colors['surface']};
                border:1px solid {colors['border']};
                border-radius:{sizes['button_radius']}px;
                padding:4px 8px;
                color:{colors['text']};
                font-size:{fonts['size']['small']}px;
            }}
            QPushButton:hover {{
                background:{colors['card']};
            }}
            QPushButton#edit {{
                background:{colors['primary']};
                color:white;
            }}
            QPushButton#delete {{
                background:#ef4444;
                color:white;
            }}
        """)
        
        # 设置列宽
        table.horizontalHeader().setStretchLastSection(True)
        table.setColumnWidth(0, 40)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 250)
        table.setColumnWidth(3, 100)
        
        # 设置行高
        table.verticalHeader().setDefaultSectionSize(45)
        
        # 填充数据
        table.setRowCount(len(day_schedules))
        
        for row, s in enumerate(day_schedules):
            # 复选框列
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(10, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            checkbox = QCheckBox()
            checkbox.setChecked(s.get("completed", False))
            checkbox.stateChanged.connect(lambda state, s=s: self.toggle_schedule_completed(s))
            checkbox_layout.addWidget(checkbox)
            
            table.setCellWidget(row, 0, checkbox_widget)
            
            # 时间列
            display_time = s.get("start_time", "")
            if display_time and s.get("end_time", ""):
                display_time = f"{display_time}-{s['end_time']}"
            elif not display_time:
                display_time = s.get("time", "")
            
            time_item = QTableWidgetItem(display_time)
            time_item.setData(Qt.ItemDataRole.UserRole, s)
            if s["completed"]:
                time_item.setForeground(QColor("#9ca3af"))
                font = time_item.font()
                font.setStrikeOut(True)
                time_item.setFont(font)
            table.setItem(row, 1, time_item)
            
            # 内容列
            content_text = f"{'✅ ' if s['completed'] else ''}{s['content']}"
            content_item = QTableWidgetItem(content_text)
            content_item.setData(Qt.ItemDataRole.UserRole, s)
            if s["completed"]:
                content_item.setForeground(QColor("#9ca3af"))
                font = content_item.font()
                font.setStrikeOut(True)
                content_item.setFont(font)
            table.setItem(row, 2, content_item)
            
            # 标签列
            tag_id = s.get("tag", "normal")
            importance = s.get("importance", 0)
            urgency = s.get("urgency", 0)
            
            # 构建标签文本
            tag_parts = []
            
            # 添加自定义标签
            if tag_id != "normal":
                tag_parts.append(tag_id)
            
            # 添加重要程度和紧急程度
            if importance > 0 or urgency > 0:
                tag_parts.append(f"重要:{importance} 紧急:{urgency}")
            
            # 如果没有标签，使用默认值
            tag_text = "一般" if not tag_parts else " ".join(tag_parts)
            tag_item = QTableWidgetItem(tag_text)
            tag_item.setData(Qt.ItemDataRole.UserRole, s)
            if s["completed"]:
                tag_item.setForeground(QColor("#9ca3af"))
                font = tag_item.font()
                font.setStrikeOut(True)
                tag_item.setFont(font)
            table.setItem(row, 3, tag_item)
            
            # 操作列
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 5, 5, 5)
            action_layout.setSpacing(8)
            
            edit_btn = QPushButton("编辑")
            edit_btn.setObjectName("edit")
            edit_btn.clicked.connect(lambda checked, s=s: self.edit_schedule_direct(s))
            
            delete_btn = QPushButton("删除")
            delete_btn.setObjectName("delete")
            delete_btn.clicked.connect(lambda checked, s=s: self.delete_schedule_direct(s))
            
            action_layout.addStretch()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            
            table.setCellWidget(row, 4, action_widget)
        
        # 设置表格选择行为
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 连接双击事件
        table.cellDoubleClicked.connect(lambda row, col: self.on_table_cell_double_clicked(row, col, table))
        
        self.schedule_list_layout.addWidget(table)



    def render_week(self):
        try:
            self.title_label.setText(self.current_date.strftime("%Y年%m月第%W周"))
            self.week_bar.show()
            start = self.current_date - timedelta(days=self.current_date.weekday() + 1)
            
            # 左侧：周视图日历（水平布局优化）
            
            # 添加日期卡片
            for i in range(7):
                day = start + timedelta(days=i)
                widget = self.create_day_card(day)
                widget.setMinimumWidth(100)
                widget.setMinimumHeight(150)
                self.grid_layout.addWidget(widget, 0, i)
            
            # 右侧：本周日程列表
            self.schedule_list_layout.addWidget(QLabel("📅 本周日程"))
            
            # 获取本周所有日程
            week_schedules = []
            for i in range(7):
                day = start + timedelta(days=i)
                day_str = day.strftime("%Y-%m-%d")
                for s in self.schedules:
                    # 跳过空日期的日程
                    if not s.get("date", ""):
                        continue
                    if s["date"] == day_str:
                        if not self.hide_completed or not s["completed"]:
                            week_schedules.append(s)
            week_schedules = self.filter_schedules_by_tag(week_schedules)
            
            # 对日程进行排序
            week_schedules = self.sort_schedules(week_schedules)
            
            if not week_schedules:
                self.schedule_list_layout.addWidget(QLabel("本周暂无日程"))
            else:
                for s in week_schedules:
                    # 创建带有复选框的日程行
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(5, 5, 5, 5)
                    row_layout.setSpacing(10)
                    
                    # 复选框
                    checkbox = QCheckBox()
                    checkbox.setChecked(s.get("completed", False))
                    checkbox.stateChanged.connect(lambda state, s=s: self.toggle_schedule_completed(s))
                    row_layout.addWidget(checkbox)
                    
                    # 优先使用 start_time 和 end_time，没有时回退到旧 time 字段
                    display_time = s.get("start_time", "")
                    if display_time and s.get("end_time", ""):
                        display_time = f"{display_time}-{s['end_time']}"
                    elif not display_time:
                        display_time = s.get("time", "")
                    
                    # 获取标签文本
                    tag_id = s.get("tag", "normal")
                    importance = s.get("importance", 0)
                    urgency = s.get("urgency", 0)
                    
                    # 构建标签文本
                    tag_parts = []
                    
                    # 添加自定义标签
                    if tag_id != "normal":
                        tag_parts.append(tag_id)
                    
                    # 添加重要程度和紧急程度
                    if importance > 0 or urgency > 0:
                        tag_parts.append(f"重要:{importance} 紧急:{urgency}")
                    
                    # 如果没有标签，使用默认值
                    tag_text = "一般" if not tag_parts else " ".join(tag_parts)
                    
                    txt = f"{s['date']} {display_time} {s['content']} [标签: {tag_text}]"
                    
                    # 日程按钮
                    btn = ScheduleButton(txt, s)
                    if s["completed"]:
                        btn.setStyleSheet("text-align:left;border:none;text-decoration:line-through;color:#9ca3af;")
                    btn.clicked.connect(lambda checked, s=s: self.edit_schedule_direct(s))
                    # 设置长按事件处理
                    btn.on_long_press = lambda s=s: self.on_schedule_long_press(s)
                    
                    row_layout.addWidget(btn, 1)
                    self.schedule_list_layout.addWidget(row_widget)
        except Exception as e:
            print(f"Error in render_week: {e}")
            import traceback
            traceback.print_exc()

    def render_month(self):
        try:
            self.title_label.setText(self.current_date.strftime("%Y年%m月"))
            self.week_bar.show()
            first = self.current_date.replace(day=1)
            start = first - timedelta(days=first.weekday() + 1)
            
            # 左侧：月视图日历
            for i in range(42):
                day = start + timedelta(days=i)
                widget = self.create_day_card(day)
                self.grid_layout.addWidget(widget, i // 7, i % 7)
            
            # 右侧：本月日程列表
            self.schedule_list_layout.addWidget(QLabel("📅 本月日程"))
            
            # 获取本月所有日程
            month_schedules = []
            year, month = self.current_date.year, self.current_date.month
            for s in self.schedules:
                # 跳过空日期的日程
                if not s.get("date", ""):
                    continue
                try:
                    s_date = datetime.strptime(s["date"], "%Y-%m-%d")
                    if s_date.year == year and s_date.month == month:
                        if not self.hide_completed or not s["completed"]:
                            month_schedules.append(s)
                except (ValueError, TypeError):
                    # 如果日期解析失败，跳过这个日程
                    continue
            month_schedules = self.filter_schedules_by_tag(month_schedules)
            
            # 对日程进行排序
            month_schedules = self.sort_schedules(month_schedules)
            
            if not month_schedules:
                self.schedule_list_layout.addWidget(QLabel("本月暂无日程"))
            else:
                for s in month_schedules:
                    # 创建带有复选框的日程行
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(5, 5, 5, 5)
                    row_layout.setSpacing(10)
                    
                    # 复选框
                    checkbox = QCheckBox()
                    checkbox.setChecked(s.get("completed", False))
                    checkbox.stateChanged.connect(lambda state, s=s: self.toggle_schedule_completed(s))
                    row_layout.addWidget(checkbox)
                    
                    # 优先使用 start_time 和 end_time，没有时回退到旧 time 字段
                    display_time = s.get("start_time", "")
                    if display_time and s.get("end_time", ""):
                        display_time = f"{display_time}-{s['end_time']}"
                    elif not display_time:
                        display_time = s.get("time", "")
                    
                    # 获取标签文本
                    tag_id = s.get("tag", "normal")
                    importance = s.get("importance", 0)
                    urgency = s.get("urgency", 0)
                    
                    # 构建标签文本
                    tag_parts = []
                    
                    # 添加自定义标签
                    if tag_id != "normal":
                        tag_parts.append(tag_id)
                    
                    # 添加重要程度和紧急程度
                    if importance > 0 or urgency > 0:
                        tag_parts.append(f"重要:{importance} 紧急:{urgency}")
                    
                    # 如果没有标签，使用默认值
                    tag_text = "一般" if not tag_parts else " ".join(tag_parts)
                    
                    txt = f"{s['date']} {display_time} {s['content']} [标签: {tag_text}]"
                    
                    # 日程按钮
                    btn = ScheduleButton(txt, s)
                    if s["completed"]:
                        btn.setStyleSheet("text-align:left;border:none;text-decoration:line-through;color:#9ca3af;")
                    btn.clicked.connect(lambda checked, s=s: self.edit_schedule_direct(s))
                    # 设置长按事件处理
                    btn.on_long_press = lambda s=s: self.on_schedule_long_press(s)
                    
                    row_layout.addWidget(btn, 1)
                    self.schedule_list_layout.addWidget(row_widget)
        except Exception as e:
            print(f"Error in render_month: {e}")
            import traceback
            traceback.print_exc()

    def create_day_card(self, date):
        try:
            # 不使用缓存，避免widget已被删除的问题
            w = ClickableDateCard(date, self)
            
            # 检查是否是今天
            today = datetime.now().date()
            is_today = date.date() == today
            
            # 获取当前样式配置
            colors = self.current_style['colors']
            sizes = self.current_style['sizes']
            fonts = self.current_style['fonts']
            
            # 设置卡片样式，今天的卡片有特殊样式
            if is_today:
                w.setStyleSheet(f"background:{colors['today']};border-radius:{sizes['card_radius']}px;padding:{sizes['padding']}px;")
            else:
                w.setStyleSheet(f"background:{colors['card']};border-radius:{sizes['card_radius']}px;padding:{sizes['padding']}px;")
            
            lay = QVBoxLayout(w)
            lay.setContentsMargins(sizes['padding'], sizes['padding'], sizes['padding'], sizes['padding'])
            
            # 日期标签
            day_label = QLabel(str(date.day))
            day_label.setStyleSheet(f"font-size:{fonts['size']['medium']}px;font-weight:bold;")
            lay.addWidget(day_label)
            
            # 显示日程
            day_str = date.strftime("%Y-%m-%d")
            day_schedules = [s for s in self.schedules if s.get("date", "") == day_str and not (self.hide_completed and s.get("completed", False))]
            day_schedules = self.filter_schedules_by_tag(day_schedules)
            
            # 对日程进行排序
            day_schedules = self.sort_schedules(day_schedules)
            
            if day_schedules:
                for s in day_schedules[:3]:  # 最多显示3个日程
                    # 优先使用 start_time 和 end_time，没有时回退到旧 time 字段
                    display_time = s.get("start_time", "")
                    if display_time and s.get("end_time", ""):
                        display_time = f"{display_time}-{s['end_time']}"
                    elif not display_time:
                        display_time = s.get("time", "")
                    time_label = QLabel(f"• {display_time}")
                    time_label.setStyleSheet(f"font-size:{fonts['size']['small']}px;margin-top:2px;")
                    lay.addWidget(time_label)
                if len(day_schedules) > 3:
                    more_label = QLabel(f"... 还有 {len(day_schedules) - 3} 个")
                    more_label.setStyleSheet(f"font-size:{fonts['size']['small']}px;color:{colors['text_secondary']};")
                    lay.addWidget(more_label)
            else:
                empty_label = QLabel("暂无日程")
                empty_label.setStyleSheet(f"font-size:{fonts['size']['small']}px;color:{colors['text_secondary']};")
                lay.addWidget(empty_label)
            
            return w
        except Exception as e:
            print(f"Error in create_day_card: {e}")
            import traceback
            traceback.print_exc()
            # 返回一个简单的卡片作为 fallback
            w = QWidget()
            w.setStyleSheet("background:#1f2937;border-radius:8px;padding:8px;")
            lay = QVBoxLayout(w)
            lay.addWidget(QLabel(str(date.day)))
            lay.addWidget(QLabel("暂无日程"))
            return w

    def render_todo(self):
        self.title_label.setText("待办日程")
        self.week_bar.hide()
        
        # 确保所有待办日程都有 completed 字段
        for g in self.todo_schedules:
            if "completed" not in g:
                g["completed"] = False
            if "subtasks" not in g:
                g["subtasks"] = []
        
        # 左侧：简化显示
        general_widget = QWidget()
        general_lay = QVBoxLayout(general_widget)
        general_lay.addWidget(QLabel("📋 待办日程"))
        self.grid_layout.addWidget(general_widget, 0, 0)
        
        # 右侧：待办日程列表
        self.schedule_list_layout.addWidget(QLabel("📋 待办日程"))
        if not self.todo_schedules:
            self.schedule_list_layout.addWidget(QLabel("暂无待办日程"))
        else:
            for g in self.todo_schedules:
                box = TodoScheduleBox(g, self)
                self.schedule_list_layout.addWidget(box)

        # 添加待办日程
        add_layout = QVBoxLayout()
        
        # 内容输入框
        content_layout = QHBoxLayout()
        self.todo_content = QLineEdit()
        self.todo_content.setPlaceholderText("一句话新建待办日程（如：完成作业）")
        add_todo_btn = QPushButton("➕ 添加")
        add_todo_btn.setFixedWidth(80)
        add_todo_btn.clicked.connect(self.add_todo_schedule)
        add_todo_btn.setObjectName("blue")
        content_layout.addWidget(self.todo_content)
        content_layout.addWidget(add_todo_btn)
        add_layout.addLayout(content_layout)
        
        self.schedule_list_layout.addLayout(add_layout)
        self.todo_content.returnPressed.connect(self.add_todo_schedule)

    # ===================== 日程排序 =====================
    def sort_schedules(self, schedules):
        """
        对日程进行排序：
        1. 首先按起始时间排序
        2. 相同起始时间的，按添加时间排序
        """
        def get_sort_key(schedule):
            # 提取起始时间
            start_time = schedule.get("start_time", "")
            # 如果没有起始时间，使用空字符串，这样会排在后面
            time_key = start_time if start_time else "99:99"
            
            # 提取创建时间，用于二次排序
            created_at = schedule.get("created_at", 0)
            if not created_at and "id" in schedule:
                try:
                    # id 格式为 "timestamp + random"，提取开头的数字部分
                    id_str = schedule["id"]
                    # 找到第一个非数字字符的位置
                    split_index = 0
                    while split_index < len(id_str) and id_str[split_index].isdigit():
                        split_index += 1
                    if split_index > 0:
                        created_at = float(id_str[:split_index])
                except (ValueError, IndexError):
                    created_at = 0
            
            return (time_key, created_at)
        
        return sorted(schedules, key=get_sort_key)

    # ===================== AI 助手控制 =====================
    def toggle_ai_visibility(self):
        if self.ai_chat_widget.isVisible():
            self.ai_chat_widget.hide()
            self.ai_toggle_btn.setText("🤖 显示")
        else:
            self.ai_chat_widget.show()
            self.ai_toggle_btn.setText("🤖 隐藏")

    # ===================== 标签管理 =====================
    def open_tag_manager(self):
        dialog = TagManagerDialog(self)
        dialog.exec()
        self.render_calendar()

    # ===================== 基础功能 =====================
    def generate_id(self):
        return str(int(datetime.now().timestamp())) + str(os.urandom(2).hex())

    def add_schedule(self):
        dialog = ScheduleDialog(self, default_date=datetime.now().strftime("%Y-%m-%d"), tag_manager=self.tag_manager)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            current_time = datetime.now().timestamp()
            
            selected_date = data.get("date", "")
            
            if selected_date and selected_date.strip():
                self.schedules.append({
                    "id": self.generate_id(),
                    "content": data["content"],
                    "time": data["time"],
                    "start_time": data["start_time"],
                    "end_time": data["end_time"],
                    "date": selected_date,
                    "completed": False,
                    "tag": data["tag"],
                    "subtasks": data["subtasks"],
                    "created_at": current_time
                })
                Storage.save("schedules", self.schedules)
            else:
                self.todo_schedules.append({
                    "id": self.generate_id(),
                    "content": data["content"],
                    "time": data["time"],
                    "start_time": data["start_time"],
                    "end_time": data["end_time"],
                    "completed": False,
                    "tag": data["tag"],
                    "subtasks": data["subtasks"],
                    "created_at": current_time
                })
                Storage.save("todo", self.todo_schedules)
            
            self.render_calendar()

    def add_day_schedule(self):
        day_str = self.current_date.strftime("%Y-%m-%d")
        dialog = ScheduleDialog(self, default_date=day_str, tag_manager=self.tag_manager)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            current_time = datetime.now().timestamp()
            
            # 从对话框获取日期
            selected_date = data.get("date", "")
            
            # 检查是否有日期，没有则归档到待办日程
            if selected_date and selected_date.strip():
                # 有日期，添加到日程
                self.schedules.append({
                    "id": self.generate_id(),
                    "content": data["content"],
                    "time": data["time"],
                    "start_time": data["start_time"],
                    "end_time": data["end_time"],
                    "date": selected_date,
                    "completed": False,
                    "tag": data["tag"],
                    "subtasks": data["subtasks"],
                    "created_at": current_time
                })
                Storage.save("schedules", self.schedules)
            else:
                # 没有日期，归档到待办日程
                self.todo_schedules.append({
                    "id": self.generate_id(),
                    "content": data["content"],
                    "time": data["time"],
                    "start_time": data["start_time"],
                    "end_time": data["end_time"],
                    "completed": False,
                    "tag": data["tag"],
                    "subtasks": data["subtasks"],
                    "created_at": current_time
                })
                Storage.save("todo", self.todo_schedules)
            
            self.render_calendar()



    def add_todo_schedule(self):
        content = self.todo_content.text().strip()
        if not content:
            return
        
        # 先尝试解析时间
        parse_result = TimeParser.parse(content)
        parsed_start_time = parse_result['start_time']
        parsed_end_time = parse_result['end_time']
        cleaned_content = parse_result['remaining_text'].strip()
        
        initial_schedule = {
            "content": cleaned_content if cleaned_content else content,
            "time": "",
            "start_time": parsed_start_time if parsed_start_time else "",
            "end_time": parsed_end_time if parsed_end_time else ""
        }
        
        dialog = ScheduleDialog(self, schedule=initial_schedule, is_todo=True, tag_manager=self.tag_manager)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            current_time = datetime.now().timestamp()
            self.todo_schedules.append({
                "id": self.generate_id(),
                "content": data["content"],
                "time": data["time"],
                "start_time": data["start_time"],
                "end_time": data["end_time"],
                "tag": data["tag"],
                "subtasks": data["subtasks"],
                "completed": False,
                "created_at": current_time
            })
            Storage.save("todo", self.todo_schedules)
            self.todo_content.clear()
            self.render_calendar()



    def add_habit(self):
        content, ok = QInputDialog.getText(self, "添加习惯", "内容：")
        if not ok or not content:
            return
        time, ok = QInputDialog.getText(self, "时间", "如：08:00")
        self.habits.append({"id": self.generate_id(), "content": content, "time": time or ""})
        Storage.save("habits", self.habits)
        self.render_calendar()

    def import_data(self):
        # 选择导入方式
        options = ["从JSON导入", "从系统日历导入"]
        if not self.system_calendar.calendar_available:
            options = ["从JSON导入"]
        
        choice, ok = QInputDialog.getItem(self, "选择导入方式", "请选择导入方式：", options, 0, False)
        if not ok:
            return
        
        if choice == "从JSON导入":
            text, ok = QInputDialog.getMultiLineText(self, "导入", "粘贴JSON数据：")
            if not ok or not text:
                return
            try:
                import json
                data = json.loads(text)
                # 确保导入的数据包含所有必要的字段
                current_time = datetime.now().timestamp()
                for item in data:
                    if "id" not in item:
                        item["id"] = self.generate_id()
                    if "tag" not in item:
                        item["tag"] = "normal"
                    if "subtasks" not in item:
                        item["subtasks"] = []
                    if "completed" not in item:
                        item["completed"] = False
                    if "time" not in item:
                        item["time"] = ""
                    if "start_time" not in item:
                        item["start_time"] = ""
                    if "end_time" not in item:
                        item["end_time"] = ""
                    if "created_at" not in item:
                        item["created_at"] = current_time
                    # 确保子任务也有必要的字段
                    for subtask in item.get("subtasks", []):
                        if "id" not in subtask:
                            subtask["id"] = self.generate_id()
                        if "completed" not in subtask:
                            subtask["completed"] = False
                self.schedules.extend(data)
                Storage.save("schedules", self.schedules)
                QMessageBox.information(self, "成功", "导入完成！")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"JSON格式错误：{str(e)}")
        elif choice == "从系统日历导入":
            try:
                events = self.system_calendar.import_events()
                if events:
                    # 确保导入的事件包含所有必要的字段
                    current_time = datetime.now().timestamp()
                    for event in events:
                        if "id" not in event:
                            event["id"] = self.generate_id()
                        if "tag" not in event:
                            event["tag"] = "normal"
                        if "subtasks" not in event:
                            event["subtasks"] = []
                        if "completed" not in event:
                            event["completed"] = False
                        if "time" not in event:
                            event["time"] = ""
                        if "start_time" not in event:
                            event["start_time"] = ""
                        if "end_time" not in event:
                            event["end_time"] = ""
                        if "created_at" not in event:
                            event["created_at"] = current_time
                    self.schedules.extend(events)
                    Storage.save("schedules", self.schedules)
                    QMessageBox.information(self, "成功", f"从系统日历导入了 {len(events)} 个事件！")
                else:
                    QMessageBox.information(self, "提示", "系统日历中没有事件，或导入失败")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"系统日历导入错误：{str(e)}")

    def export_data(self):
        # 选择导出方式
        options = ["导出为JSON", "导出到系统日历"]
        if not self.system_calendar.calendar_available:
            options = ["导出为JSON"]
        
        choice, ok = QInputDialog.getItem(self, "选择导出方式", "请选择导出方式：", options, 0, False)
        if not ok:
            return
        
        if choice == "导出为JSON":
            # 确保导出的数据包含所有必要的字段
            export_data = []
            for item in self.schedules:
                export_item = {
                    "id": item.get("id", ""),
                    "content": item.get("content", ""),
                    "time": item.get("time", ""),
                    "start_time": item.get("start_time", ""),
                    "end_time": item.get("end_time", ""),
                    "date": item.get("date", ""),
                    "completed": item.get("completed", False),
                    "tag": item.get("tag", "normal"),
                    "subtasks": item.get("subtasks", [])
                }
                export_data.append(export_item)
            import json
            text = json.dumps(export_data, ensure_ascii=False, indent=2)
            file, _ = QFileDialog.getSaveFileName(self, "导出", f"日程_{datetime.now().strftime('%Y%m%d')}.json", "JSON Files (*.json)")
            if file:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "成功", "导出完成！")
        elif choice == "导出到系统日历":
            try:
                # 只导出未完成的事件
                events_to_export = [s for s in self.schedules if not s.get("completed", False)]
                if events_to_export:
                    success = self.system_calendar.export_events(events_to_export)
                    if success:
                        QMessageBox.information(self, "成功", f"成功导出 {len(events_to_export)} 个事件到系统日历！")
                    else:
                        QMessageBox.warning(self, "失败", "导出到系统日历失败")
                else:
                    QMessageBox.information(self, "提示", "没有未完成的事件可导出")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"系统日历导出错误：{str(e)}")

    def open_recycle_bin(self):
        if not self.recycle_bin:
            QMessageBox.information(self, "回收站", "空")
            return
        
        # 显示回收站内容和操作选项
        options = ["查看所有", "恢复全部", "恢复单个", "清空"]
        act, ok = QInputDialog.getItem(self, "回收站", f"回收站中有 {len(self.recycle_bin)} 个已删除日程", options, 0, False)
        if not ok:
            return
        
        if act == "查看所有":
            # 格式化显示回收站内容
            def get_display_time(item):
                display_time = item.get("start_time", "")
                if display_time and item.get("end_time", ""):
                    display_time = f"{display_time}-{item['end_time']}"
                elif not display_time:
                    display_time = item.get("time", "")
                return display_time
            content = "\n".join([f"{i+1}. {get_display_time(item)} {item['content']} [标签: {item.get('tag', 'normal')}]" for i, item in enumerate(self.recycle_bin)])
            QMessageBox.information(self, "回收站内容", content)
        
        elif act == "恢复全部":
            if QMessageBox.question(self, "确认", "确定要恢复所有已删除的日程吗？") == QMessageBox.StandardButton.Yes:
                self.schedules.extend(self.recycle_bin)
                self.recycle_bin = []
                Storage.save("schedules", self.schedules)
                Storage.save("recycle_bin", self.recycle_bin)
                QMessageBox.information(self, "成功", "所有日程已恢复")
                self.render_calendar()
        
        elif act == "恢复单个":
            # 让用户选择要恢复的日程
            def get_display_time(item):
                display_time = item.get("start_time", "")
                if display_time and item.get("end_time", ""):
                    display_time = f"{display_time}-{item['end_time']}"
                elif not display_time:
                    display_time = item.get("time", "")
                return display_time
            recycle_list = [f"{i+1}. {get_display_time(item)} {item['content']} [标签: {item.get('tag', 'normal')}]" for i, item in enumerate(self.recycle_bin)]
            selected, ok = QInputDialog.getItem(self, "恢复单个日程", "选择要恢复的日程：", recycle_list, 0, False)
            if ok:
                selected_index = recycle_list.index(selected)
                restored_item = self.recycle_bin.pop(selected_index)
                self.schedules.append(restored_item)
                Storage.save("schedules", self.schedules)
                Storage.save("recycle_bin", self.recycle_bin)
                QMessageBox.information(self, "成功", "日程已恢复")
                self.render_calendar()
        
        elif act == "清空":
            if QMessageBox.question(self, "确认", "确定要清空回收站吗？此操作不可恢复。") == QMessageBox.StandardButton.Yes:
                self.recycle_bin = []
                Storage.save("recycle_bin", self.recycle_bin)
                QMessageBox.information(self, "成功", "回收站已清空")

    def clear_all(self):
        if QMessageBox.question(self, "确认", "清空所有日程？") == QMessageBox.StandardButton.Yes:
            self.recycle_bin.extend(self.schedules)
            self.schedules = []
            Storage.save("schedules", self.schedules)
            Storage.save("recycle_bin", self.recycle_bin)
            self.render_calendar()

    def execute_ai_command(self, cmd, user_prompt=None):
        """执行 AI 返回的命令"""
        try:
            if cmd["type"] == "add":
                data = cmd["data"]
                current_time = datetime.now().timestamp()
                
                # 使用用户原始输入进行日期和时间解析
                parse_text = user_prompt if user_prompt else data.get("content", "")
                parse_result = TimeParser.parse(parse_text)
                parsed_start_time = parse_result['start_time']
                parsed_end_time = parse_result['end_time']
                parsed_date = parse_result['date']
                
                # 解析内容部分（优先使用 AI 返回的 content）
                content = data.get("content", "")
                content_parse_result = TimeParser.parse(content)
                cleaned_content = content_parse_result['remaining_text'].strip()
                
                # 优先使用解析到的日期和时间
                final_date = parsed_date
                final_start_time = parsed_start_time if parsed_start_time else data.get("start_time", "")
                final_end_time = parsed_end_time if parsed_end_time else data.get("end_time", "")
                
                # 处理子任务
                subtasks = data.get("subtasks", [])
                formatted_subtasks = []
                for subtask in subtasks:
                    formatted_subtasks.append({
                        "id": self.generate_id(),
                        "content": subtask.get("content", ""),
                        "completed": False
                    })
                
                # 检查是否有日期，没有则归档到待办日程
                if final_date and final_date.strip():
                    # 有日期，添加到日程
                    self.schedules.append({
                        "id": self.generate_id(),
                        "content": cleaned_content if cleaned_content else content,
                        "time": data.get("time", ""),
                        "start_time": final_start_time,
                        "end_time": final_end_time,
                        "date": final_date,
                        "completed": False,
                        "tag": data.get("tag", "normal"),
                        "subtasks": formatted_subtasks,
                        "created_at": current_time
                    })
                    Storage.save("schedules", self.schedules)
                else:
                    # 没有日期，归档到待办日程
                    self.todo_schedules.append({
                        "id": self.generate_id(),
                        "content": cleaned_content if cleaned_content else content,
                        "time": data.get("time", ""),
                        "start_time": final_start_time,
                        "end_time": final_end_time,
                        "completed": False,
                        "tag": data.get("tag", "normal"),
                        "subtasks": formatted_subtasks,
                        "created_at": current_time
                    })
                    Storage.save("todo", self.todo_schedules)
            
            elif cmd["type"] == "delete":
                if "id" in cmd:
                    # 按 ID 删除
                    self.recycle_bin.extend([s for s in self.schedules if s["id"] == cmd["id"]])
                    self.schedules = [s for s in self.schedules if s["id"] != cmd["id"]]
                elif "keyword" in cmd:
                    # 按关键词删除
                    self.recycle_bin.extend([s for s in self.schedules if cmd["keyword"] in s["content"]])
                    self.schedules = [s for s in self.schedules if cmd["keyword"] not in s["content"]]
                Storage.save("schedules", self.schedules)
                Storage.save("recycle_bin", self.recycle_bin)
            
            elif cmd["type"] == "complete":
                if "id" in cmd:
                    # 按 ID 标记完成
                    for s in self.schedules:
                        if s["id"] == cmd["id"]:
                            s["completed"] = True
                else:
                    # 标记所有完成
                    for s in self.schedules:
                        s["completed"] = True
                Storage.save("schedules", self.schedules)
            
            elif cmd["type"] == "clear":
                # 清空所有日程
                self.recycle_bin.extend(self.schedules)
                self.schedules = []
                Storage.save("schedules", self.schedules)
                Storage.save("recycle_bin", self.recycle_bin)
            
            # 重新渲染日历
            self.render_calendar()
            
        except Exception as e:
            print(f"Error executing AI command: {e}")
            import traceback
            traceback.print_exc()

    def edit_schedule(self):
        # 显示所有日程供选择
        def get_display_time(item):
            display_time = item.get("start_time", "")
            if display_time and item.get("end_time", ""):
                display_time = f"{display_time}-{item['end_time']}"
            elif not display_time:
                display_time = item.get("time", "")
            return display_time
        schedule_list = [f"{get_display_time(s)} {s['content']} [标签: {s.get('tag', 'normal')}]" for s in self.schedules]
        if not schedule_list:
            QMessageBox.warning(self, "提示", "暂无日程可编辑")
            return
        
        selected, ok = QInputDialog.getItem(self, "编辑日程", "选择要编辑的日程：", schedule_list, 0, False)
        if not ok:
            return
        
        # 找到选中的日程
        selected_index = schedule_list.index(selected)
        schedule = self.schedules[selected_index]
        self.edit_schedule_direct(schedule)

    def toggle_schedule_completed(self, schedule):
        """切换日程完成状态"""
        schedule["completed"] = not schedule.get("completed", False)
        Storage.save("schedules", self.schedules)
        self.render_calendar()
    
    def delete_schedule_direct(self, schedule):
        if QMessageBox.question(self, "确认", "确定要删除这条日程吗？") == QMessageBox.StandardButton.Yes:
            self.recycle_bin.append(schedule)
            self.schedules = [s for s in self.schedules if s["id"] != schedule["id"]]
            Storage.save("schedules", self.schedules)
            Storage.save("recycle_bin", self.recycle_bin)
            self.render_calendar()
            QMessageBox.information(self, "成功", "日程已删除！")
    
    def on_table_cell_double_clicked(self, row, column, table):
        item = table.item(row, 1)
        if item:
            schedule = item.data(Qt.ItemDataRole.UserRole)
            if schedule:
                self.edit_schedule_direct(schedule)
    
    def edit_schedule_direct(self, schedule):
        dialog = ScheduleDialog(self, schedule=schedule, is_edit=True, tag_manager=self.tag_manager)
        result = dialog.exec()
        if result == 2:
            # 删除
            self.recycle_bin.append(schedule)
            self.schedules = [s for s in self.schedules if s["id"] != schedule["id"]]
            Storage.save("schedules", self.schedules)
            Storage.save("recycle_bin", self.recycle_bin)
            self.render_calendar()
            QMessageBox.information(self, "成功", "日程已删除！")
            return
        elif result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            new_date = data.get("date", "")
            
            schedule["content"] = data["content"]
            schedule["time"] = data["time"]
            schedule["start_time"] = data["start_time"]
            schedule["end_time"] = data["end_time"]
            schedule["tag"] = data["tag"]
            schedule["subtasks"] = data["subtasks"]
            schedule["date"] = new_date
            
            if new_date and new_date.strip():
                Storage.save("schedules", self.schedules)
            else:
                self.schedules = [s for s in self.schedules if s["id"] != schedule["id"]]
                self.todo_schedules.append(schedule)
                Storage.save("schedules", self.schedules)
                Storage.save("todo", self.todo_schedules)
            
            self.render_calendar()
            QMessageBox.information(self, "成功", "日程编辑完成！")

    def edit_todo_schedule_direct(self, schedule):
        dialog = ScheduleDialog(self, schedule=schedule, is_todo=True, is_edit=True)
        result = dialog.exec()
        if result == 2:
            # 删除
            self.todo_schedules = [s for s in self.todo_schedules if s["id"] != schedule["id"]]
            Storage.save("todo", self.todo_schedules)
            self.render_calendar()
            QMessageBox.information(self, "成功", "待办日程已删除！")
            return
        elif result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            new_date = data.get("date", "")
            
            schedule["content"] = data["content"]
            schedule["time"] = data["time"]
            schedule["start_time"] = data["start_time"]
            schedule["end_time"] = data["end_time"]
            schedule["tag"] = data["tag"]
            schedule["subtasks"] = data["subtasks"]
            schedule["date"] = new_date
            
            if new_date and new_date.strip():
                self.todo_schedules = [s for s in self.todo_schedules if s["id"] != schedule["id"]]
                self.schedules.append(schedule)
                Storage.save("todo", self.todo_schedules)
                Storage.save("schedules", self.schedules)
            else:
                Storage.save("todo", self.todo_schedules)
            
            self.render_calendar()
            QMessageBox.information(self, "成功", "待办日程编辑完成！")

    # ===================== 拖拽功能 =====================
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    # ===================== 设置对话框 =====================
    def open_settings_dialog(self):
        from src.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self, self.current_style)
        dialog.exec()
    
    # ===================== 长按事件处理 =====================
    def on_schedule_long_press(self, schedule):
        # 长按事件处理：显示日程详情和快捷操作
        tag_map = {"normal": "一般", "important": "重要", "urgent": "紧急", "important_urgent": "重要且紧急"}
        tag_text = tag_map.get(schedule.get("tag", "normal"), "一般")
        
        # 构建详情文本
        details = f"内容: {schedule['content']}\n"
        details += f"时间: {schedule['time']}\n"
        if schedule.get("start_time"):
            details += f"开始时间: {schedule['start_time']}\n"
        if schedule.get("end_time"):
            details += f"结束时间: {schedule['end_time']}\n"
        details += f"日期: {schedule['date']}\n"
        details += f"标签: {tag_text}\n"
        details += f"状态: {'已完成' if schedule['completed'] else '未完成'}\n"
        
        # 添加子任务信息
        subtasks = schedule.get("subtasks", [])
        if subtasks:
            details += "\n子任务:\n"
            for i, subtask in enumerate(subtasks):
                details += f"  {i+1}. {'✅' if subtask.get('completed', False) else '◽'} {subtask['content']}\n"
        
        # 显示详情对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("日程详情")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(details))
        
        # 添加快捷操作按钮
        btn_layout = QHBoxLayout()
        toggle_btn = QPushButton("切换完成状态")
        delete_btn = QPushButton("删除")
        cancel_btn = QPushButton("取消")
        
        def toggle_completed():
            schedule["completed"] = not schedule["completed"]
            Storage.save("schedules", self.schedules)
            self.render_calendar()
            dialog.accept()
        
        def delete_schedule():
            if QMessageBox.question(self, "确认删除", "确定要删除此日程吗？", 
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.recycle_bin.append(schedule)
                self.schedules = [s for s in self.schedules if s["id"] != schedule["id"]]
                Storage.save("schedules", self.schedules)
                Storage.save("recycle_bin", self.recycle_bin)
                self.render_calendar()
                dialog.accept()
        
        toggle_btn.clicked.connect(toggle_completed)
        delete_btn.clicked.connect(delete_schedule)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(toggle_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def on_todo_schedule_long_press(self, schedule):
        # 长按事件处理：显示待办日程详情和快捷操作
        tag_map = {"normal": "一般", "important": "重要", "urgent": "紧急", "important_urgent": "重要且紧急"}
        tag_text = tag_map.get(schedule.get("tag", "normal"), "一般")
        
        # 构建详情文本
        details = f"内容: {schedule['content']}\n"
        details += f"时间: {schedule['time']}\n"
        if schedule.get("start_time"):
            details += f"开始时间: {schedule['start_time']}\n"
        if schedule.get("end_time"):
            details += f"结束时间: {schedule['end_time']}\n"
        details += f"标签: {tag_text}\n"
        details += f"状态: {'已完成' if schedule.get('completed', False) else '未完成'}\n"
        
        # 添加子任务信息
        subtasks = schedule.get("subtasks", [])
        if subtasks:
            details += "\n子任务:\n"
            for i, subtask in enumerate(subtasks):
                details += f"  {i+1}. {'✅' if subtask.get('completed', False) else '◽'} {subtask['content']}\n"
        
        # 显示详情对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("待办日程详情")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(details))
        
        # 添加快捷操作按钮
        btn_layout = QHBoxLayout()
        toggle_btn = QPushButton("切换完成状态")
        delete_btn = QPushButton("删除")
        cancel_btn = QPushButton("取消")
        
        def toggle_completed():
            schedule["completed"] = not schedule.get("completed", False)
            Storage.save("todo", self.todo_schedules)
            self.render_calendar()
            dialog.accept()
        
        def delete_schedule():
            if QMessageBox.question(self, "确认删除", "确定要删除此待办日程吗？", 
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.todo_schedules = [s for s in self.todo_schedules if s["id"] != schedule["id"]]
                Storage.save("todo", self.todo_schedules)
                self.render_calendar()
                dialog.accept()
        
        toggle_btn.clicked.connect(toggle_completed)
        delete_btn.clicked.connect(delete_schedule)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(toggle_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    # ===================== 样式管理 =====================
    def load_preset_style(self, preset_name):
        """加载预设样式"""
        if preset_name in PRESET_STYLES:
            self.current_style = PRESET_STYLES[preset_name].copy()
            self.update_style_controls()
            self.apply_style()
            self.render_calendar()
    
    def show_color_dialog(self, color_key):
        """显示颜色选择对话框"""
        color = QColorDialog.getColor(QColor(self.current_style['colors'][color_key]), self, f"选择{color_key}颜色")
        if color.isValid():
            self.current_style['colors'][color_key] = color.name()
            self.color_pickers[color_key].setStyleSheet(f"background:{color.name()};")
            self.apply_style()
            self.render_calendar()
    
    def update_font_family(self, family):
        """更新字体家族"""
        self.current_style['fonts']['family'] = family
        self.apply_style()
        self.render_calendar()
    
    def update_font_size(self, size):
        """更新字体大小"""
        self.current_style['fonts']['size']['normal'] = size
        # 调整其他字体大小比例
        self.current_style['fonts']['size']['small'] = int(size * 0.8)
        self.current_style['fonts']['size']['medium'] = int(size * 1.2)
        self.current_style['fonts']['size']['large'] = int(size * 1.4)
        self.current_style['fonts']['size']['xlarge'] = int(size * 1.6)
        self.apply_style()
        self.render_calendar()
    
    def update_card_radius(self, radius):
        """更新卡片圆角"""
        self.current_style['sizes']['card_radius'] = radius
        self.apply_style()
        self.render_calendar()
    
    def update_button_radius(self, radius):
        """更新按钮圆角"""
        self.current_style['sizes']['button_radius'] = radius
        self.apply_style()
        self.render_calendar()
    
    def update_padding(self, padding):
        """更新内边距"""
        self.current_style['sizes']['padding'] = padding
        self.apply_style()
        self.render_calendar()
    
    def update_style_controls(self):
        """更新样式控制面板的值"""
        # 更新颜色选择器
        for key, picker in self.color_pickers.items():
            picker.setStyleSheet(f"background:{self.current_style['colors'][key]};")
        
        # 更新字体设置
        self.font_family.setCurrentText(self.current_style['fonts']['family'])
        self.font_size.setValue(self.current_style['fonts']['size']['normal'])
        
        # 更新大小设置
        self.card_radius.setValue(self.current_style['sizes']['card_radius'])
        self.button_radius.setValue(self.current_style['sizes']['button_radius'])
        self.padding.setValue(self.current_style['sizes']['padding'])
    
    def load_api_config(self):
        """加载 API Key 和模型配置"""
        api_key, model = Storage.load_config()
        if api_key:
            self.api_key.setText(api_key)
        if model and model in MODEL_LIST:
            index = MODEL_LIST.index(model)
            self.model_select.setCurrentIndex(index)
    
    def save_api_config(self):
        """保存 API Key 和模型配置"""
        api_key = self.api_key.text().strip()
        model = self.model_select.currentText()
        Storage.save_config(api_key, model)
    
    def save_style(self):
        """保存样式配置"""
        Storage.save("style", self.current_style)
        QMessageBox.information(self, "成功", "样式已保存！")
    
    def closeEvent(self, event):
        """窗口关闭事件，清理资源"""
        try:
            widget_manager.cleanup_all()
        except:
            pass
        event.accept()
