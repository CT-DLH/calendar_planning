# 界面组件模块
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


class AIChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.chat_history = []
        self.is_visible = True
        self.init_ui()
        self.apply_dark_style()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题栏
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("🤖 AI 助手")
        title_label.setStyleSheet("font-size:16px;font-weight:bold;")
        
        self.toggle_btn = QPushButton("−")
        self.toggle_btn.setFixedSize(25, 25)
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.toggle_btn)
        layout.addWidget(title_bar)
        
        # 对话历史区域
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll, 1)
        
        # 上下文选项
        options_group = QGroupBox("上下文选项")
        options_layout = QVBoxLayout(options_group)
        
        self.include_unfinished = QCheckBox("包含未完成日程")
        self.include_unfinished.setChecked(True)
        
        self.include_not_expired = QCheckBox("包含未到期日程")
        
        self.include_todo = QCheckBox("包含待办日程")
        
        self.include_completed = QCheckBox("包含已完成日程")
        
        self.execute_commands = QCheckBox("执行命令（修改日程）")
        
        options_layout.addWidget(self.include_unfinished)
        options_layout.addWidget(self.include_not_expired)
        options_layout.addWidget(self.include_todo)
        options_layout.addWidget(self.include_completed)
        options_layout.addWidget(self.execute_commands)
        
        layout.addWidget(options_group)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("输入消息...")
        self.input_edit.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("发送")
        self.send_btn.setObjectName("blue")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_edit, 1)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
    
    def toggle_visibility(self):
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.show()
            self.toggle_btn.setText("−")
        else:
            self.hide()
            self.toggle_btn.setText("+")
    
    def apply_dark_style(self):
        self.setStyleSheet("""
            QWidget { background:#111827; }
            QGroupBox { border:1px solid #374151; border-radius:8px; margin-top:12px; padding-top:10px; color:#e5e7eb; }
            QGroupBox::title { subcontrol-origin:margin; left:8px; padding:0 4px; }
            QCheckBox { color:#e5e7eb; }
            QPushButton { background:#374151; color:#e5e7eb; border:none; border-radius:6px; padding:8px 16px; }
            QPushButton:hover { background:#4b5563; }
            QPushButton#blue { background:#3b82f6; }
            QPushButton#blue:hover { background:#2563eb; }
            QLineEdit { background:#1f2937; color:#e5e7eb; border:1px solid #374151; border-radius:6px; padding:8px; }
            QScrollArea { border:none; }
        """)
    
    def send_message(self):
        content = self.input_edit.text().strip()
        if not content:
            return
        
        # 添加用户消息
        user_msg = QLabel(content)
        user_msg.setWordWrap(True)
        user_msg.setStyleSheet("background:#374151;color:#e5e7eb;padding:8px 12px;border-radius:8px;")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_msg)
        
        self.input_edit.clear()
        
        # 滚动到底部
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
        
        # 检查是否有父窗口引用
        if not self.parent_window:
            return
        
        # 获取上下文
        context = []
        now = datetime.now()
        
        if self.include_unfinished.isChecked():
            unfinished = [s for s in self.parent_window.schedules if not s.get("completed", False)]
            if unfinished:
                context.append("未完成日程：")
                for s in unfinished:
                    time_str = s.get("start_time", "")
                    if time_str and s.get("end_time", ""):
                        time_str = f"{time_str}-{s['end_time']}"
                    elif not time_str:
                        time_str = s.get("time", "")
                    context.append(f"- {s['date']} {time_str} {s['content']}")
        
        if self.include_todo.isChecked():
            if self.parent_window.todo_schedules:
                context.append("\n待办日程：")
                for s in self.parent_window.todo_schedules:
                    time_str = s.get("start_time", "")
                    if time_str and s.get("end_time", ""):
                        time_str = f"{time_str}-{s['end_time']}"
                    elif not time_str:
                        time_str = s.get("time", "")
                    context.append(f"- {time_str} {s['content']}")
        
        if self.include_completed.isChecked():
            completed = [s for s in self.parent_window.schedules if s.get("completed", False)]
            if completed:
                context.append("\n已完成日程：")
                for s in completed:
                    time_str = s.get("start_time", "")
                    if time_str and s.get("end_time", ""):
                        time_str = f"{time_str}-{s['end_time']}"
                    elif not time_str:
                        time_str = s.get("time", "")
                    context.append(f"- {s['date']} {time_str} {s['content']}")
        
        context_text = "\n".join(context) if context else "暂无日程"
        
        # 显示AI思考中
        thinking = QLabel("思考中...")
        thinking.setWordWrap(True)
        thinking.setStyleSheet("background:#1f2937;color:#e5e7eb;padding:8px 12px;border-radius:8px;")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, thinking)
        
        def process_ai():
            try:
                api_key = self.parent_window.api_key.text().strip()
                model = self.parent_window.model_select.currentText()
                
                # 判断是命令还是普通聊天
                is_command = self.execute_commands.isChecked()
                
                if is_command:
                    # 命令模式：构建完整的prompt并执行命令
                    full_prompt = content
                    if context_text:
                        full_prompt = f"当前日程上下文：\n{context_text}\n\n用户指令：{content}"
                    result = AIClient.run_command(api_key, model, full_prompt)
                    response = result.get("message", "完成")
                    if self.execute_commands.isChecked():
                        self.parent_window.execute_ai_command(result, content)
                else:
                    # 对话模式：普通聊天
                    full_prompt = content
                    if context_text:
                        full_prompt = f"当前日程上下文：\n{context_text}\n\n用户问题：{content}"
                    response = AIClient.get_suggestion(api_key, model, [], full_prompt)
                
                # 替换思考消息
                ai_msg = QLabel(response)
                ai_msg.setWordWrap(True)
                ai_msg.setStyleSheet("background:#1f2937;color:#e5e7eb;padding:8px 12px;border-radius:8px;")
                index = self.chat_layout.indexOf(thinking)
                self.chat_layout.replaceWidget(thinking, ai_msg)
                thinking.deleteLater()
                
                QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
                    self.chat_scroll.verticalScrollBar().maximum()
                ))
                
            except Exception as e:
                thinking.setText(f"错误：{str(e)}")
        
        QTimer.singleShot(100, process_ai)


class ScheduleButton(QPushButton):
    def __init__(self, text, schedule):
        super().__init__(text)
        self.schedule = schedule
        self.long_press_timer = QTimer(self)
        self.long_press_timer.setSingleShot(True)
        self.long_press_timer.timeout.connect(self.on_long_press)
        self.setStyleSheet("text-align:left;border:none;")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.long_press_timer.start(500)  # 500ms长按
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.long_press_timer.isActive():
            self.long_press_timer.stop()
        super().mouseReleaseEvent(event)
    
    def on_long_press(self):
        # 长按事件处理
        pass


class ClickableDateCard(QWidget):
    def __init__(self, date, parent_window, parent=None):
        super().__init__(parent)
        self.date = date
        self.parent_window = parent_window
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_window.current_date = self.date
            self.parent_window.switch_view("day")
        super().mousePressEvent(event)

