# 日程功能优化 v2 - 实施计划

## [ ] Task 1: 优化日程数据结构，添加时间字段
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 修改日程数据结构，添加start_time和end_time字段
  - 保持向后兼容，旧的time字段仍然支持
  - 没有输入的属性默认留空
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: 日程可以有start_time和end_time字段
  - `programmatic` TR-1.2: 旧数据可以正常加载
  - `programmatic` TR-1.3: 未输入的字段默认留空
- **Notes**: 保持数据向后兼容是关键

## [ ] Task 2: 实现长期日程箱功能
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 将长期日程改为日程箱形式
  - 实现展开/收起功能
  - 支持手动勾选完成
  - 保持现有长期日程数据
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgment` TR-2.1: 长期日程显示为日程箱形式
  - `human-judgment` TR-2.2: 支持展开/收起功能
  - `programmatic` TR-2.3: 支持手动勾选完成
- **Notes**: 可以使用QGroupBox或自定义组件实现

## [ ] Task 3: 实现AI智能时间识别
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 添加时间解析工具类
  - 支持识别"4月3日"、"明天"、"下周一"等时间表达
  - 自动提取日期到date字段
  - 自动提取时间到start_time字段
  - 修改AI命令处理，集成时间解析
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 可以识别"4月3日"格式
  - `programmatic` TR-3.2: 可以识别"明天"、"后天"等相对时间
  - `programmatic` TR-3.3: 可以识别"下周一"等星期表达
  - `programmatic` TR-3.4: 自动提取日期到date字段
  - `programmatic` TR-3.5: 自动提取时间到start_time字段
- **Notes**: 可以使用正则表达式和日期库实现

## [ ] Task 4: 修改日程创建和编辑界面
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3
- **Description**: 
  - 修改日周期日程创建界面，添加起始时间和截止时间输入
  - 修改长期日程创建界面，添加起始时间和截止时间输入
  - 修改日程编辑界面，支持编辑起始时间和截止时间
  - 集成AI智能时间识别到创建界面
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `human-judgment` TR-4.1: 创建界面有起始时间和截止时间输入
  - `human-judgment` TR-4.2: 编辑界面支持编辑起始时间和截止时间
  - `programmatic` TR-4.3: 未输入的字段默认留空
- **Notes**: 保持界面简洁美观

## [ ] Task 5: 实现日视图表格展示
- **Priority**: P0
- **Depends On**: Task 1, Task 4
- **Description**: 
  - 将日视图改为表格形式
  - 列标题：时间、内容、标签、操作
  - 支持显示起始时间和截止时间
  - 表格样式适配深色主题
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgment` TR-5.1: 日视图以表格形式展示
  - `human-judgment` TR-5.2: 包含时间、内容、标签、操作列
  - `human-judgment` TR-5.3: 支持显示起始时间和截止时间
  - `human-judgment` TR-5.4: 表格样式适配深色主题
- **Notes**: 使用QTableWidget实现

## [ ] Task 6: 实现智能排序
- **Priority**: P0
- **Depends On**: Task 1, Task 5
- **Description**: 
  - 实现日程排序函数
  - 自动按照起始时间排序
  - 相同时间的日程按添加时间排序
  - 在日视图和其他视图中应用排序
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 日程自动按起始时间排序
  - `programmatic` TR-6.2: 相同时间按添加时间排序
  - `human-judgment` TR-6.3: 所有视图中排序正确
- **Notes**: 确保排序逻辑在所有视图中一致

## [ ] Task 7: 全面测试所有功能
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**: 
  - 测试日程箱功能是否正常
  - 测试AI时间识别是否准确
  - 测试时间字段是否正常工作
  - 测试日视图表格展示是否美观
  - 测试智能排序是否正确
  - 确保所有现有功能保持完整
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 日程箱功能正常
  - `programmatic` TR-7.2: AI时间识别准确
  - `programmatic` TR-7.3: 时间字段正常工作
  - `human-judgment` TR-7.4: 日视图表格展示美观
  - `programmatic` TR-7.5: 智能排序正确
  - `programmatic` TR-7.6: 所有现有功能保持完整
- **Notes**: 全面测试，确保无回归
