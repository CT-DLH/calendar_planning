#!/usr/bin/env python3
# 测试脚本：验证时间解析器功能
import sys
import io
from datetime import datetime
from src.time_parser import TimeParser

def test_time_parser():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("=" * 60)
    print("AI时间识别测试")
    print("=" * 60)
    print()
    
    test_cases = [
        # 具体日期测试
        "4月3日 下午3点",
        "2026年4月3日 14:00-16:00",
        "4月5号 上午9点",
        
        # 相对日期测试
        "明天 10:00",
        "后天 下午2点到4点",
        "大后天 18:00",
        
        # 周几测试
        "下周一 14:30",
        "本周三 9:00-12:00",
        "下周日 上午10点",
        
        # 仅时间测试
        "15:00",
        "下午3点半",
        "早上9点15分",
        
        # 时间段测试
        "14:00-16:00",
        "下午2点到4点",
        "9:00至11:30"
    ]
    
    today = datetime.now()
    print(f"当前时间: {today.strftime('%Y年%m月%d日 %H:%M:%S')}")
    print()
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: '{test_case}'")
        try:
            result = TimeParser.parse(test_case)
            print(f"  日期: {result['date']}")
            print(f"  开始时间: {result['start_time']}")
            print(f"  结束时间: {result['end_time']}")
            print(f"  剩余文本: '{result['remaining_text']}'")
            print("  [PASS] 通过")
        except Exception as e:
            print(f"  [FAIL] 失败: {e}")
            all_passed = False
        print()
    
    print("=" * 60)
    if all_passed:
        print("[OK] 所有时间解析测试通过！")
    else:
        print("[WARN] 部分测试失败")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_time_parser()
    sys.exit(0 if success else 1)
