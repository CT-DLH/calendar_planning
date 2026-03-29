# 系统日历集成模块
import platform
import json
from datetime import datetime

class SystemCalendar:
    def __init__(self):
        self.platform = platform.system()
        self.calendar_available = self.check_calendar_availability()
    
    def check_calendar_availability(self):
        """检查系统日历是否可用"""
        if self.platform == "Windows":
            try:
                import win32com.client
                return True
            except ImportError:
                return False
        elif self.platform == "Darwin":
            try:
                import objc
                return True
            except ImportError:
                return False
        elif self.platform == "Linux":
            # Linux 系统日历支持
            return True
        return False
    
    def import_events(self):
        """从系统日历导入事件"""
        if not self.calendar_available:
            return []
        
        if self.platform == "Windows":
            return self._import_from_windows_calendar()
        elif self.platform == "Darwin":
            return self._import_from_mac_calendar()
        elif self.platform == "Linux":
            return self._import_from_linux_calendar()
        return []
    
    def export_events(self, events):
        """导出事件到系统日历"""
        if not self.calendar_available:
            return False
        
        if self.platform == "Windows":
            return self._export_to_windows_calendar(events)
        elif self.platform == "Darwin":
            return self._export_to_mac_calendar(events)
        elif self.platform == "Linux":
            return self._export_to_linux_calendar(events)
        return False
    
    def _import_from_windows_calendar(self):
        """从 Windows 日历导入事件"""
        try:
            import win32com.client
            outlook = win32com.client.Dispatch('Outlook.Application')
            namespace = outlook.GetNamespace('MAPI')
            calendar = namespace.GetDefaultFolder(9)  # 9 是日历文件夹
            items = calendar.Items
            items.IncludeRecurrences = True
            
            events = []
            for item in items:
                if hasattr(item, 'Subject') and hasattr(item, 'Start'):
                    event = {
                        'id': str(hash(item.Subject + str(item.Start))),
                        'content': item.Subject,
                        'time': item.Start.strftime('%H:%M') if hasattr(item.Start, 'strftime') else '',
                        'date': item.Start.strftime('%Y-%m-%d') if hasattr(item.Start, 'strftime') else '',
                        'completed': False,
                        'tag': 'normal',
                        'subtasks': []
                    }
                    events.append(event)
            return events
        except Exception as e:
            print(f"Windows 日历导入错误: {e}")
            return []
    
    def _import_from_mac_calendar(self):
        """从 macOS 日历导入事件"""
        try:
            from Foundation import NSBundle
            CalendarStore = NSBundle.bundleWithIdentifier_('com.apple.CalendarStore')
            if CalendarStore:
                CalendarStore = CalendarStore.classNamed_('CalCalendarStore')
                store = CalendarStore.defaultCalendarStore()
                events = store.events()
                
                result = []
                for event in events:
                    start_date = event.startDate()
                    if start_date:
                        event_dict = {
                            'id': str(hash(event.title() + str(start_date))),
                            'content': event.title(),
                            'time': start_date.description().split(' ')[1],
                            'date': start_date.description().split(' ')[0],
                            'completed': False,
                            'tag': 'normal',
                            'subtasks': []
                        }
                        result.append(event_dict)
                return result
        except Exception as e:
            print(f"macOS 日历导入错误: {e}")
        return []
    
    def _import_from_linux_calendar(self):
        """从 Linux 日历导入事件"""
        try:
            import os
            import vobject
            
            # 尝试读取标准位置的 iCalendar 文件
            calendar_paths = [
                os.path.expanduser('~/.local/share/calendar/'),
                os.path.expanduser('~/.calendars/'),
                os.path.expanduser('~/.kde/share/apps/korganizer/')
            ]
            
            events = []
            for path in calendar_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.ics'):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r') as f:
                                        cal = vobject.readOne(f)
                                        if hasattr(cal, 'vevent_list'):
                                            for event in cal.vevent_list:
                                                if hasattr(event, 'summary') and hasattr(event, 'dtstart'):
                                                    event_dict = {
                                                        'id': str(hash(str(event.summary.value) + str(event.dtstart.value))),
                                                        'content': str(event.summary.value),
                                                        'time': event.dtstart.value.strftime('%H:%M') if hasattr(event.dtstart.value, 'strftime') else '',
                                                        'date': event.dtstart.value.strftime('%Y-%m-%d') if hasattr(event.dtstart.value, 'strftime') else '',
                                                        'completed': False,
                                                        'tag': 'normal',
                                                        'subtasks': []
                                                    }
                                                    events.append(event_dict)
                                except Exception:
                                    pass
            return events
        except Exception as e:
            print(f"Linux 日历导入错误: {e}")
            return []
    
    def _export_to_windows_calendar(self, events):
        """导出事件到 Windows 日历"""
        try:
            import win32com.client
            outlook = win32com.client.Dispatch('Outlook.Application')
            namespace = outlook.GetNamespace('MAPI')
            calendar = namespace.GetDefaultFolder(9)  # 9 是日历文件夹
            
            for event in events:
                appointment = outlook.CreateItem(1)  # 1 是约会项
                appointment.Subject = event['content']
                appointment.Start = f"{event['date']} {event['time'] if event['time'] else '09:00'}"
                appointment.End = f"{event['date']} {event['time'] if event['time'] else '10:00'}"
                appointment.Save()
            return True
        except Exception as e:
            print(f"Windows 日历导出错误: {e}")
            return False
    
    def _export_to_mac_calendar(self, events):
        """导出事件到 macOS 日历"""
        try:
            from Foundation import NSBundle, NSDate
            CalendarStore = NSBundle.bundleWithIdentifier_('com.apple.CalendarStore')
            if CalendarStore:
                CalendarStore = CalendarStore.classNamed_('CalCalendarStore')
                CalEvent = NSBundle.bundleWithIdentifier_('com.apple.CalendarStore').classNamed_('CalEvent')
                store = CalendarStore.defaultCalendarStore()
                calendars = store.calendars()
                
                if calendars:
                    target_calendar = calendars[0]  # 使用第一个日历
                    
                    for event in events:
                        cal_event = CalEvent.event()
                        cal_event.setTitle_(event['content'])
                        
                        # 创建日期对象
                        date_str = f"{event['date']} {event['time'] if event['time'] else '09:00'}"
                        start_date = NSDate.dateWithString_(date_str)
                        end_date = start_date.dateByAddingTimeInterval_(3600)  # 默认 1 小时
                        
                        cal_event.setStartDate_(start_date)
                        cal_event.setEndDate_(end_date)
                        cal_event.setCalendar_(target_calendar)
                        
                        error = store.saveEvent_span_error_(cal_event, 0, None)
                        if error:
                            print(f"保存事件失败: {error}")
                    return True
        except Exception as e:
            print(f"macOS 日历导出错误: {e}")
        return False
    
    def _export_to_linux_calendar(self, events):
        """导出事件到 Linux 日历"""
        try:
            import os
            import vobject
            
            # 创建 iCalendar 文件
            cal = vobject.iCalendar()
            
            for event in events:
                vevent = cal.add('vevent')
                vevent.add('summary').value = event['content']
                
                # 设置开始时间
                start_time = f"{event['date']}T{event['time'] if event['time'] else '09:00'}:00"
                vevent.add('dtstart').value = start_time
                
                # 设置结束时间（默认 1 小时后）
                end_time = f"{event['date']}T{event['time'] if event['time'] else '10:00'}:00"
                vevent.add('dtend').value = end_time
            
            # 保存到标准位置
            calendar_dir = os.path.expanduser('~/.local/share/calendar')
            os.makedirs(calendar_dir, exist_ok=True)
            
            file_path = os.path.join(calendar_dir, f'exported_events_{datetime.now().strftime("%Y%m%d_%H%M%S")}.ics')
            with open(file_path, 'w') as f:
                f.write(cal.serialize())
            
            return True
        except Exception as e:
            print(f"Linux 日历导出错误: {e}")
            return False