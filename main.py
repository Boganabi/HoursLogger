from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from datetime import date, datetime
from config import Config
from hour_tracking import WorkWeek, WorkDay, ShiftTime
from timesheet import TimeSheet

def main():
    try:
        # Initialize config
        print("Loading config...")
        config = Config()

        # Initialize driver (browser)
        print("Starting web browser...")
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        service = Service(executable_path=ChromeDriverManager().install())
        driver = Chrome(service=service, chrome_options=chrome_options)

        # Goto time clock size
        print("Going to time clock website...")
        driver.get("https://61783.tcplusondemand.com/app/webclock/#/EmployeeLogOn/61783")

        # get hours
        print("Scraping hours...")
        login_and_navigate_to_hours(config, driver)
        hours:list[WorkWeek] = scrape_hours(config, driver)

        # Goto adobe sign
        print("Going to adobe sign...")
        driver.get("https://csusbsign.na2.documents.adobe.com/account/customComposeJs?workflowid=CBJCHBCAABAAIfLxRZ7xj7zi7uLegFYwKypc4N7ZcGop")

        # fill out adobe sign form
        print("Logging into adobe sign...")
        adobe_sign_login(config, driver)
        print("Filling out adobe sign info...")
        adobe_sign_form_fill(config, driver)

        # fill out time sheet
        print("Filling out basic info...")
        fill_out_timesheet_basic(config, driver)
        print("Filling out hours...")
        fill_out_timesheet_hours(config, driver, hours)

    except Exception as e:
        print("An error has occured")
        print(e)
        print(" ")
    finally:
        pause_execution()
        print("End of execution.")


def pause_execution():
    input("Paused. (Press Enter to continue)")

def login_and_navigate_to_hours(config:Config, driver:WebDriver):
    box:WebElement = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.ID, "LogOnEmployeeId"))
    sleep(2) # sleep here bc sometimes javascript hasnt loaded yet, even if page is loaded
    box.send_keys(config.employee_id) # employee sign in ID goes here
    box.send_keys(Keys.ENTER)
    viewButton:WebElement = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "View"))
    viewButton.click()
    hoursButton:WebElement = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "ViewHours"))
    hoursButton.click()

def scrape_hours(config:Config, driver:WebDriver) -> list[WorkWeek]:
    def page_older(driver:WebDriver=driver):
        sleep(0.2)
        button:WebElement = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "Previous"))
        button.click()

    def page_newer(driver:WebDriver=driver):
        sleep(0.2)
        button:WebElement = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "Next"))
        button.click()

    def get_date_range_str(driver:WebDriver=driver) -> str:
        sleep(0.2) # this sleep is necessary bc we are scraping the wrong date when we let the scraper go without it
        return WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME, "PeriodTotal")).text

    def parse_date_range_str(date_range_str:str) -> tuple[date, date]:
        # format "06/26 - 07/02"
        start_date_str, end_date_str = date_range_str.split(" - ")
        start_date = datetime.strptime(start_date_str, "%m/%d").date()
        end_date = datetime.strptime(end_date_str, "%m/%d").date()
        return (start_date, end_date)
    
    def get_date_range() -> tuple[date, date]:
        return parse_date_range_str(get_date_range_str())
    
    def date_less_than(date1:date, date2:date) -> bool:
        """Compares date only on month and day"""
        return (date1.month < date2.month) or (date1.month == date2.month and date1.day < date2.day)
    
    def day_int_to_string(day:int):
        switcher = {
            0: "MON",
            1: "TUE",
            2: "WED",
            3: "THU",
            4: "FRI",
            5: "SAT",
            6: "SUN",
        }
        return switcher.get(day, "Invalid") # this calls the dictionary and returns invalid (the second argument if nothing is returned)

    # goto start of range
    while True:
        start_date, end_date = get_date_range()
        if date_less_than(config.timesheet_start_date, start_date):
            page_older()
        else:
            break

    # scrape hours
    hours:list[WorkWeek] = []
    while True:
        # scrape
        sleep(1) # slightly bigger sleep bc slow loading

        # narrow scope to parent element of rows of table
        table:WebElement = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME, "WorkSegmentGrid"))
        tbody:WebElement = table.find_element(By.TAG_NAME, "tbody")
        trows:list[WebElement] = tbody.find_elements(By.TAG_NAME, "tr")[:-1]
        no_records:bool = tbody.find_element(By.CLASS_NAME, "NoRecordsRow").is_displayed()

        start_date, end_date = get_date_range()
        if not no_records:
            week = WorkWeek()
            for tr in trows:
                data_elems = tr.find_elements(By.CLASS_NAME, "ng-binding")
                data = [d.text for d in data_elems]
                try:
                    week.add_shift(ShiftTime(data[0], data[1], data[2]))
                except Exception:
                    pass
            week.trim_outside_range(config.timesheet_start_date, config.timesheet_end_date)
            week.trim_empty_days()
            if not week.is_empty():
                hours.append(week)

        # end reached?
        if date_less_than(end_date, config.timesheet_end_date):
            page_newer()
        else:
            for work_week in hours:
                print("New week")
                for key, work_day in work_week.work_days.items():
                    print({day_int_to_string(key): work_day.get_form_info()})
            return hours

def adobe_sign_login(config:Config, driver:WebDriver):
    # signs into adobe sign
    user:WebElement = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "EmailPage-EmailField"))
    user.send_keys(config.adobe_sign_email + "@coyote.csusb.edu") # email goes here
    user.send_keys(Keys.ENTER)

    print("\nPlease sign in to your mycoyote account to continue...\n") # i do this instead of automatically signing in bc entering passwords could be bad

def adobe_sign_form_fill(config:Config, driver:WebDriver):
    # enters the needed items
    # this find thing is pretty annoying but its the only thing that works >:(
    reviewerBox:WebElement = WebDriverWait(driver, timeout=1000).until(lambda d: d.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[2]/div[2]/div/div[2]/div[3]/div/div/div[1]/textarea"))
    reviewerBox.send_keys(config.reviewer_email) # reviewer box

    supervisorBox = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[2]/div[3]/div/div[2]/div[3]/div/div/div[1]/textarea")
    supervisorBox.send_keys(config.supervisor_email) # supervisor box

    adminBox = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[2]/div[4]/div/div[2]/div[3]/div/div/div[1]/textarea")
    adminBox.send_keys(config.admin_email) # admin box

    ccBox = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[4]/div/div/div[2]/div/div[1]/textarea")
    ccBox.send_keys(config.cc_email) # CC box

    signButton = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[6]/div/ul/li/button")
    signButton.send_keys(Keys.PAGE_DOWN) # need to scroll to button bc element is blocking it
    sleep(.3)
    signButton.click()

def fill_out_timesheet_basic(config:Config, driver:WebDriver):
    # first field: coyote id
    cid:WebElement = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.NAME, "COYOTE ID"))
    cid.send_keys(config.school_id) # ID goes here

    # second field: rate of pay
    payrate = driver.find_element(By.NAME, "PAY_RATE")
    payrate.send_keys("15.50")

    # third field: month and year of timesheet
    mon = driver.find_element(By.NAME, "MONTH  YEAR OF TIMESHEET")
    mon.send_keys(config.timesheet_start_date.strftime("%B %Y"))

    # fourth field: student job title
    jobTitle = driver.find_element(By.NAME, "STUDENT JOB TITLE")
    jobTitle.send_keys("Student Assistant")

    # fifth field: department
    dept = driver.find_element(By.NAME, "DEPARTMENT")
    dept.send_keys("ITS ATI")

    # sixth field: unit enrollment
    units = driver.find_element(By.NAME, "Current Unit Enrollment")
    units.send_keys(config.units_enrolled)

def fill_out_timesheet_hours(config:Config, driver:WebDriver, hours:list[WorkWeek]):
        timesheet = TimeSheet()
        timesheet.grab_form(driver)

        for i, workweek in enumerate(hours):
            for weekday, workday in workweek.work_days.items():
                info = workday.get_form_info()
                if info is not None:
                    (date_info, clockin1_info, clockout1_info, clockin2_info, clockout2_info) = info
                    (date_field, clockin1_field, clockout1_field, clockin2_field, clockout2_field) = timesheet.form[i][weekday]

                    date_field.send_keys(date_info)

                    clockin1_field.send_keys(clockin1_info)
                    clockout1_field.send_keys(clockout1_info)

                    if clockin2_info is not None:
                        clockin2_field.send_keys(clockin2_info)
                    if clockout2_info is not None:
                        clockout2_field.send_keys(clockout2_info)

if __name__ == "__main__":
    main()