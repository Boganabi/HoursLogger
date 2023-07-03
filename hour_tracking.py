from datetime import datetime, date

class ShiftTime:
    """Contains info for a 'shift', a group of corresponding clock-in and clock-out time. Some checks are performed to prevent errors."""
    def __init__(self, clock_in_datetime_str:str, clock_out_datetime_str:str, hours_check_str:str=None):
        # parse datetimes
        self.clock_in_datetime:datetime = self._parse_datetime_str(clock_in_datetime_str)
        self.clock_out_datetime:datetime = self._parse_datetime_str(clock_out_datetime_str)

        # set date pointer for easy access
        self.date:date = self.clock_in_datetime.date()

        # parse weekday
        self.day_of_week:int = self.date.weekday()
        self.day_of_week_str:str = self.date.strftime("%A")

        # format form info
        self.date_str:str = self.date.strftime("%m/%d")
        self.clock_in_time_str:str = self.clock_in_datetime.strftime("%H.%M")
        self.clock_out_time_str:str = self.clock_out_datetime.strftime("%H.%M")
        
        # check that times are for same day
        if self.clock_in_datetime.date().day != self.clock_out_datetime.date().day:
            raise ValueError(f"ShiftTime clock-in clock-out date do not match. Clock-in date:{self.clock_in_datetime.date().isoformat()}. Clock-out-date:{self.clock_out_datetime.date().isoformat()}")
        
        # check if clock out is after clock in
        if self.clock_in_datetime > self.clock_out_datetime:
            raise ValueError(f"ShifctTime clock-out is before clock-in. Clock-in: {self.clock_in_datetime.strftime('%H:%M')}. Clock-out: {self.clock_out_datetime.strftime('%H:%M')}")
        
        # check if parsed hours are correct and line up with what is reported on website
        if hours_check_str is not None:
            shift_hours:int = (self.clock_out_datetime - self.clock_in_datetime).seconds // 3600
            shift_minutes:int = (self.clock_out_datetime - self.clock_in_datetime).seconds // 60
            check_hours_str, check_minutes_str = hours_check_str.split(":")
            check_minutes = int(check_hours_str) * 60 + int(check_minutes_str)
            if abs(shift_minutes - check_minutes) > 1:
                raise ValueError(f"The hours parsed are not the same as reported from check. Parsed: {shift_hours}:{shift_minutes%60}. Check: {hours_check_str}.")

    def _parse_datetime_str(self, datetime_str:str) -> datetime:
        # all this hoopla is required because no leading zeros is platform dependent, without using alternate parsing libraries
        date_str, time_str, ampm_str = datetime_str.split(" ")
        month_str, day_str, year_str = date_str.split("/")
        hour_str, minute_str = time_str.split(":")

        day_str = "0" + day_str if len(day_str) == 1 else day_str
        month_str = "0" + month_str if len(month_str) == 1 else month_str
        hour_str = "0" + hour_str if len(hour_str) == 1 else hour_str
        fixed_datetime_str = f"{year_str}-{month_str}-{day_str} {hour_str}:{minute_str} {ampm_str}"
        return datetime.strptime(fixed_datetime_str, "%Y-%m-%d %I:%M %p")
    
class WorkDay:
    def __init__(self):
        self.shift_times:list[ShiftTime] = []
    
    def add_shift(self, shift:ShiftTime):
        self.shift_times.append(shift)
    
    def is_valid(self) -> bool:
        if len(self.shift_times) == 0:
            return False
        if len(self.shift_times) > 1:
            day_of_week = self.shift_times[0].day_of_week
            for shift in self.shift_times:
                if day_of_week != shift.day_of_week:
                    return False
        return True
    
    def get_form_info(self) -> tuple[str,str,str,str|None,str|None]|None:
        """Returns a tuple of that has form info of:
        date, clock in, clock out, clock in (optional), clock out (optional)
        Can return None if no shifts.
        If invalid, will return 00.00 for first clock in and clock out"""
        if len(self.shift_times) == 0:
            return None
        
        if not self.is_valid():
            return (self.shift_times[0].date_str, "00.00", "00.00", None, None)
        
        shift1:ShiftTime|None = None
        shift2:ShiftTime|None = None

        for shift in self.shift_times:
            if shift1 is None:
                shift1 = shift
            elif shift1.clock_in_datetime > shift.clock_in_datetime:
                shift2 = shift1
                shift1 = shift
            elif shift2 is None:
                shift2 = shift
            elif shift2.clock_in_datetime > shift.clock_in_datetime:
                shift2 = shift

        return (
            shift1.date_str,
            shift1.clock_in_time_str,
            shift1.clock_out_time_str,
            shift2.clock_in_time_str if shift2 is not None else None,
            shift2.clock_out_time_str if shift2 is not None else None
        )

class WorkWeek:
    def __init__(self):
        self.work_days:dict[int,WorkDay] = {}
    
    def add_shift(self, shift:ShiftTime):
        if shift.day_of_week not in self.work_days.keys():
            self.work_days[shift.day_of_week] = WorkDay()
        self.work_days[shift.day_of_week].add_shift(shift)

    def trim_outside_range(self, date_lower:date, date_upper:date):
        def date_less_than_eq(date1:date, date2:date) -> bool:
            """Compares date only on month and day"""
            return (date1.month < date2.month) or (date1.month == date2.month and date1.day <= date2.day)
        def date_greater_than_eq(date1:date, date2:date) -> bool:
            """Compares date only on month and day"""
            return (date1.month > date2.month) or (date1.month == date2.month and date1.day >= date2.day)
        
        self.work_days = {day_of_week:work_day for (day_of_week, work_day) in self.work_days.items() if date_greater_than_eq(work_day.shift_times[0].date, date_lower) and date_less_than_eq(work_day.shift_times[0].date, date_upper) }
            
    def trim_empty_days(self):
        self.work_days = {key:val for (key, val) in self.work_days.items() if len(val.shift_times) > 0}
    
    def is_empty(self) -> bool:
        for work_day in self.work_days.values():
            if len(work_day.shift_times) > 0:
                return False
        return True