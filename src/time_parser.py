import re
from datetime import datetime, timedelta

class TimeParser:
    WEEKDAY_MAP = {
        '周一': 0, '周二': 1, '周三': 2, '周四': 3, '周五': 4, '周六': 5, '周日': 6,
        '星期一': 0, '星期二': 1, '星期三': 2, '星期四': 3, '星期五': 4, '星期六': 5, '星期日': 6,
        '星期天': 6
    }

    @staticmethod
    def parse(text):
        result = {
            'date': None,
            'start_time': '',
            'end_time': '',
            'remaining_text': text
        }

        # 先尝试提取时间段（包含完整的时间段，如 14:00-16:00）
        full_time_range_pattern = re.compile(r'(\d{1,2}):(\d{2})\s*[~-至到]\s*(\d{1,2}):(\d{2})')
        full_match = full_time_range_pattern.search(text)
        if full_match:
            start_hour = int(full_match.group(1))
            start_min = int(full_match.group(2))
            end_hour = int(full_match.group(3))
            end_min = int(full_match.group(4))
            result['start_time'] = f"{start_hour:02d}:{start_min:02d}"
            result['end_time'] = f"{end_hour:02d}:{end_min:02d}"
            text = text[:full_match.start()] + text[full_match.end():]
        else:
            # 尝试简单的连字符格式，如 14:00-16:00，不匹配中文
            simple_time_range_pattern = re.compile(r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})')
            simple_match = simple_time_range_pattern.search(text)
            if simple_match:
                start_hour = int(simple_match.group(1))
                start_min = int(simple_match.group(2))
                end_hour = int(simple_match.group(3))
                end_min = int(simple_match.group(4))
                result['start_time'] = f"{start_hour:02d}:{start_min:02d}"
                result['end_time'] = f"{end_hour:02d}:{end_min:02d}"
                text = text[:simple_match.start()] + text[simple_match.end():]

        # 再提取其他时间部分
        if not result['start_time']:
            time_result = TimeParser._extract_times(text)
            result['start_time'] = time_result['start_time']
            result['end_time'] = time_result['end_time']
            text = time_result['remaining_text']

        # 再提取日期部分
        date_result = TimeParser._extract_date(text)
        result['date'] = date_result['date']
        result['remaining_text'] = date_result['remaining_text'].strip()

        return result

    @staticmethod
    def _extract_times(text):
        result = {
            'start_time': '',
            'end_time': '',
            'remaining_text': text
        }

        # 匹配时间段，如 14:00-16:00, 下午2点到4点
        time_range_pattern = re.compile(
            r'(\d{1,2}):(\d{2})\s*[~-至到]\s*(\d{1,2}):(\d{2})|'
            r'(上午|下午|晚上|早上|凌晨)?(\d{1,2})[点时](半)?(\d{2}分)?\s*[~-至到]\s*(上午|下午|晚上|早上|凌晨)?(\d{1,2})[点时](半)?(\d{2}分)?'
        )

        match = time_range_pattern.search(text)
        if match:
            if match.group(1):
                # 格式: 14:00-16:00
                start_hour = int(match.group(1))
                start_min = int(match.group(2))
                end_hour = int(match.group(3))
                end_min = int(match.group(4))
                result['start_time'] = f"{start_hour:02d}:{start_min:02d}"
                result['end_time'] = f"{end_hour:02d}:{end_min:02d}"
            else:
                # 格式: 下午2点到4点, 下午2点半到4点
                start_period = match.group(5) or ''
                start_hour = int(match.group(6))
                start_half = match.group(7) == '半'
                start_min_str = match.group(8) or '0分'
                start_min = int(start_min_str.replace('分', '')) if '分' in start_min_str else 0
                if start_half:
                    start_min = 30
                end_period = match.group(9) or ''
                end_hour = int(match.group(10))
                end_half = match.group(11) == '半'
                end_min_str = match.group(12) or '0分'
                end_min = int(end_min_str.replace('分', '')) if '分' in end_min_str else 0
                if end_half:
                    end_min = 30

                start_hour = TimeParser._adjust_hour(start_hour, start_period)
                end_hour = TimeParser._adjust_hour(end_hour, end_period or start_period)

                result['start_time'] = f"{start_hour:02d}:{start_min:02d}"
                result['end_time'] = f"{end_hour:02d}:{end_min:02d}"

            result['remaining_text'] = text[:match.start()] + text[match.end():]
            return result

        # 匹配单个时间，如 14:00, 下午2点, 下午2点半
        single_time_pattern = re.compile(
            r'(\d{1,2}):(\d{2})|'
            r'(上午|下午|晚上|早上|凌晨)?(\d{1,2})[点时](半)?(\d{2}分)?'
        )

        match = single_time_pattern.search(text)
        if match:
            if match.group(1):
                # 格式: 14:00
                hour = int(match.group(1))
                minute = int(match.group(2))
                result['start_time'] = f"{hour:02d}:{minute:02d}"
            else:
                # 格式: 下午2点, 下午2点半
                period = match.group(3) or ''
                hour = int(match.group(4))
                half = match.group(5) == '半'
                min_str = match.group(6) or '0分'
                minute = int(min_str.replace('分', '')) if '分' in min_str else 0
                if half:
                    minute = 30
                hour = TimeParser._adjust_hour(hour, period)
                result['start_time'] = f"{hour:02d}:{minute:02d}"

            result['remaining_text'] = text[:match.start()] + text[match.end():]
            return result

        return result

    @staticmethod
    def _adjust_hour(hour, period):
        if period in ['下午', '晚上'] and hour < 12:
            return hour + 12
        if period in ['凌晨', '早上'] and hour == 12:
            return 0
        return hour

    @staticmethod
    def _extract_date(text):
        result = {
            'date': None,
            'remaining_text': text
        }

        today = datetime.now()

        # 匹配具体日期格式: 4月3日, 4月3号, 2024年4月3日
        specific_date_pattern = re.compile(
            r'((\d{4})年)?(\d{1,2})月(\d{1,2})[日号]'
        )

        match = specific_date_pattern.search(text)
        if match:
            year = int(match.group(2)) if match.group(2) else today.year
            month = int(match.group(3))
            day = int(match.group(4))
            try:
                result['date'] = datetime(year, month, day).strftime('%Y-%m-%d')
                result['remaining_text'] = text[:match.start()] + text[match.end():]
                return result
            except ValueError:
                pass

        # 匹配相对日期: 明天, 后天, 昨天
        relative_pattern = re.compile(r'(明天|后天|昨天|大后天|大前天)')
        match = relative_pattern.search(text)
        if match:
            keyword = match.group(1)
            delta = {
                '明天': 1,
                '后天': 2,
                '大后天': 3,
                '昨天': -1,
                '大前天': -2
            }.get(keyword, 0)
            result['date'] = (today + timedelta(days=delta)).strftime('%Y-%m-%d')
            result['remaining_text'] = text[:match.start()] + text[match.end():]
            return result

        # 匹配下周一/本周一
        weekday_pattern = re.compile(r'(下|本)?(周|星期)(一|二|三|四|五|六|日|天)')
        match = weekday_pattern.search(text)
        if match:
            prefix = match.group(1) or ''
            weekday_key = match.group(2) + match.group(3)
            target_weekday = TimeParser.WEEKDAY_MAP.get(weekday_key, 0)
            current_weekday = today.weekday()

            if prefix == '下':
                days_ahead = (target_weekday - current_weekday + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7
            else:
                days_ahead = (target_weekday - current_weekday + 7) % 7

            result['date'] = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            result['remaining_text'] = text[:match.start()] + text[match.end():]
            return result

        return result
