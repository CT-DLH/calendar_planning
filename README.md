# AI 日程管理器

一个功能强大的 Python 日历 GUI 组件，提供直观的日程管理功能，支持 AI 辅助创建日程、系统日历集成和高度可定制的界面。

## 功能特性

- 📅 **多视图切换**：日、周、月和长期日程视图
- ✨ **AI 辅助**：使用 AI 智能创建和管理日程
- 🔄 **系统日历集成**：支持与系统日历的导入/导出
- 🎨 **高度可定制**：自定义颜色、字体、大小等样式
- 📋 **子任务管理**：为每个日程添加详细的子任务
- 🗑️ **回收站功能**：误删日程可恢复
- 🏷️ **标签系统**：支持一般、重要、紧急、重要且紧急标签
- 🎯 **习惯追踪**：专门的习惯管理功能
- 💾 **数据导入导出**：支持 JSON 格式的导入导出

## 系统要求

- Python 3.7+
- 操作系统：Windows、macOS 或 Linux

## 安装

### 1. 克隆仓库

```bash
git clone <repository-url>
cd calendar_planning
```

### 2. 安装依赖

使用 pip 安装所需依赖：

```bash
pip install -r requirements.txt
```

依赖说明：
- `PyQt6==6.10.2` - GUI 框架
- `requests==2.32.3` - 用于 API 调用
- `pywin32` (Windows) - 系统日历集成
- `pyobjc` (macOS) - 系统日历集成
- `vobject` (Linux) - 系统日历集成

## 快速开始

### 运行应用

在项目根目录执行：

```bash
python main.py
```

### 基本使用

1. **添加日程**：点击底部的"+ 添加日程"按钮，或在日视图/长期视图的输入框中输入内容并按 Enter
2. **切换视图**：点击顶部的"日"、"周"、"月"、"长期"按钮
3. **导航日期**：使用左右箭头按钮在不同时期之间导航
4. **标记完成**：长按日程，在弹出的对话框中切换完成状态
5. **编辑日程**：点击日程卡片，在弹出的对话框中编辑
6. **删除日程**：长按日程，在弹出的对话框中选择删除
7. **导入/导出**：使用底部的导入/导出按钮进行数据迁移

### AI 功能使用

1. 在设置面板中填写智谱 API Key
2. 选择合适的模型
3. 在日视图或长期视图的输入框中输入自然语言描述
4. 按 Enter 键，AI 将自动创建日程

## 界面说明

### 顶部区域
- **拖拽栏**：可以拖动窗口
- **设置按钮**：打开设置面板，配置 API Key、模型和样式
- **最小化/关闭按钮**：控制窗口状态

### 导航栏
- **视图切换按钮**：在日/周/月/长期视图之间切换
- **日期导航**：左右箭头按钮用于切换日期
- **隐藏已完成**：勾选后隐藏已完成的日程

### 主内容区
- **左侧**：日历视图，显示日期和日程概览
- **右侧**：详细的日程列表，可滚动查看

### 底部操作栏
- **添加日程**：创建新的日程
- **添加习惯**：创建新的习惯
- **导入**：从 JSON 或系统日历导入数据
- **导出**：导出数据到 JSON 或系统日历
- **回收站**：查看和恢复已删除的日程
- **清空所有**：清空所有日程到回收站

## 样式定制

1. 点击设置按钮打开设置面板
2. 选择预设样式或自定义颜色、字体和大小
3. 点击"保存样式"按钮保存更改

## 数据存储

- 日程数据保存在 `schedule_data/` 目录中
- `schedules.json`：存储所有日程
- `recycle_bin.json`：存储已删除的日程

## 打包分发

### Windows 打包

使用 PyInstaller 打包为可执行文件：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AI日程管理器" main.py
```

### macOS 打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AI日程管理器" main.py
```

### Linux 打包

```bash
pip install pyinstaller
pyinstaller --onefile --name "AI日程管理器" main.py
```

## 常见问题

### API Key 配置
- 请访问智谱 AI 官方网站获取 API Key
- 确保 API Key 格式正确且有效

### 系统日历集成
- Windows：需要安装 pywin32
- macOS：需要安装 pyobjc
- Linux：需要安装 vobject

### 性能优化
- 应用使用卡片缓存来提高渲染性能
- 对于大量日程，建议使用月视图进行概览

## 开发

### 项目结构

```
calendar_planning/
├── src/
│   ├── ui.py          # 主界面模块
│   ├── storage.py     # 数据存储模块
│   ├── ai.py          # AI 功能模块
│   ├── config.py      # 配置模块
│   └── system_calendar.py  # 系统日历集成
├── schedule_data/     # 数据存储目录
├── main.py            # 主入口
├── requirements.txt   # 依赖文件
└── README.md          # 文档
```

### 扩展功能

要添加新功能，可以：
1. 在 `src/ui.py` 中添加新的 UI 组件和事件处理
2. 在 `src/ai.py` 中扩展 AI 功能
3. 在 `src/config.py` 中添加新的配置选项
4. 在 `src/system_calendar.py` 中增强系统日历集成

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：<your-email@example.com>
- GitHub：<your-github-username>
