# 界面对话框模块
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
from src.tag_manager import TagManager


class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None, is_todo=False, is_edit=False, default_date=None, tag_manager=None):
        super().__init__(parent)
        self.schedule = schedule
        self.is_todo = is_todo
        self.is_edit = is_edit
        self.default_date = default_date
        self.tag_manager = tag_manager if tag_manager else TagManager()
        self.setWindowTitle("编辑日程" if is_edit else "添加日程")
        self.setMinimumWidth(450)
        self.init_ui()
        self.apply_dark_style()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        colors = self.parent().current_style['colors'] if hasattr(self.parent(), 'current_style') else None
        
        title = QLabel("📅 日程信息")
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText("输入日程内容")
        if self.schedule and self.schedule.get("content", ""):
            self.content_edit.setText(self.schedule["content"])
        form_layout.addRow("内容：", self.content_edit)
        
        self.date_checkbox = QCheckBox("设置日期")
        self.date_checkbox.setChecked(True)
        self.date_checkbox.stateChanged.connect(self.on_date_checkbox_changed)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setStyleSheet("min-width:150px;")
        if self.schedule and self.schedule.get("date", ""):
            self.date_edit.setDate(QDate.fromString(self.schedule["date"], "yyyy-MM-dd"))
            self.date_checkbox.setChecked(True)
        elif self.schedule and not self.schedule.get("date", ""):
            self.date_edit.setDate(QDate.currentDate())
            self.date_checkbox.setChecked(False)
        elif self.default_date:
            self.date_edit.setDate(QDate.fromString(self.default_date, "yyyy-MM-dd"))
            self.date_checkbox.setChecked(True)
        else:
            self.date_edit.setDate(QDate.currentDate())
            self.date_checkbox.setChecked(True)
        
        self.date_edit.setEnabled(self.date_checkbox.isChecked())
        
        form_layout.addRow(self.date_checkbox)
        form_layout.addRow("日期：", self.date_edit)
        
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("时间描述（可选，如：下午3点）")
        if self.schedule and self.schedule.get("time", ""):
            self.time_edit.setText(self.schedule["time"])
        form_layout.addRow("时间描述：", self.time_edit)
        
        time_input_layout = QHBoxLayout()
        self.start_time_edit = QLineEdit()
        self.start_time_edit.setPlaceholderText("如：09:00")
        if self.schedule and self.schedule.get("start_time", ""):
            self.start_time_edit.setText(self.schedule["start_time"])
        self.end_time_edit = QLineEdit()
        self.end_time_edit.setPlaceholderText("如：18:00")
        if self.schedule and self.schedule.get("end_time", ""):
            self.end_time_edit.setText(self.schedule["end_time"])
        time_input_layout.addWidget(QLabel("起始时间："))
        time_input_layout.addWidget(self.start_time_edit)
        time_input_layout.addWidget(QLabel("截止时间："))
        time_input_layout.addWidget(self.end_time_edit)
        form_layout.addRow("时间范围：", time_input_layout)
        
        # 重要程度滑动条
        importance_layout = QHBoxLayout()
        self.importance_slider = QSlider(Qt.Orientation.Horizontal)
        self.importance_slider.setRange(0, 100)
        self.importance_slider.setTickInterval(10)
        self.importance_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.importance_label = QLabel("0")
        self.importance_slider.valueChanged.connect(lambda value: self.importance_label.setText(str(value)))
        importance_layout.addWidget(self.importance_slider)
        importance_layout.addWidget(self.importance_label)
        form_layout.addRow("重要程度：", importance_layout)
        
        # 紧急程度滑动条
        urgency_layout = QHBoxLayout()
        self.urgency_slider = QSlider(Qt.Orientation.Horizontal)
        self.urgency_slider.setRange(0, 100)
        self.urgency_slider.setTickInterval(10)
        self.urgency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.urgency_label = QLabel("0")
        self.urgency_slider.valueChanged.connect(lambda value: self.urgency_label.setText(str(value)))
        urgency_layout.addWidget(self.urgency_slider)
        urgency_layout.addWidget(self.urgency_label)
        form_layout.addRow("紧急程度：", urgency_layout)
        
        # 自定义标签输入框
        self.custom_tag_edit = QLineEdit()
        self.custom_tag_edit.setPlaceholderText("输入自定义标签（可选）")
        form_layout.addRow("自定义标签：", self.custom_tag_edit)
        
        # 初始化滑动条值
        if self.schedule:
            # 优先从日程属性中读取重要程度和紧急程度
            importance = self.schedule.get("importance", 0)
            urgency = self.schedule.get("urgency", 0)
            self.importance_slider.setValue(importance)
            self.urgency_slider.setValue(urgency)
            
            # 读取自定义标签
            tag_id = self.schedule.get("tag", "normal")
            if tag_id != "normal" and "_" not in tag_id:
                self.custom_tag_edit.setText(tag_id)
        else:
            # 默认值
            self.importance_slider.setValue(0)
            self.urgency_slider.setValue(0)
        
        layout.addLayout(form_layout)
        
        subtask_group = QGroupBox("子任务")
        subtask_layout = QVBoxLayout(subtask_group)
        self.subtasks_list = QListWidget()
        subtask_layout.addWidget(self.subtasks_list)
        
        subtask_input_layout = QHBoxLayout()
        self.subtask_edit = QLineEdit()
        self.subtask_edit.setPlaceholderText("输入子任务内容")
        add_subtask_btn = QPushButton("+ 添加")
        add_subtask_btn.clicked.connect(self.add_subtask)
        subtask_input_layout.addWidget(self.subtask_edit)
        subtask_input_layout.addWidget(add_subtask_btn)
        subtask_layout.addLayout(subtask_input_layout)
        
        layout.addWidget(subtask_group)
        
        if self.schedule and self.schedule.get("subtasks", []):
            for subtask in self.schedule["subtasks"]:
                item = QListWidgetItem(subtask["content"])
                item.setData(Qt.ItemDataRole.UserRole, subtask)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked if subtask.get("completed", False) else Qt.CheckState.Unchecked)
                self.subtasks_list.addItem(item)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        if self.is_edit:
            delete_btn = QPushButton("删除")
            delete_btn.setObjectName("red")
            delete_btn.clicked.connect(self.delete_schedule)
            btn_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("blue")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
    
    def apply_dark_style(self):
        self.setStyleSheet("""
            QDialog { background:#111827; }
            QLabel { color:#e5e7eb; }
            QLineEdit, QComboBox, QListWidget, QDateEdit {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px; color:#e5e7eb;
            }
            QPushButton {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px 16px; color:#e5e7eb;
            }
            QPushButton:hover { background:#374151; }
            QPushButton#blue { background:#2563eb; color:white; }
            QPushButton#blue:hover { background:#1d4ed8; }
            QPushButton#red { background:#dc2626; color:white; }
            QPushButton#red:hover { background:#b91c1c; }
            QGroupBox {
                color:#e5e7eb; border:1px solid #374151;
                border-radius:6px; margin-top:12px; padding-top:12px;
            }
            QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 5px; }
        """)
    
    def on_date_checkbox_changed(self):
        self.date_edit.setEnabled(self.date_checkbox.isChecked())
    
    def add_subtask(self):
        content = self.subtask_edit.text().strip()
        if content:
            item = QListWidgetItem(content)
            item.setData(Qt.ItemDataRole.UserRole, {"id": str(int(datetime.now().timestamp())) + str(os.urandom(2).hex()), "content": content, "completed": False})
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.subtasks_list.addItem(item)
            self.subtask_edit.clear()
    
    def delete_schedule(self):
        self.done(2)
    
    def get_data(self):
        subtasks = []
        for i in range(self.subtasks_list.count()):
            item = self.subtasks_list.item(i)
            subtask_data = item.data(Qt.ItemDataRole.UserRole)
            subtasks.append({
                "id": subtask_data["id"] if subtask_data else str(int(datetime.now().timestamp())) + str(os.urandom(2).hex()),
                "content": item.text(),
                "completed": item.checkState() == Qt.CheckState.Checked
            })
        
        # 从滑动条获取重要程度和紧急程度
        importance = self.importance_slider.value()
        urgency = self.urgency_slider.value()
        
        # 获取自定义标签
        custom_tag = self.custom_tag_edit.text().strip()
        
        # 标签ID
        tag_id = custom_tag if custom_tag else "normal"
        
        date_value = self.date_edit.date().toString("yyyy-MM-dd") if self.date_checkbox.isChecked() else ""
        
        return {
            "content": self.content_edit.text().strip(),
            "time": self.time_edit.text().strip(),
            "start_time": self.start_time_edit.text().strip(),
            "end_time": self.end_time_edit.text().strip(),
            "tag": tag_id,
            "importance": importance,
            "urgency": urgency,
            "subtasks": subtasks,
            "date": date_value
        }


class TodoScheduleBox(QGroupBox):
    def __init__(self, schedule, parent_window, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.parent_window = parent_window
        self.tag_manager = TagManager()
        self.is_expanded = True
        self.init_ui()
    
    def init_ui(self):
        # 设置标题
        tag_id = self.schedule.get("tag", "normal")
        importance = self.schedule.get("importance", 0)
        urgency = self.schedule.get("urgency", 0)
        
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
        
        self.setTitle(f"📋 {self.schedule['content']} [{tag_text}]")
        self.setCheckable(True)
        self.setChecked(not self.schedule.get("completed", False))
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # 时间显示
        display_time = self.schedule.get("start_time", "")
        if display_time and self.schedule.get("end_time", ""):
            display_time = f"{display_time}-{self.schedule['end_time']}"
        elif not display_time:
            display_time = self.schedule.get("time", "")
        
        if display_time:
            time_label = QLabel(f"⏰ {display_time}")
            main_layout.addWidget(time_label)
        
        # 子任务部分
        self.subtasks_widget = QWidget()
        self.subtasks_layout = QVBoxLayout(self.subtasks_widget)
        self.subtasks_layout.setContentsMargins(0, 5, 0, 0)
        
        subtasks = self.schedule.get("subtasks", [])
        if subtasks:
            self.subtasks_layout.addWidget(QLabel("📋 子任务："))
            for subtask in subtasks:
                subtask_check = QCheckBox(subtask['content'])
                subtask_check.setChecked(subtask.get('completed', False))
                subtask_check.subtask = subtask
                subtask_check.schedule_box = self
                subtask_check.stateChanged.connect(lambda state, sb=self, st=subtask: self.on_subtask_toggled(state, st))
                self.subtasks_layout.addWidget(subtask_check)
        
        main_layout.addWidget(self.subtasks_widget)
        
        # 初始状态设置
        if self.schedule.get("completed", False):
            self.setStyleSheet("QGroupBox { color: #9ca3af; }")
        
        # 连接信号
        self.toggled.connect(self.on_toggled)
    
    def on_toggled(self, checked):
        self.schedule['completed'] = not checked
        if not checked:
            self.setStyleSheet("QGroupBox { color: #9ca3af; }")
        else:
            self.setStyleSheet("")
        Storage.save("todo", self.parent_window.todo_schedules)
    
    def on_subtask_toggled(self, state, subtask):
        subtask['completed'] = (state == Qt.CheckState.Checked.value)
        Storage.save("todo", self.parent_window.todo_schedules)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            # 检查是否点击在复选框区域
            if pos.x() > 20:
                self.is_expanded = not self.is_expanded
                self.subtasks_widget.setVisible(self.is_expanded)
                event.accept()
                return
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_window.edit_todo_schedule_direct(self.schedule)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class TagManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tag_manager = TagManager()
        self.setWindowTitle("标签管理")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.init_ui()
        self.apply_dark_style()
        self.refresh_tag_list()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🏷️ 标签管理")
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(title)
        
        info_label = QLabel("内置标签不可编辑和删除")
        info_label.setStyleSheet("color:#9ca3af;font-size:12px;")
        layout.addWidget(info_label)
        
        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet("""
            QListWidget {
                background:#1f2937;
                border:1px solid #374151;
                border-radius:6px;
                padding:8px;
            }
        """)
        layout.addWidget(self.tag_list)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.add_btn = QPushButton("+ 添加标签")
        self.add_btn.clicked.connect(self.add_tag)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.clicked.connect(self.edit_tag)
        btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.setObjectName("red")
        self.delete_btn.clicked.connect(self.delete_tag)
        btn_layout.addWidget(self.delete_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def apply_dark_style(self):
        self.setStyleSheet("""
            QDialog { background:#111827; }
            QLabel { color:#e5e7eb; }
            QListWidget {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px; color:#e5e7eb;
            }
            QPushButton {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px 16px; color:#e5e7eb;
            }
            QPushButton:hover { background:#374151; }
            QPushButton#red { background:#dc2626; color:white; }
            QPushButton#red:hover { background:#b91c1c; }
            QLineEdit {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px; color:#e5e7eb;
            }
        """)
    
    def refresh_tag_list(self):
        self.tag_list.clear()
        self.tag_manager.load_tags()
        
        for tag in self.tag_manager.get_all_tags():
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, tag)
            
            label = QWidget()
            label_layout = QHBoxLayout(label)
            label_layout.setContentsMargins(8, 4, 8, 4)
            
            color_label = QLabel()
            color_label.setFixedSize(16, 16)
            color_label.setStyleSheet(f"background-color:{tag.color};border-radius:8px;")
            label_layout.addWidget(color_label)
            
            name_label = QLabel(tag.name)
            label_layout.addWidget(name_label)
            
            if tag.is_builtin:
                builtin_label = QLabel("(内置)")
                builtin_label.setStyleSheet("color:#9ca3af;font-size:12px;")
                label_layout.addWidget(builtin_label)
            
            label_layout.addStretch()
            
            self.tag_list.addItem(item)
            self.tag_list.setItemWidget(item, label)
        
        self.update_button_states()
    
    def update_button_states(self):
        current_item = self.tag_list.currentItem()
        if current_item:
            tag = current_item.data(Qt.ItemDataRole.UserRole)
            is_builtin = tag.is_builtin
            self.edit_btn.setEnabled(not is_builtin)
            self.delete_btn.setEnabled(not is_builtin)
        else:
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def add_tag(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加标签")
        dialog.setMinimumWidth(400)
        dialog_layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("输入标签名称")
        form_layout.addRow("标签名称：", name_edit)
        
        color_edit = QLineEdit()
        color_edit.setPlaceholderText("#RRGGBB (可选)")
        form_layout.addRow("颜色：", color_edit)
        
        dialog_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("blue")
        btn_layout.addWidget(ok_btn)
        
        dialog_layout.addLayout(btn_layout)
        
        dialog.setStyleSheet("""
            QDialog { background:#111827; }
            QLabel { color:#e5e7eb; }
            QLineEdit {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px; color:#e5e7eb;
            }
            QPushButton {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px 16px; color:#e5e7eb;
            }
            QPushButton:hover { background:#374151; }
            QPushButton#blue { background:#2563eb; color:white; }
            QPushButton#blue:hover { background:#1d4ed8; }
        """)
        
        def on_ok():
            name = name_edit.text().strip()
            color = color_edit.text().strip() or "#60a5fa"
            
            if not name:
                QMessageBox.warning(dialog, "提示", "请输入标签名称")
                return
            
            try:
                self.tag_manager.create_tag(name, color)
                self.refresh_tag_list()
                dialog.accept()
            except ValueError as e:
                QMessageBox.warning(dialog, "错误", str(e))
        
        ok_btn.clicked.connect(on_ok)
        dialog.exec()
    
    def edit_tag(self):
        current_item = self.tag_list.currentItem()
        if not current_item:
            return
        
        tag = current_item.data(Qt.ItemDataRole.UserRole)
        if tag.is_builtin:
            QMessageBox.warning(self, "提示", "不能编辑内置标签")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑标签")
        dialog.setMinimumWidth(400)
        dialog_layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        name_edit = QLineEdit(tag.name)
        form_layout.addRow("标签名称：", name_edit)
        
        color_edit = QLineEdit(tag.color or "")
        color_edit.setPlaceholderText("#RRGGBB (可选)")
        form_layout.addRow("颜色：", color_edit)
        
        dialog_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("blue")
        btn_layout.addWidget(ok_btn)
        
        dialog_layout.addLayout(btn_layout)
        
        dialog.setStyleSheet("""
            QDialog { background:#111827; }
            QLabel { color:#e5e7eb; }
            QLineEdit {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px; color:#e5e7eb;
            }
            QPushButton {
                background:#1f2937; border:1px solid #374151;
                border-radius:6px; padding:8px 16px; color:#e5e7eb;
            }
            QPushButton:hover { background:#374151; }
            QPushButton#blue { background:#2563eb; color:white; }
            QPushButton#blue:hover { background:#1d4ed8; }
        """)
        
        def on_ok():
            new_name = name_edit.text().strip()
            new_color = color_edit.text().strip()
            
            if not new_name:
                QMessageBox.warning(dialog, "提示", "请输入标签名称")
                return
            
            try:
                self.tag_manager.update_tag(tag.id, new_name, new_color if new_color else None)
                self.update_schedules_tag(tag.id, new_name=tag.name)
                self.refresh_tag_list()
                dialog.accept()
            except ValueError as e:
                QMessageBox.warning(dialog, "错误", str(e))
        
        ok_btn.clicked.connect(on_ok)
        dialog.exec()
    
    def delete_tag(self):
        current_item = self.tag_list.currentItem()
        if not current_item:
            return
        
        tag = current_item.data(Qt.ItemDataRole.UserRole)
        if tag.is_builtin:
            QMessageBox.warning(self, "提示", "不能删除内置标签")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除标签\"{tag.name}\"吗？相关日程的标签将重置为\"一般\"。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.update_schedules_tag(tag.id, reset_to_normal=True)
                self.tag_manager.delete_tag(tag.id)
                self.refresh_tag_list()
            except ValueError as e:
                QMessageBox.warning(self, "错误", str(e))
    
    def update_schedules_tag(self, old_tag_id, reset_to_normal=False, new_name=None):
        schedules = Storage.load("schedules", [])
        todo_schedules = Storage.load("todo", [])
        updated = False
        
        for schedule in schedules:
            if schedule.get("tag") == old_tag_id:
                if reset_to_normal:
                    schedule["tag"] = "normal"
                updated = True
        
        for todo_schedule in todo_schedules:
            if todo_schedule.get("tag") == old_tag_id:
                if reset_to_normal:
                    todo_schedule["tag"] = "normal"
                updated = True
        
        if updated:
            Storage.save("schedules", schedules)
            Storage.save("todo", todo_schedules)
