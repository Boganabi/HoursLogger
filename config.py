from datetime import date
from dotenv import dotenv_values

class Config:
    def __init__(self):
        config = dotenv_values("config.txt")
        self.employee_id:str = self._get_var(config, "EMPLOYEE_ID", "Enter your employee ID number: ")
        self.school_id:str = self._get_var(config, "SCHOOL_ID", "Enter your school ID number: ")
        self.adobe_sign_email:str = self._get_var(config, "ADOBE_SIGN_EMAIL", "Enter your adobe sign email (omit the @coyote.csusb.edu): ")
        self.units_enrolled:str = self._get_var(config, "UNITS_ENROLLED", "Enter the amount of units you are currently enrolled in: ")

        tmp = None
        while tmp is None:
            tmp = self._get_var(config, "TEST_TIMESHEET_START_DATE", "Enter the start date for your timesheet (MM/DD/YY, ex: 6/30/23): ")
            try:
                month, day, year = tmp.split("/")
                tmp = date(int("20"+year), int(month), int(day))
            except Exception:
                tmp = None
        self.timesheet_start_date:date = tmp

        tmp = None
        while tmp is None:
            tmp = self._get_var(config, "TEST_TIMESHEET_END_DATE", "Enter the end date for your timesheet (MM/DD/YY, ex: 6/30/23): ")
            try:
                month, day, year = tmp.split("/")
                tmp = date(int("20"+year), int(month), int(day))
            except Exception:
                tmp = None
        self.timesheet_end_date:date = tmp

        self.reviewer_email:str = self._get_var(config, "REVIEWER_EMAIL", "Enter reviewer email: ")
        self.supervisor_email:str = self._get_var(config, "SUPERVISOR_EMAIL", "Enter reviewer email: ")
        self.admin_email:str = self._get_var(config, "ADMIN_EMAIL", "Enter reviewer email: ")
        self.cc_email:str = self._get_var(config, "CC_EMAIL", "Enter reviewer email: ")

    def _get_var(self, config:dict, var_name:str, missing_prompt:str):
        value = config.get(var_name)
        while value is None or value == "":
            value = input(missing_prompt)
        return value