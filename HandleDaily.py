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
from db.fonDb import fonDb
import time
import re
from datetime import date
from datetime import datetime, timedelta
import csv
from tabulate import tabulate
from itertools import islice
import numpy as np
import shelve
import os
import sys
sys.path.insert(0, "..")

# Get the data in order, ascending by the date
# Create Date column which is readable and rankable: eg.2021.05.23
# Starting from the last data, fix the 1/10 and 1/100 issues. İf a data is more than 9x then fix it by either multiplying or dividing by the powers of 10

def days_between(d1, d2):
    return (d2 - d1).days

def dater(date):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    return day + '.' + month + '.' + year

def readDate(strA):
    datetime_object = datetime.strptime(strA, '%d.%m.%Y')
    return datetime_object.date()
    
def readnewDate(strA):
    datetime_object = datetime.strptime(strA, '%Y-%m-%d')
    return datetime_object.date()

def find_ind(dictA, keyA, wordA):
    for i in range(len(dictA[keyA])):
        if dictA[keyA][i] == wordA:
            return [True, i]
    return [False, 0]
    

        
    

############################################

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
p = Path(__file__)
daily_mem_path = 'mem\\dailyFonDb'
dbPath = os.path.join(p, 'mem\\dailyFonDb')
last_date_on_db = None
with shelve.open(dbPath, writeback=True) as dailyFonDb:
    if len(dailyFonDb['newTarih']) >= 1:
        last_date_on_db = dailyFonDb['newTarih'][-1]
        gap_start_date = readnewDate(dailyFonDb['newTarih'][-1]) - timedelta(days = 1)
    else:
        gap_start_date = today - timedelta(days = one_year_days*5 - 1)
        last_date_on_db = gap_start_date
dailyFonDb.close()
if today - gap_start_date < timedelta(days = three_months_days):
    gap_stop_date = today
else:
    gap_stop_date = gap_start_date + timedelta(days = three_months_days)

startDate = driver.find_element(By.NAME, startDateDiv)
stopDate = driver.find_element(By.NAME, stopDateDiv)
searchDatesButton = driver.find_element(By.NAME, searchDatesButtonName)
numOfDataOnPageSelect = Select(driver.find_element(By.NAME, numOfDataOnPageName))
portfoyDagilimTab = driver.find_element(By.XPATH, "//li[@role = 'tab']/a[@id= 'ui-id-2']")
numOfDataOnPageSelect.select_by_value('250')

startDate.clear()
stopDate.clear()
ActionChains(driver).move_to_element(startDate).click().send_keys(dater(gap_start_date)).perform()
ActionChains(driver).move_to_element(stopDate).click().send_keys(dater(gap_stop_date)).perform()
ActionChains(driver).move_to_element(searchDatesButton).click().perform()
ActionChains(driver).move_to_element(portfoyDagilimTab).click().perform()
time.sleep(5)
numOfDataOnDistrPageSelect = Select(driver.find_element(By.NAME, numOfDataOnDistrPageName))
numOfDataOnDistrPageSelect.select_by_value('250')
dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_allocation_wrapper']/div[@id= 'table_allocation_info']") 
dataCount = dataCountText.text.split(' ')[0].split('.')
temp = dataCount[0]
for i in range(len(dataCount)-1):
    temp += dataCount[i+1]
dataCount = int(temp)
listedTableDagilim = driver.find_element(By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']").get_attribute('outerHTML')
df_listedTable  = pd.read_html(listedTableDagilim)


if(dataCount > 250):
    
    pageCount = int(dataCount / 250)
    for i in range(pageCount):
        nextButton = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id='table_allocation_paginate']/a[@id = 'table_allocation_next']")))
        driver.implicitly_wait(1) 
        time.sleep(1)
        ActionChains(driver).move_to_element(nextButton).perform()
        driver.execute_script('arguments[0].click()', nextButton)
        driver.implicitly_wait(20) 
        time.sleep(1)
        tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']"))).get_attribute('outerHTML')
        time.sleep(1)
        tempTable = pd.read_html(tempTableHTML)
        df_listedTable[0] = df_listedTable[0].append(tempTable[0])
        time.sleep(1)

date_diff = days_between(gap_stop_date, today)

while(date_diff > 4):
    gap_start_date = gap_stop_date
    gap_stop_date = gap_start_date + timedelta(days = three_months_days)
    
    startDate = driver.find_element(By.NAME, startDateDiv)
    stopDate = driver.find_element(By.NAME, stopDateDiv)
    searchDatesButton = driver.find_element(By.NAME, searchDatesButtonName)
    portfoyDagilimTab = driver.find_element(By.XPATH, "//li[@role = 'tab']/a[@id= 'ui-id-2']")
    numOfDataOnDistrPageSelect = Select(driver.find_element(By.NAME, numOfDataOnDistrPageName))
    numOfDataOnDistrPageSelect.select_by_value('250')
    startDate.clear()
    stopDate.clear()
    ActionChains(driver).move_to_element(startDate).click().send_keys(dater(gap_start_date)).perform()
    ActionChains(driver).move_to_element(stopDate).click().send_keys(dater(gap_stop_date)).perform()
    ActionChains(driver).move_to_element(searchDatesButton).click().perform()
    ActionChains(driver).move_to_element(portfoyDagilimTab).click().perform()
    time.sleep(10)
    dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_allocation_wrapper']/div[@id= 'table_allocation_info']")
    time.sleep(5)
    dataCount = dataCountText.text.split(' ')[0].split('.')
    temp = dataCount[0]
    for i in range(len(dataCount)-1):
        temp += dataCount[i+1]
    dataCount = int(temp)
    listedTableDagilim = driver.find_element(By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']").get_attribute('outerHTML')
    tempTable = pd.read_html(listedTableDagilim)
    df_listedTable[0] = df_listedTable[0].append(tempTable[0])
    if(dataCount > 250):    
        pageCount = int(dataCount / 250)
        for i in range(pageCount):
            nextButton = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id='table_allocation_paginate']/a[@id = 'table_allocation_next']")))
            driver.implicitly_wait(1) 
            ActionChains(driver).move_to_element(nextButton).perform()
            driver.execute_script('arguments[0].click()', nextButton)
            driver.implicitly_wait(20) 
            tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@class = 'dataTables_scrollBody']/table[@id= 'table_allocation']"))).get_attribute('outerHTML')
            tempTable = pd.read_html(tempTableHTML)
            df_listedTable[0] = df_listedTable[0].append(tempTable[0])
            driver.implicitly_wait(1) 
    
    date_diff = days_between(gap_stop_date, today)

date_time = today.strftime("%Y-%m-%d)
df_listedTable[0].to_csv('//fon_database/'+date_time+'_DailyDistribution.csv')


time.sleep(5)

## Now the general info

startDate.clear()
stopDate.clear()
ActionChains(driver).move_to_element(startDate).click().send_keys(dater(gap_start_date)).perform()
ActionChains(driver).move_to_element(stopDate).click().send_keys(dater(gap_stop_date)).perform()
ActionChains(driver).move_to_element(searchDatesButton).click().perform()
time.sleep(5)
numOfDataOnPageSelect = Select(driver.find_element(By.NAME, numOfDataOnPageName))
numOfDataOnPageSelect.select_by_value('250')
dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/div[@id= 'table_general_info_info']")
dataCount = dataCountText.text.split(' ')[0].split('.')
temp = dataCount[0]
for i in range(len(dataCount)-1):
    temp += dataCount[i+1]
dataCount = int(temp)
listedTable = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']").get_attribute('outerHTML')
df_listedTable  = pd.read_html(listedTable) 


if(dataCount > 250):
    
    pageCount = int(dataCount / 250)
    for i in range(pageCount):
        nextButton = driver.find_element(By.XPATH, "//div[@id='table_general_info_paginate']/a[@id = 'table_general_info_next']")
        driver.implicitly_wait(1) 
        time.sleep(1)
        ActionChains(driver).move_to_element(nextButton).perform()
        driver.execute_script('arguments[0].click()', nextButton)
        driver.implicitly_wait(20) 
        time.sleep(1)
        tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']"))).get_attribute('outerHTML')
        time.sleep(1)
        tempTable = pd.read_html(tempTableHTML)
        df_listedTable[0] = df_listedTable[0].append(tempTable[0])
        time.sleep(1)

date_diff = days_between(gap_stop_date, today)

while(date_diff > 4):
    gap_start_date = gap_stop_date
    gap_stop_date = gap_start_date + timedelta(days = three_months_days)
    
    startDate = driver.find_element(By.NAME, startDateDiv)
    stopDate = driver.find_element(By.NAME, stopDateDiv)
    searchDatesButton = driver.find_element(By.NAME, searchDatesButtonName)
    numOfDataOnPageSelect = Select(driver.find_element(By.NAME, numOfDataOnPageName))
    numOfDataOnPageSelect.select_by_value('250')
    startDate.clear()
    stopDate.clear()
    ActionChains(driver).move_to_element(startDate).click().send_keys(dater(gap_start_date)).perform()
    ActionChains(driver).move_to_element(stopDate).click().send_keys(dater(gap_stop_date)).perform()
    ActionChains(driver).move_to_element(searchDatesButton).click().perform()
    time.sleep(10)
    dataCountText = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/div[@id= 'table_general_info_info']")
    time.sleep(5)
    dataCount = dataCountText.text.split(' ')[0].split('.')
    temp = dataCount[0]
    for i in range(len(dataCount)-1):
        temp += dataCount[i+1]
    dataCount = int(temp)
    listedTable = driver.find_element(By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']").get_attribute('outerHTML')
    df_listedTable  = pd.read_html(listedTable) 
    df_listedTable[0] = df_listedTable[0].append(tempTable[0])
    if(dataCount > 250):    
        pageCount = int(dataCount / 250)
        for i in range(pageCount):
            nextButton = driver.find_element(By.XPATH, "//div[@id='table_general_info_paginate']/a[@id = 'table_general_info_next']")
            driver.implicitly_wait(1) 
            ActionChains(driver).move_to_element(nextButton).perform()
            driver.execute_script('arguments[0].click()', nextButton)
            driver.implicitly_wait(20) 
            tempTableHTML = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@id = 'table_general_info_wrapper']/table[@id= 'table_general_info']"))).get_attribute('outerHTML')
            tempTable = pd.read_html(tempTableHTML)
            df_listedTable[0] = df_listedTable[0].append(tempTable[0])
            driver.implicitly_wait(1) 
    
    date_diff = days_between(gap_stop_date, today)

df_listedTable[0].to_csv('//fon_database/'+date_time+'_DailyGeneralInfo.csv')
    
##############################

data_file_dist = '//fon_database/'+date_time+'_DailyDistribution.csv'
data_file_gen_inf = '//fon_database/'+date_time+'_DailyGeneralInfo.csv'

head = pd.read_csv(data_file_dist)

excluded_columns = ['newTarih', 'Tarih', 'Fon Adı', 'Fon Kodu']
head = head.iloc[: , 1:]
head["newTarih"] = np.nan
head.replace('', np.nan, inplace=True)
cols = head.columns.tolist()
ind_Tarih = cols.index("Tarih")
ind_newTrh = cols.index("newTarih")
cols.insert(ind_Tarih, cols.pop(ind_newTrh))
head = head[cols]

for i in range(len(head['Tarih'])):
    head['newTarih'][i] = readDate(head['Tarih'][i])

head.sort_values(by = ['newTarih'], inplace = True)
head = head.reset_index(drop=True)
data = ['0001-01-01']
newDataFrame = pd.DataFrame(data, columns=['newTarih'])

for i in range(len(head['newTarih'])):
    for j in head.columns:
        if j not in excluded_columns:
            if head['newTarih'][i] not in newDataFrame.newTarih:
                newDataFrame = newDataFrame.append(pd.Series([np.nan for k in range(len(newDataFrame.columns))], index=newDataFrame.columns), ignore_index=True)
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc('newTarih')] = head['newTarih'][i]
                if head['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head['Fon Kodu'][i] + '_' + j] = np.nan
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
            else:
                if head['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head['Fon Kodu'][i] + '_' + j] = np.nan
                newDataFrame[head['Fon Kodu'][i] + '_' + j][newDataFrame['newTarih'].index(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
                   
stt_len = len(newDataFrame['newTarih']) - 1
for i in range(stt_len):
    if newDataFrame['newTarih'][stt_len - i - 1] == newDataFrame['newTarih'][stt_len - i]:
        for j in newDataFrame.columns:
            if pd.isna(newDataFrame[j][stt_len - 1 - i]):
                newDataFrame[j][stt_len - 1 - i] = newDataFrame[j][stt_len - i]
        newDataFrame = newDataFrame.drop(index = stt_len - i)
newDataFrame = newDataFrame.reset_index(drop=True)
      
newDataFrame.replace(np.nan, 0, inplace=True)

daily_fon_db = fonDb(newDataFrame, mem_path = daily_mem_path)
## newData frame dailyMem e kaydedildi. Bu distribution. Şimdi general info lazım.
            
            


