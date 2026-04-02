# 设置对话框模块
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from src.storage import Storage
from src.config import MODEL_LIST, DEFAULT_STYLE, PRESET_STYLES
from src.tag_manager import TagManager


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None, current_style=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_style = current_style if current_style else DEFAULT_STYLE.copy()
        self.tag_manager = TagManager()
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.init_ui()
        self.apply_dark_style()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("⚙️ 设置")
        title.setStyleSheet("font-size:20px;font-weight:bold;")
        layout.addWidget(title)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # API Key + 模型
        api_group = QGroupBox("API 设置")
        api_layout = QVBoxLayout(api_group)
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key："))
        self.api_key = QLineEdit()
        self.api_key.setPlaceholderText("输入智谱API Key")
        # 加载已保存的API Key
        api_key, _ = Storage.load_config()
        if api_key:
            self.api_key.setText(api_key)
        api_key_layout.addWidget(self.api_key)
        api_layout.addLayout(api_key_layout)
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型："))
        self.model_select = QComboBox()
        self.model_select.addItems(MODEL_LIST)
        # 加载已保存的模型
        _, model = Storage.load_config()
        if model and model in MODEL_LIST:
            self.model_select.setCurrentText(model)
        model_layout.addWidget(self.model_select)
        api_layout.addLayout(model_layout)
        
        content_layout.addWidget(api_group)
        
        # 样式设置
        style_group = QGroupBox("样式设置")
        style_layout = QVBoxLayout(style_group)
        
        # 预设样式选择
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设样式："))
        self.preset_style_select = QComboBox()
        self.preset_style_select.addItems(list(PRESET_STYLES.keys()))
        self.preset_style_select.currentTextChanged.connect(self.load_preset_style)
        preset_layout.addWidget(self.preset_style_select)
        style_layout.addLayout(preset_layout)
        
        # 颜色设置
        color_group = QGroupBox("颜色设置")
        color_layout = QGridLayout(color_group)
        
        color_keys = ["primary", "secondary", "background", "surface", "text", "text_secondary", "border", "today", "card"]
        self.color_pickers = {}
        
        for i, key in enumerate(color_keys):
            label = QLabel(f"{key}：")
            color_picker = QPushButton()
            color_picker.setFixedSize(50, 25)
            color_picker.setStyleSheet(f"background:{self.current_style['colors'][key]};")
            color_picker.clicked.connect(lambda checked, k=key: self.show_color_dialog(k))
            self.color_pickers[key] = color_picker
            color_layout.addWidget(label, i // 3, (i % 3) * 2)
            color_layout.addWidget(color_picker, i // 3, (i % 3) * 2 + 1)
        
        style_layout.addWidget(color_group)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QVBoxLayout(font_group)
        
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("字体："))
        self.font_family = QComboBox()
        self.font_family.addItems(["Arial", "SimHei", "Microsoft YaHei", "Times New Roman"])
        self.font_family.setCurrentText(self.current_style['fonts']['family'])
        font_family_layout.addWidget(self.font_family)
        font_layout.addLayout(font_family_layout)
        
        # 字体大小设置
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("字体大小："))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(self.current_style['fonts']['size']['normal'])
        font_size_layout.addWidget(self.font_size)
        font_layout.addLayout(font_size_layout)
        
        style_layout.addWidget(font_group)
        
        # 大小设置
        size_group = QGroupBox("大小设置")
        size_layout = QVBoxLayout(size_group)
        
        # 卡片圆角
        card_radius_layout = QHBoxLayout()
        card_radius_layout.addWidget(QLabel("卡片圆角："))
        self.card_radius = QSpinBox()
        self.card_radius.setRange(0, 20)
        self.card_radius.setValue(self.current_style['sizes']['card_radius'])
        card_radius_layout.addWidget(self.card_radius)
        size_layout.addLayout(card_radius_layout)
        
        # 按钮圆角
        button_radius_layout = QHBoxLayout()
        button_radius_layout.addWidget(QLabel("按钮圆角："))
        self.button_radius = QSpinBox()
        self.button_radius.setRange(0, 20)
        self.button_radius.setValue(self.current_style['sizes']['button_radius'])
        button_radius_layout.addWidget(self.button_radius)
        size_layout.addLayout(button_radius_layout)
        
        # 内边距
        padding_layout = QHBoxLayout()
        padding_layout.addWidget(QLabel("内边距："))
        self.padding = QSpinBox()
        self.padding.setRange(0, 20)
        self.padding.setValue(self.current_style['sizes']['padding'])
        padding_layout.addWidget(self.padding)
        size_layout.addLayout(padding_layout)
        
        style_layout.addWidget(size_group)
        content_layout.addWidget(style_group)
        
        # 数据管理
        data_group = QGroupBox("数据管理")
        data_layout = QVBoxLayout(data_group)
        
        # 导入按钮
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self.import_data)
        data_layout.addWidget(import_btn)
        
        # 导出按钮
        export_btn = QPushButton("导出")
        export_btn.clicked.connect(self.export_data)
        data_layout.addWidget(export_btn)
        
        # 回收站按钮
        bin_btn = QPushButton("回收站")
        bin_btn.clicked.connect(self.open_recycle_bin)
        data_layout.addWidget(bin_btn)
        
        content_layout.addWidget(data_group)
        
        # 标签管理按钮
        tag_manager_btn = QPushButton("🏷️ 标签管理")
        tag_manager_btn.clicked.connect(self.open_tag_manager)
        content_layout.addWidget(tag_manager_btn)
        
        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("保存")
        save_btn.setObjectName("blue")
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
    
    def apply_dark_style(self):
        self.setStyleSheet("""
            QDialog { background:#111827; }
            QLabel { color:#e5e7eb; }
            QLineEdit, QComboBox, QSpinBox, QGroupBox {
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
            QGroupBox {
                color:#e5e7eb; border:1px solid #374151;
                border-radius:6px; margin-top:12px; padding-top:12px;
            }
            QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 5px; }
            QScrollArea { border:none; }
        """)
    
    def show_color_dialog(self, color_key):
        color = QColorDialog.getColor(QColor(self.current_style['colors'][color_key]), self)
        if color.isValid():
            self.current_style['colors'][color_key] = color.name()
            self.color_pickers[color_key].setStyleSheet(f"background:{color.name()};")
    
    def load_preset_style(self, preset_name):
        if preset_name in PRESET_STYLES:
            self.current_style = PRESET_STYLES[preset_name].copy()
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
    
    def save_settings(self):
        # 保存API配置
        Storage.save_config(self.api_key.text().strip(), self.model_select.currentText())
        
        # 更新样式配置
        self.current_style['fonts']['family'] = self.font_family.currentText()
        self.current_style['fonts']['size']['normal'] = self.font_size.value()
        self.current_style['sizes']['card_radius'] = self.card_radius.value()
        self.current_style['sizes']['button_radius'] = self.button_radius.value()
        self.current_style['sizes']['padding'] = self.padding.value()
        
        # 保存样式
        Storage.save("style", self.current_style)
        
        # 通知父窗口应用样式
        if self.parent_window:
            self.parent_window.current_style = self.current_style
            self.parent_window.apply_style()
        
        self.accept()
    
    def import_data(self):
        if self.parent_window:
            self.parent_window.import_data()
    
    def export_data(self):
        if self.parent_window:
            self.parent_window.export_data()
    
    def open_recycle_bin(self):
        if self.parent_window:
            self.parent_window.open_recycle_bin()
    
    def open_tag_manager(self):
        from src.ui_dialogs import TagManagerDialog
        dialog = TagManagerDialog(self)
        dialog.exec()
