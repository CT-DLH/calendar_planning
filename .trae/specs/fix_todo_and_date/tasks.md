# 修复待办显示和日期留空 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 在ScheduleDialog中添加日期复选框
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 在日期选择器上方添加复选框"设置日期"
  - 默认选中"设置日期"（保持向后兼容）
  - 未选中时，禁用日期选择器
  - 选中时，启用日期选择器
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 对话框中显示"设置日期"复选框
  - `programmatic` TR-1.2: 复选框默认选中
  - `programmatic` TR-1.3: 未选中时日期选择器禁用
- **Notes**: 保持代码风格一致

## [x] Task 2: 修改get_data()方法，支持日期留空
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 当复选框未选中时，返回空字符串作为日期
  - 当复选框选中时，返回选择的日期
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-2.1: 未选中复选框时get_data()返回空日期
  - `programmatic` TR-2.2: 选中复选框时get_data()返回选择的日期
- **Notes**: 保持现有功能完整

## [x] Task 3: 修改add_schedule方法，支持空日期
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 检查get_data()返回的日期是否为空
  - 空日期时添加到待办日程
  - 有日期时添加到日程
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-3.1: 空日期时添加到待办
  - `programmatic` TR-3.2: 有日期时添加到日程
- **Notes**: 保持现有功能不变

## [x] Task 4: 修改add_day_schedule方法，支持空日期
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 检查get_data()返回的日期是否为空
  - 空日期时添加到待办日程
  - 有日期时添加到日程
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: 空日期时添加到待办
  - `programmatic` TR-4.2: 有日期时添加到日程
- **Notes**: 保持现有功能不变

## [x] Task 5: 验证待办日程显示
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 确保待办视图能正确显示待办日程
  - TodoScheduleBox组件正常工作
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-5.1: 应用启动无错误
  - `human-judgement` TR-5.2: 待办日程正确显示
- **Notes**: 确保之前的修复已生效
