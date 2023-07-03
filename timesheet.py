from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class TimeSheet:
    def __init__(self):
        self.form_element:WebElement = None
        self.form:list[dict[int, tuple[WebElement,WebElement,WebElement,WebElement,WebElement]]] = []
    
    def grab_form(self, driver:WebDriver):
        self.form_element:WebElement = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "document"))

        self.form:list[dict[int, tuple[WebElement,WebElement,WebElement,WebElement,WebElement]]] = []
        for week in range(5):
            form_week = {}
            for weekday in range(7):
                date_element = self.get_date_element(week, weekday)
                tito_element = self.get_time_in_out_elements(week, weekday)
                form_week[weekday] = (date_element, *tito_element)
            self.form.append(form_week)

    def get_date_element(self, week:int, weekday:int) -> WebElement:
        """weeks[0,4], weekday[0=Mon,6=Sun]"""
        weekday_name_lookup = {
            0: "MONDAY",
            1: "TUESDAY",
            2: "WEDNESDAY",
            3: "THURSDAY",
            4: "FRIDAY",
            5: "SATURDAY",
            6: "SUNDAY"
        }
        week_suffix_lookup = {
            0: "",
            1: "_2",
            2: "_3",
            3: "_4",
            4: "_5"
        }
        weekday_name = weekday_name_lookup[weekday]
        week_suffix = week_suffix_lookup[week]
        return self.form_element.find_element(By.NAME, f"DATE{weekday_name + week_suffix}")
    
    def get_time_in_out_elements(self, week:int, weekday:int) -> tuple[WebElement,WebElement,WebElement,WebElement]:
        """weeks[0,4], weekday[0=Mon,6=Sun]"""
        week_fields_lookup = {
            0: ("A", "B", "C", "D"),
            1: ("E", "F", "G", "H"),
            2: ("I", "J", "K", "L"),
            3: ("M", "N", "O", "P"),
            4: ("Q", "R", "S", "T")
        }

        week_fields = week_fields_lookup[week]
        elements:list[WebElement] = []
        for field in week_fields:
            elements.append(self.form_element.find_element(By.NAME, f"{field + str(weekday)}"))
        return tuple(elements)
