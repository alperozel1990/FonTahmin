from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import re
from datetime import date
from datetime import datetime, timedelta

def days_between(d1, d2):
    # d1 = datetime.strptime(d1, "%Y-%m-%d")
    # d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (d2 - d1).days

def dater(date):
    # splittedDate = date.split('-')
    # year = splittedDate[0]
    # month = splittedDate[1]
    # day = splittedDate[2].split(' ')[0]
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    return day + '.' + month + '.' + year

tarihselVeriPage = "https://www.tefas.gov.tr/TarihselVeriler.aspx"
startDateDiv = "ctl00$MainContent$TextBoxStartDate"
stopDateDiv = "ctl00$MainContent$TextBoxEndDate"
numOfDataOnPageName = "table_general_info_length"
numOfDataOnDistrPageName = "table_allocation_length"
searchDatesButtonName = "ctl00$MainContent$ButtonSearchDates"
listedTableClassName= "display dataTable no-footer"
driver = webdriver.Chrome(executable_path=r'D:\Users\26015017\chromedriver.exe')
driver.get("https://www.tefas.gov.tr/TarihselVeriler.aspx")

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
today = datetime.now() 
one_year_days = 365
three_months_days = 90
# n_days_ago = today - timedelta(days=5)
# print("today, 5 days ago: ", dater(today), dater(n_days_ago))
gap_start_date = today - timedelta(days = one_year_days*5 - three_months_days)
gap_stop_date = gap_start_date + timedelta(days = three_months_days)

# startDate = driver.find_element_by_name(startDateDiv)
startDate = driver.find_element(By.NAME, startDateDiv)

# stopDate = driver.find_element_by_name(stopDateDiv)
stopDate = driver.find_element(By.NAME, stopDateDiv)

# searchDatesButton = driver.find_element_by_name(searchDatesButtonName)
searchDatesButton = driver.find_element(By.NAME, searchDatesButtonName)

# numOfDataOnPageSelect = Select(driver.find_element_by_name(numOfDataOnPageName))
numOfDataOnPageSelect = Select(driver.find_element(By.NAME, numOfDataOnPageName))


portfoyDagilimTab = driver.find_element(By.XPATH, "//li[@role = 'tab']/a[@id= 'ui-id-2']")

numOfDataOnPageSelect.select_by_value('250')

startDate.clear()
stopDate.clear()
# ActionChains(driver).move_to_element(startDate).click().send_keys('30.10.2016').perform()
# ActionChains(driver).move_to_element(startDate).click().send_keys(dater(today - timedelta(days=one_year_days*5))).perform()
ActionChains(driver).move_to_element(startDate).click().send_keys(dater(gap_start_date)).perform()
# ActionChains(driver).move_to_element(stopDate).click().send_keys('31.10.2016').perform()
# ActionChains(driver).move_to_element(stopDate).click().send_keys(dater(today - timedelta(days=one_year_days*5-three_months_days))).perform()
ActionChains(driver).move_to_element(stopDate).click().send_keys(dater(gap_stop_date)).perform()
ActionChains(driver).move_to_element(searchDatesButton).click().perform()
ActionChains(driver).move_to_element(portfoyDagilimTab).click().perform()
# driver.implicitly_wait(1000)
time.sleep(5)
numOfDataOnDistrPageSelect = Select(driver.find_element(By.NAME, numOfDataOnDistrPageName))
numOfDataOnDistrPageSelect.select_by_value('250')
# time.sleep(2)

# dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/div[@id= 'table_general_info_info']")
# dataCountText = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id = 'table_general_info_wrapper']/div[@id= 'table_general_info_info']")))
# dataCountText = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id = 'table_allocation_wrapper']/div[@id= 'table_allocation_info']")))
dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_allocation_wrapper']/div[@id= 'table_allocation_info']")
# driver.implicitly_wait(10)
# time.sleep(10)
start = datetime.now() 
print("başladı")
# driver.implicitly_wait(10000)
time.sleep(5)
stop = datetime.now() 
print("bitti")
print("saniye: ", (stop - start).seconds)
dataCount = dataCountText.text.split(' ')[0].split('.')
print("dataCount: ", dataCount)
temp = dataCount[0]
for i in range(len(dataCount)-1):
    temp += dataCount[i+1]
dataCount = int(temp)

print("dataNum is: ", dataCount)

# listedTable = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']").get_attribute('outerHTML')
listedTableDagilim = driver.find_element(By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']").get_attribute('outerHTML')

# df_listedTable  = pd.read_html(listedTable)
df_listedTable  = pd.read_html(listedTableDagilim)


if(dataCount > 250):
    # nextButton = driver.find_element(By.XPATH, "//div[@id='table_general_info_paginate']/a[@id = 'table_general_info_next']")
    # driver.implicitly_wait(1) 
    
    pageCount = int(dataCount / 250)
    for i in range(pageCount):
        # time.sleep(10)
        
        # driver.refresh()
        # nextButton = driver.find_element(By.XPATH, "//div[@id='table_general_info_paginate']/a[@id = 'table_general_info_next']")

        # nextButton = driver.find_element(By.XPATH, "//div[@id='table_allocation_paginate']/a[@id = 'table_allocation_next']")
        nextButton = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id='table_allocation_paginate']/a[@id = 'table_allocation_next']")))
        driver.implicitly_wait(1) 
        time.sleep(1)
        # ActionChains(driver).move_to_element(nextButton).click(nextButton).perform()
        ActionChains(driver).move_to_element(nextButton).perform()
        driver.execute_script('arguments[0].click()', nextButton)
        driver.implicitly_wait(20) 
        time.sleep(1)
        # tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']"))).get_attribute('outerHTML')
        tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']"))).get_attribute('outerHTML')
        # tempTableHTML = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']").get_attribute('outerHTML')
        time.sleep(1)
        tempTable = pd.read_html(tempTableHTML)
        df_listedTable[0] = df_listedTable[0].append(tempTable[0])
        # driver.implicitly_wait(1) 
        time.sleep(1)
        print("pageNum: ", i, " is OK")

date_diff = days_between(gap_stop_date, today)

# while(False):
while(date_diff > 4):
    gap_start_date = gap_stop_date
    gap_stop_date = gap_start_date + timedelta(days = three_months_days)
    
    startDate = driver.find_element(By.NAME, startDateDiv)
    stopDate = driver.find_element(By.NAME, stopDateDiv)
    searchDatesButton = driver.find_element(By.NAME, searchDatesButtonName)
    # numOfDataOnPageSelect = Select(driver.find_element(By.NAME, numOfDataOnPageName))
    portfoyDagilimTab = driver.find_element(By.XPATH, "//li[@role = 'tab']/a[@id= 'ui-id-2']")
    # numOfDataOnPageSelect.select_by_value('250')
    numOfDataOnDistrPageSelect = Select(driver.find_element(By.NAME, numOfDataOnDistrPageName))
    numOfDataOnDistrPageSelect.select_by_value('250')
    startDate.clear()
    stopDate.clear()
    ActionChains(driver).move_to_element(startDate).click().send_keys(dater(gap_start_date)).perform()
    ActionChains(driver).move_to_element(stopDate).click().send_keys(dater(gap_stop_date)).perform()
    ActionChains(driver).move_to_element(searchDatesButton).click().perform()
    ActionChains(driver).move_to_element(portfoyDagilimTab).click().perform()
    time.sleep(10)
    # driver.implicitly_wait(10)
    # dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/div[@id= 'table_general_info_info']")
    dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_allocation_wrapper']/div[@id= 'table_allocation_info']")
    time.sleep(5)
    dataCount = dataCountText.text.split(' ')[0].split('.')
    print("dataNum is: ", dataCount)
    temp = dataCount[0]
    for i in range(len(dataCount)-1):
        temp += dataCount[i+1]
    dataCount = int(temp)
    print("dataNum is: ", dataCount)
    # listedTable = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']").get_attribute('outerHTML')
    listedTableDagilim = driver.find_element(By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']").get_attribute('outerHTML')
    # tempTable = pd.read_html(listedTable)
    tempTable = pd.read_html(listedTableDagilim)
    df_listedTable[0] = df_listedTable[0].append(tempTable[0])
    if(dataCount > 250):    
        pageCount = int(dataCount / 250)
        for i in range(pageCount):
            # nextButton = driver.find_element(By.XPATH, "//div[@id='table_general_info_paginate']/a[@id = 'table_general_info_next']")
            # nextButton = driver.find_element(By.XPATH, "//div[@id='table_allocation_paginate']/a[@id = 'table_allocation_next']")
            nextButton = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id='table_allocation_paginate']/a[@id = 'table_allocation_next']")))
            driver.implicitly_wait(1) 
            # ActionChains(driver).move_to_element(nextButton).click().perform()
            ActionChains(driver).move_to_element(nextButton).perform()
            driver.execute_script('arguments[0].click()', nextButton)
            driver.implicitly_wait(20) 
            # tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']"))).get_attribute('outerHTML')
            tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']"))).get_attribute('outerHTML')
            tempTable = pd.read_html(tempTableHTML)
            df_listedTable[0] = df_listedTable[0].append(tempTable[0])
            driver.implicitly_wait(1) 
    
    date_diff = days_between(gap_stop_date, today)
    
# df_listedTable[0].to_csv('5YearsGeneralSummary.csv')
df_listedTable[0].to_csv('5YearsDistribution.csv')
    
for i in df_listedTable[0]:
    print(i, "\n")


