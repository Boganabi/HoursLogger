
from datetime import datetime, date, timedelta
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

class TimeSheetDate:
    'An object to represent what will be put on the timesheet'

    def __init__(self, sheetDate, timeIn, timeOut, hours, b):
        newDate = sheetDate.split("/") # passed in as a m/d/yyyy
        self.useDate = datetime(int(newDate[2]), int(newDate[0]), int(newDate[1])) # to make sure its proper date
        self.timeIn = timeIn # note that these times are not in military time as of construction, call getMilitaryTime to get that
        self.timeOut = timeOut # times passed in as hh:mm am/pm
        self.hours = hours
        self.isEndOfWeek = b

    def getDayWeek(self): # can be used with dayIntToString to get name of day instead of int
        return self.useDate.weekday() # monday = 0, sunday = 6
    
    def getPrintableDate(self):
        m = int(self.useDate.month)
        d = int(self.useDate.day)
        if(m < 10):
            m = "0" + str(m)
        if(d < 10):
            d = "0" + str(d)
        return str(m) + "/" + str(d)
    
    def getMilitaryTime(self, time): # passed in as hh:mm am/pm, no space for some reason???
        # separate time into hh:mm and am/pm
        hour = ""
        ind = len(time) - 2
        for i in range(ind):
            hour += time[i]
        # maybe theres a better solution to the above? kinda wacky tbh
        t = hour.split(":")
        if(time[ind] == "P" and int(t[0]) != 12): # checks if it is PM or AM
            t[0] = int(t[0]) + 12

        return str(t[0]) + "." + t[1] # returned as hh:mm

    # make def for changing minutes into a decimal of hour
    def getMinuteRatio(self, time): # do note that the military time must be passed into here, otherwise it may not work
        # first split up
        t = time.split(":")
        minute = (float(t[1]) / 60.0) * 100.0 # always getting 0 for some reason
        if(minute < 10):
            minute = str(minute)
            minute = "0" + minute[0:2]
        minute = str(minute)
        minute = minute[0:2]
        return str(t[0]) + "." + minute

    def getTimeSheetTimeIn(self):
        return self.getMilitaryTime(self.timeIn)
    
    def getTimeSheetTimeOut(self):
        return self.getMilitaryTime(self.timeOut)

    def print(self):
        print()
        print("Day: " + str(self.getDayWeek()))
        print("Date: " + self.getPrintableDate())
        print("Time in: " + self.getMilitaryTime(self.timeIn))
        print("Time out: " + self.getMilitaryTime(self.timeOut))
        print("Total hours: " + str(self.hours))
        print()

"""
# devMode = True
# if(devMode):
#     # employee ID
#     eid = "7247156"

#     # adobe sign email
#     asemail = "logan.ashbaugh7156"

#     # school ID
#     sid = "007247156"

#     # units enrolled
#     uni = "15" 

#     # start date
#     sdate = "1/10/2023" 
#     nstart = sdate.split("/")
#     begTimeSheet = datetime(int(nstart[2]), int(nstart[1]), int(nstart[0]))

#     # end date
#     edate = "31/10/2023"
#     nend = edate.split("/")
#     endTimeSheet = datetime(int(nend[2]), int(nend[1]), int(nend[0]))

# else:
#     # employee ID
#     eid = input("Enter your employee ID number: ")

#     # adobe sign email
#     asemail = input("Enter your adobe sign email (omit the @coyote.csusb.edu): ")

#     # school ID
#     sid = input("Enter your school ID number: ")

#     # units enrolled
#     uni = input("Enter the amount of units you are currently enrolled in: ")

#     # start date
#     sdate = input("Enter the start date for your timesheet in DD/MM/YYYY format, omit leading 0's (ex: 21/7/2022): ")
#     nstart = sdate.split("/")
#     begTimeSheet = datetime(int(nstart[2]), int(nstart[1]), int(nstart[0]))

#     # end date
#     edate = input("Enter the end date for your timesheet in DD/MM/YYYY format, omit leading 0's (ex: 21/7/2022): ")
#     nend = edate.split("/")
#     endTimeSheet = datetime(int(nend[2]), int(nend[1]), int(nend[0]))
"""
# using the file reading solution here
eid = asemail = sid = uni = sdate = edate = reviewer = supervisor = admin = cc = "" 

infoArray = []

# use this instead of open function bc this way file will automatically close
with open('inputs.txt') as f:

    # parse file into each variable
    for x in f:
        # skip "comment" lines and empty lines
        if(x[0] and x[0] not in ["#", "\n"]):
            infoArray.append(x)

# parse values out of array
eid, asemail, sid, uni, sdate, edate, reviewer, supervisor, admin, cc = infoArray

# parse into date objects
sdate = sdate.split("/")
edate = edate.split("/")
begTimeSheet = datetime(int(sdate[2]), int(sdate[1]), int(sdate[0]))
endTimeSheet = datetime(int(edate[2]), int(edate[1]), int(edate[0]))

def checkDate(dateRange): # return a number corresponding to the state that the current page is on relative to the time sheet dates
    dateList = dateRange.split(" ")
    first = dateList[0].split("/")
    second = dateList[2].split("/") # we get the 2nd element bc the one before is just a -
    # begDate = datetime(date.today().year, int(first[0]), int(first[1]))
    # endDate = datetime(date.today().year, int(second[0]), int(second[1]))
    begDate = datetime(begTimeSheet.year, int(first[0]), int(first[1]))
    endDate = datetime(endTimeSheet.year, int(second[0]), int(second[1]))

    # if((begTimeSheet >= begDate and begTimeSheet <= endDate) or begTimeSheet == begDate or begTimeSheet == endDate):
    if(begTimeSheet >= begDate and begTimeSheet <= endDate):
        return 0
    elif(begTimeSheet < begDate or begDate.month == 1 and begTimeSheet.month == 12): # bad, we are too far forward, we need to move back
        # the second or statement is an edge case where current month is january but timesheet dates are in december and need to move back
        return -1
    else: # bad, we are too far back and need to move forward
        return 1

def pageBack():
    prevButton = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "Previous"))
    prevButton.click()

def pageForward():
    forwButton = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "Next"))
    forwButton.click()

def isDateInRange(inDate): # returns true if date is is the range we want to scrape
    dateList = inDate.split(" ") # index 0 is m/d/yyyy, 1 is time, 2 is am/pm
    currDate = dateList[0].split("/")
    dateCheck = datetime(int(currDate[2]), int(currDate[0]), int(currDate[1]))
    return begTimeSheet <= dateCheck and dateCheck <= endTimeSheet

def checkSecondDate(inDate): # returns true if the second date is out of the range we want to scrape
    dateList = inDate.split(" ")
    second = dateList[2].split("/") # this gives us the second date
    dateOn = datetime(endTimeSheet.year, int(second[0]), int(second[1]))

    if(dateOn.month > endTimeSheet.month):
        return True
    return False

def getMonthFromNumber(month):
    switcher = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    return switcher.get(month, "Invalid")

def dayIntToString(num):
    switcher = {
        0: "MON",
        1: "TUE",
        2: "WED",
        3: "THU",
        4: "FRI",
        5: "SAT",
        6: "SUN",
    }

    return switcher.get(num, "Invalid") # this calls the dictionary and returns invalid (the second argument if nothing is returned)

def truncateYear(date):
    # takes in mm/dd/yyyy and returns mm/dd
    splitDate = date.split("/")
    return splitDate[0] + "/" + splitDate[1]

def findCorrespondingDay(day, inc):
    strDay = dayIntToString(day)
    for i in range(0, len(sheetRange)):
        if (strDay == str(sheetRange[i].get_attribute('data-fieldname'))[4:7]):
            if (inc == 0):
                return i
            inc = inc - 1

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=Options())

driver.get("https://61783.tcplusondemand.com/app/webclock/#/EmployeeLogOn/61783")

box = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.ID, "LogOnEmployeeId"))
time.sleep(2) # sleep here bc sometimes javascript hasnt loaded yet, even if page is loaded
box.send_keys(eid) # employee sign in ID goes here
box.send_keys(Keys.ENTER)

viewButton = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "View"))
viewButton.click()

hoursButton = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "ViewHours"))
hoursButton.click()

rangeInt = 2
while(rangeInt != 0):
    time.sleep(0.2) # this sleep is necessary bc we are scraping the wrong date when we let the scraper go without it
    dateRange = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME, "PeriodTotal")).text
    rangeInt = checkDate(dateRange)
    if(rangeInt == -1):
        pageBack()
    if(rangeInt == 1):
        pageForward()

# now that we are on the right date, we can begin scraping data
# refactor to use dictionary instead
listOfDates = [] 
# information i want in the dict:
# week number and day of the week
datesDict = {}

bGatherDates = True
while(bGatherDates):
    time.sleep(0.2) # small sleep so that the right dates are scraped, can cause issues in loop if no sleep
    # rows = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.TAG_NAME, "tr")) # list of all timestamps
    table = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.XPATH, "//*[@id=\"featureForm\"]/div[2]/div/table/tbody"))
    rows = table.find_elements(By.TAG_NAME, "tr")
    # since there are more than 1 tr elements on the page we need to find the specific one we need
    # 3 is the first tr element, need to find a way to iterate to the last tr that we need
    # elements 7 - 19 are trs that we do not want
    for i, element in enumerate(rows):
        time.sleep(0.2) # getting invalid elements without this >:(
        # print(len(rows))
        # changed below to 13 instead of 12 bc website changed ig
        # if(i >= 3 and i < len(rows) - 12): # since there are 12 extra tr elements we dont want, and 2 before that we also dont want
        if(i < len(rows) - 1): # 1 extra tr at end of table
            items = element.find_elements(By.TAG_NAME, "td") # row is an element (but also a list) in the above list, index 6 = time in, 7 = time out, 8 = hours
            if(len(items) < 10):
                print(len(items))
                for thing in items:
                    print(thing)
                    print(thing.text)
            # need to make check for when the hidden element is there or not, and if not then subtract index by 1
            checkedIndex = 0
            if(items[10].text == "5 - ATI Student Assistant"):
                checkedIndex = -1
            
            dateToCheck = items[6 + checkedIndex].text
            if(isDateInRange(dateToCheck)): 
                # store this value in a list of objects with date, time in, time out, and hours
                # first seperate the dates from the times 
                dateIn = dateToCheck.split(" ") # we grab the date from here and not from the time out, formatted as mm/dd/yyyy hh:mm am/pm
                dateOut = items[7 + checkedIndex].text.split(" ")

                # create object and add to list
                listOfDates.append(TimeSheetDate(dateIn[0], str(dateIn[1]) + str(dateIn[2]), str(dateOut[1]) + str(dateOut[2]), items[8 + checkedIndex].text, i == len(rows) - 14))
                # need to check if the key exists first, then add a second value as a list if it does exist
                if truncateYear(dateIn[0]) in datesDict:
                    datesDict[truncateYear(dateIn[0])].append(TimeSheetDate(dateIn[0], str(dateIn[1]) + str(dateIn[2]), str(dateOut[1]) + str(dateOut[2]), items[8 + checkedIndex].text, i == len(rows) - 14))
                else:
                    datesDict[truncateYear(dateIn[0])] = [TimeSheetDate(dateIn[0], str(dateIn[1]) + str(dateIn[2]), str(dateOut[1]) + str(dateOut[2]), items[8 + checkedIndex].text, i == len(rows) - 14)]
            else:
                secDate = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME, "PeriodTotal")).text # need the top date range
                if(checkSecondDate(secDate)): 
                    # if this is false then we are on the first page and shouldnt break loop, 
                    # but if its true then we should break because we are out of the range of dates we need to gather
                    # this should break the loop and put dates
                    bGatherDates = False
                    break
        elif (element.text == "No records found"):
            secDate = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME, "PeriodTotal")).text # need the top date range
            if(checkSecondDate(secDate)): 
                # if this is false then we are on the first page and shouldnt break loop, 
                # but if its true then we should break because we are out of the range of dates we need to gather
                # this should break the loop and put dates
                bGatherDates = False
                break
    pageForward()

# since listOfDates has all the data we need, we can now put all data in the adobe timesheet

driver.get("https://csusbsign.na2.documents.adobe.com/account/customComposeJs?workflowid=CBJCHBCAABAAIfLxRZ7xj7zi7uLegFYwKypc4N7ZcGop")

# signs into adobe sign
user = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.ID, "EmailPage-EmailField"))
user.send_keys(str(asemail) + "@coyote.csusb.edu") # email goes here
user.send_keys(Keys.ENTER)

print("\nPlease sign in to your mycoyote account to continue...\n") # i do this instead of automatically signing in bc entering passwords could be bad

# enters the needed items
# this find thing is pretty annoying but its the only thing that works >:(
reviewerBox = WebDriverWait(driver, timeout=1000).until(lambda d: d.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[2]/div[2]/div/div[2]/div[3]/div/div/div[1]/textarea"))
reviewerBox.send_keys("marcy.iniguez@csusb.edu") # reviewer box

supervisorBox = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[2]/div[3]/div/div[2]/div[3]/div/div/div[1]/textarea")
supervisorBox.send_keys("bobby.laudeman@csusb.edu") # supervisor box

adminBox = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[2]/div[4]/div/div[2]/div[3]/div/div/div[1]/textarea")
adminBox.send_keys("jamest@csusb.edu") # admin box

ccBox = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[4]/div[4]/div/div/div[2]/div/div[1]/textarea")
ccBox.send_keys("ashleea.holloway@csusb.edu") # CC box

signButton = driver.find_element(By.XPATH, "//*[@id=\"mainContent\"]/div[2]/div/div[6]/div/ul/li/button")
signButton.send_keys(Keys.PAGE_DOWN) # need to scroll to button bc element is blocking it
signButton.click()

# finally at the part where the timesheet is filled out

# first field: coyote id
cid = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.NAME, "COYOTE ID"))
cid.send_keys(str(sid)) # ID goes here

# second field: rate of pay
payrate = driver.find_element(By.NAME, "PAY_RATE")
payrate.send_keys("16.00")

# third field: month and year of timesheet
mon = driver.find_element(By.NAME, "MONTH  YEAR OF TIMESHEET")
mon.send_keys(str(getMonthFromNumber(begTimeSheet.month)) + " " + str(begTimeSheet.year))

# fourth field: student job title
jobTitle = driver.find_element(By.NAME, "STUDENT JOB TITLE")
jobTitle.send_keys("Student Assistant")

# fifth field: department
dept = driver.find_element(By.NAME, "DEPARTMENT")
dept.send_keys("MIT")

# sixth field: unit enrollment
units = driver.find_element(By.NAME, "Current Unit Enrollment")
units.send_keys(str(uni))

# now we fill out the times and dates
# can try getting all the elements of class 'pdfFormField text_field todo-done'?
sheetRange = driver.find_elements(By.CLASS_NAME, "todo-done")

# for some [heck]ing reason the fourth tuesday isnt added, so here is an attempt to add it manually
badTues = driver.find_element(By.XPATH, "//*[@id=\"document\"]/ul/li/div[191]")
indBeforeBadTues = driver.find_element(By.XPATH, "//*[@id=\"document\"]/ul/li/div[188]")
badInd = sheetRange.index(indBeforeBadTues)
sheetRange.insert(badInd + 1, badTues)

useDict = True
if useDict:

    # need to remove the stray boxes from the list (indicies 0-3, 19, 35, 51)
    # extraIndicies = [0, 1, 2, 3, 4, 10, 11, 12, 13, 19, 35, 51]
    # offset = 0

    # kinda a terrible way to do this but it works so????
    dateIndices = [4, 9, 14, 20, 25, 30, 36, 41, 46, 52, 57, 62, 67, 72, 77, 82, 87, 92, 97, 102, 107, 112, 117, 122, 127, 132, 137, 142, 147, 152, 157, 162, 167, 172, 177]
    
    firstDate = list(datesDict.keys())[0].split("/")
    currDate = datetime(datetime.today().year, int(firstDate[0]), int(firstDate[1])) # year is not important

    # convert list to dictionary
    for i, item in enumerate(sheetRange):#, start=(5 * currDate.weekday())):
        # print((i - offset) % 5)
        # if (i - offset) % 5 == 0: # makes sure we are on a box expecting a date entry
        if i in dateIndices:
            
            # insert hours worked for that day
            strDate = str(currDate.month) + "/" + str(currDate.day)
            if strDate not in datesDict: 
                print("failed:", strDate)
                # increment day
                currDate += timedelta(days=1)
                continue

            # print(strDate)
            times = datesDict[strDate]
            if len(times) > 0:
                print(i)
                writeableBox = item.find_element(By.CLASS_NAME, "text_field_input")
                # write date
                writeableBox.send_keys(times[0].getPrintableDate())
                
                # write times
                writeableBox = sheetRange[i + 1].find_element(By.CLASS_NAME, "text_field_input")
                writeableBox.send_keys(times[0].getTimeSheetTimeIn())
                writeableBox = sheetRange[i + 2].find_element(By.CLASS_NAME, "text_field_input")
                writeableBox.send_keys(times[0].getTimeSheetTimeOut())
                print(i + 1)
                print(i + 2)

                if len(times) == 2: # second time for clock in/out
                    writeableBox = sheetRange[i + 3].find_element(By.CLASS_NAME, "text_field_input")
                    writeableBox.send_keys(times[1].getTimeSheetTimeIn())
                    writeableBox = sheetRange[i + 4].find_element(By.CLASS_NAME, "text_field_input")
                    writeableBox.send_keys(times[1].getTimeSheetTimeOut())
                    print(i + 3)
                    print(i + 4)
            # increment day
            currDate += timedelta(days=1)
            print(strDate)

        # try:
        #     item.find_element(By.CLASS_NAME, "text_field_input").send_keys(str(i))
        # except:
        #     print("Bad box:", i)
        
else:

    # strategy: get day of the week in listOfDates, find corresponding element in sheetRange. 
    # have a counter for each day, and depending on that count fill out corresponding box
    dayCounterList = [0, 0, 0, 0, 0, 0, 0] # each index corresponds to a day of the week
    for j in range(0, len(listOfDates)):
        dayOfWeek = listOfDates[j].getDayWeek()
        # check if date we are on matches previous date
        if(j != 0 and listOfDates[j].getPrintableDate() == listOfDates[j - 1].getPrintableDate()):
            # get child so that element is interactable
            ranInt = findCorrespondingDay(dayOfWeek, dayCounterList[dayOfWeek] - 1)
            tiBox2 = sheetRange[ranInt + 3].find_element(By.CLASS_NAME, "text_field_input")
            toBox2 = sheetRange[ranInt + 4].find_element(By.CLASS_NAME, "text_field_input")

            # put hours into other two boxes
            tiBox2.send_keys(listOfDates[j].getTimeSheetTimeIn())
            toBox2.send_keys(listOfDates[j].getTimeSheetTimeOut())

        else:
            # get child of each box so we can input into it
            ranInt = findCorrespondingDay(dayOfWeek, dayCounterList[dayOfWeek])
            dateBox = sheetRange[ranInt].find_element(By.CLASS_NAME, "text_field_input")
            tiBox = sheetRange[ranInt + 1].find_element(By.CLASS_NAME, "text_field_input")
            toBox = sheetRange[ranInt + 2].find_element(By.CLASS_NAME, "text_field_input")

            # put new date and hours in
            dateBox.send_keys(listOfDates[j].getPrintableDate())
            tiBox.send_keys(listOfDates[j].getTimeSheetTimeIn())
            toBox.send_keys(listOfDates[j].getTimeSheetTimeOut())

            # increment number in day counter list
            dayCounterList[dayOfWeek] += 1
        
        # make sure days are put on the right week
        if(listOfDates[j].isEndOfWeek):
            for t in range(0, len(dayCounterList)):
                if(t <= dayOfWeek):
                    if (dayCounterList[t] < dayCounterList[dayOfWeek]):
                        # dayCounterList[t] = dayCounterList[dayOfWeek]
                        dayCounterList[t] += 1
                else:
                    # here, the day is in the future so we check if its behind by 2, since being behind by 1 is normal
                    if (dayCounterList[t] < dayCounterList[dayOfWeek] + 1):
                        # dayCounterList[t] = dayCounterList[dayOfWeek]
                        dayCounterList[t] += 1

# time.sleep(10)

# driver.quit()