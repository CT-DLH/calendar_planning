# UI优化 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 增强ScheduleDialog，添加日期选择功能
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 在ScheduleDialog中添加日期选择器（QDateEdit）
  - 支持待办模式（日期可选，不填则为待办）
  - 保持现有功能完整性
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: ScheduleDialog包含日期选择器组件
  - `programmatic` TR-1.2: 日期选择器默认显示当前日期
  - `programmatic` TR-1.3: get_data()方法返回选择的日期
- **Notes**: 保持与现有代码风格一致

## [x] Task 2: 修改execute_ai_command方法，支持智能日期判断
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 解析AI返回的内容，使用TimeParser检测是否有日期
  - 如果有日期，添加到日程；如果没有日期，添加到待办
  - 保持现有功能兼容性
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: 输入含日期的内容时，添加到日程
  - `programmatic` TR-2.2: 输入不含日期的内容时，添加到待办
- **Notes**: 使用现有的TimeParser模块进行日期解析

## [x] Task 3: 简化底部操作栏
- **Priority**: P1
- **Depends On**: None
- **Description**: 
  - 移除"添加习惯"按钮
  - 移除"清空所有"按钮
  - 只保留：添加日程、导入、导出、回收站
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 底部操作栏只显示4个必要按钮
  - `programmatic` TR-3.2: 移除的按钮相关代码被清理
- **Notes**: 保留相关功能的代码实现，只移除UI按钮

## [x] Task 4: 移除QuickAddScheduleDialog及其引用
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 删除QuickAddScheduleDialog类
  - 修改add_day_schedule方法，使用ScheduleDialog替代
  - 更新相关引用
- **Acceptance Criteria Addressed**: [AC-1, AC-5]
- **Test Requirements**:
  - `programmatic` TR-4.1: QuickAddScheduleDialog类已被移除
  - `programmatic` TR-4.2: add_day_schedule使用ScheduleDialog
- **Notes**: 确保功能替代完整

## [x] Task 5: 简化待办视图，移除单独的AI添加待办功能
- **Priority**: P2
- **Depends On**: Task 2
- **Description**: 
  - 移除add_todo_schedule_with_ai方法
  - 简化待办视图的输入区域，只保留手动添加
  - 引导用户在AI对话窗口使用AI功能
- **Acceptance Criteria Addressed**: [AC-3, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 待办视图只有手动添加功能
  - `programmatic` TR-5.2: 相关代码被清理
- **Notes**: 保持手动添加待办的功能

## [x] Task 6: 测试与验证
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5
- **Description**: 
  - 运行应用，验证所有功能正常
  - 测试AI添加日程功能
  - 测试手动添加日程功能
  - 测试待办添加功能
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: 应用启动无错误
  - `programmatic` TR-6.2: 所有添加功能正常工作
  - `human-judgement` TR-6.3: UI体验流畅
- **Notes**: 全面测试，确保没有回归
