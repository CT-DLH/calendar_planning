#!/usr/bin/env python3
# 测试脚本：验证智能排序功能
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 模拟 sort_schedules 函数
def sort_schedules(schedules):
    def get_sort_key(schedule):
        start_time = schedule.get("start_time", "")
        time_key = start_time if start_time else "99:99"
        created_at = schedule.get("created_at", 0)
        if not created_at and "id" in schedule:
            try:
                id_str = schedule["id"]
                split_index = 0
                while split_index < len(id_str) and id_str[split_index].isdigit():
                    split_index += 1
                if split_index > 0:
                    created_at = float(id_str[:split_index])
            except (ValueError, IndexError):
                created_at = 0
        return (time_key, created_at)
    return sorted(schedules, key=get_sort_key)

def test_sorting():
    print("=" * 60)
    print("智能排序测试")
    print("=" * 60)
    print()
    
    test_schedules = [
        {"id": "1711600000abc", "content": "下午会议", "start_time": "14:00", "end_time": "15:00"},
        {"id": "1711500000xyz", "content": "早晨锻炼", "start_time": "08:00"},
        {"id": "1711700000123", "content": "晚上学习", "start_time": "20:00", "end_time": "22:00"},
        {"id": "1711550000def", "content": "午餐时间", "start_time": "12:00"},
        {"id": "1711400000ghi", "content": "无时间日程"},
        {"id": "1711580000jkl", "content": "上午工作", "start_time": "09:00", "end_time": "12:00"},
    ]
    
    print("原始顺序：")
    for i, s in enumerate(test_schedules):
        time = s.get("start_time", "")
        if time and s.get("end_time", ""):
            time = f"{time}-{s['end_time']}"
        print(f"  {i+1}. {time or '无时间'} - {s['content']}")
    print()
    
    sorted_schedules = sort_schedules(test_schedules)
    
    print("排序后顺序：")
    for i, s in enumerate(sorted_schedules):
        time = s.get("start_time", "")
        if time and s.get("end_time", ""):
            time = f"{time}-{s['end_time']}"
        print(f"  {i+1}. {time or '无时间'} - {s['content']}")
    print()
    
    expected_order = [
        "08:00",
        "09:00-12:00",
        "12:00",
        "14:00-15:00",
        "20:00-22:00",
        "无时间"
    ]
    
    actual_order = []
    for s in sorted_schedules:
        time = s.get("start_time", "")
        if time and s.get("end_time", ""):
            time = f"{time}-{s['end_time']}"
        actual_order.append(time or "无时间")
    
    print("=" * 60)
    if actual_order == expected_order:
        print("[OK] 智能排序测试通过！")
        print("排序规则：")
        print("  1. 按起始时间从早到晚排序")
        print("  2. 无时间的日程排在最后")
    else:
        print("[FAIL] 智能排序测试失败")
        print(f"期望顺序: {expected_order}")
        print(f"实际顺序: {actual_order}")
    print("=" * 60)
    
    return actual_order == expected_order

if __name__ == "__main__":
    success = test_sorting()
    sys.exit(0 if success else 1)
