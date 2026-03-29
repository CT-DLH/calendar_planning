"""
Widget 管理器
优化 PyQt6 widget 的创建和销毁，防止内存泄漏
"""
from typing import Optional, List
from PyQt6.QtWidgets import QWidget, QLayout
from PyQt6.QtCore import QObject


class WidgetManager:
    """Widget 管理器类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._widgets: List[QWidget] = []
        return cls._instance
    
    def register_widget(self, widget: QWidget):
        """注册 widget 到管理器"""
        if widget not in self._widgets:
            self._widgets.append(widget)
    
    def unregister_widget(self, widget: QWidget):
        """从管理器注销 widget"""
        if widget in self._widgets:
            self._widgets.remove(widget)
    
    def safe_delete_widget(self, widget: Optional[QWidget]):
        """安全删除 widget"""
        if widget is None:
            return
        
        # 先断开所有信号连接
        try:
            if isinstance(widget, QObject):
                widget.blockSignals(True)
        except:
            pass
        
        # 从布局中移除
        parent = widget.parent()
        if parent and isinstance(parent, QWidget):
            layout = parent.layout()
            if layout:
                try:
                    layout.removeWidget(widget)
                except:
                    pass
        
        # 从管理器注销
        self.unregister_widget(widget)
        
        # 调用 deleteLater 安全删除
        widget.deleteLater()
    
    def clear_layout(self, layout: QLayout):
        """安全清空布局中的所有 widget"""
        if layout is None:
            return
        
        while layout.count():
            item = layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    self.safe_delete_widget(widget)
    
    def cleanup_all(self):
        """清理所有注册的 widget"""
        for widget in self._widgets[:]:
            self.safe_delete_widget(widget)
        self._widgets.clear()


# 全局 widget 管理器实例
widget_manager = WidgetManager()
