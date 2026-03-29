"""
颜色配置
对应原Android应用的颜色资源
"""


class Colors:
    """颜色常量类"""

    # 背景色
    ACTIVITY_BG = "#F5F5F5"
    HEADER_BG = "#FFFFFF"
    DAY_BG = "#FAFAFA"

    # 今天背景色
    TODAY_BG = "#E3F2FD"  # 浅蓝色
    TODAY_SELECTED_BG = "#2196F3"  # 蓝色

    # 选中背景色
    SELECTED_BG = "#E8E8E8"

    # 文字颜色
    TEXT_NORMAL = "#333333"  # 普通文字
    TEXT_LIGHT = "#999999"  # 浅色文字（非当前月份）
    TEXT_WEEKEND = "#1976D2"  # 周末文字（深蓝色）
    TEXT_WEEKEND_LIGHT = "#90CAF9"  # 周末浅色文字
    TEXT_TODAY = "#FFFFFF"  # 今天选中时的文字颜色
    TEXT_HEADER = "#333333"  # 头部文字

    # 标记点颜色
    MARK_BLUE = "#2196F3"
    MARK_WHITE = "#FFFFFF"

    # 边框颜色
    STROKE = "#E0E0E0"

    # 按钮颜色
    BUTTON_NORMAL = "#FFFFFF"
    BUTTON_PRESSED = "#E0E0E0"
    BUTTON_DISABLED = "#BDBDBD"

    # 日程颜色
    EVENT_COLORS = [
        "#F57F68",  # 红色
        "#87D288",  # 绿色
        "#F8B552",  # 橙色
        "#59DBE0",  # 青色
        "#9C27B0",  # 紫色
        "#3F51B5",  # 靛蓝色
    ]
