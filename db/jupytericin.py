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

def find_ind(dictA, keyA, wordA):
    for i in range(len(dictA[keyA])):
        if dictA[keyA][i] == wordA:
            return [True, i]
    return [False, 0]

data_file_dist = '5YearsDistribution.csv'
#data_file_dist = 'dummy2.csv'

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
    if i % 1000 == 0:
        print("i: ", i)
head.sort_values(by = ['newTarih'], inplace = True)
head = head.reset_index(drop=True)
data = ['0001-01-01']
newDataFrame = pd.DataFrame(data, columns=['newTarih'])


for i in range(len(head['newTarih'])):
    if i % 10 == 0:
        print("i: ", i)
    for j in head.columns:
        if j not in excluded_columns:
            try:
                #index = newDataFrame.newTarih.index(head['newTarih'][i])
                index = newDataFrame.index[newDataFrame['newTarih'] == head['newTarih'][i]].tolist()[0]
                if head['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head['Fon Kodu'][i] + '_' + j] = np.nan
                #newDataFrame[head['Fon Kodu'][i] + '_' + j][newDataFrame['newTarih'].index(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
                newDataFrame[head['Fon Kodu'][i] + '_' + j][index] = head[j][i]
            #except ValueError:
            except IndexError:
                newDataFrame = newDataFrame.append(pd.Series([np.nan for k in range(len(newDataFrame.columns))], index=newDataFrame.columns), ignore_index=True)
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc('newTarih')] = head['newTarih'][i]
                if head['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head['Fon Kodu'][i] + '_' + j] = np.nan
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
                
stt_len = len(newDataFrame['newTarih']) - 1
for i in range(stt_len):
    if i % 10 == 0:
        print("i: ", i)
    if newDataFrame['newTarih'][stt_len - i - 1] == newDataFrame['newTarih'][stt_len - i]:
        for j in newDataFrame.columns:
            if pd.isna(newDataFrame[j][stt_len - 1 - i]):
                newDataFrame[j][stt_len - 1 - i] = newDataFrame[j][stt_len - i]
        newDataFrame = newDataFrame.drop(index = stt_len - i)
newDataFrame = newDataFrame.reset_index(drop=True)
newDataFrame.replace(np.nan, 0, inplace=True)

daily_mem_path = 'mem\\dailyFonDb'

daily_fon_db = fonDb(newDataFrame, mem_path = daily_mem_path)

newDataFrame.to_csv(r'D:\Users\26015017\OneDrive - ARÇELİK A.Ş\Desktop\fonML\fon_database/2021_11_17_DailyDistribution.csv')

data_file_gen = '5YearsGeneralSummary.csv'
head_gen = pd.read_csv(data_file_gen)
head_gen = head_gen.iloc[: , 1:]
print(head_gen.head(10))
head_gen["newTarih"] = np.nan
head_gen.replace('', np.nan, inplace=True)
cols = head_gen.columns.tolist()
ind_Tarih = cols.index("Tarih")
ind_newTrh = cols.index("newTarih")
cols.insert(ind_Tarih, cols.pop(ind_newTrh))
head_gen = head_gen[cols]

for i in range(len(head_gen['Tarih'])):
    head_gen['newTarih'][i] = readDate(head_gen['Tarih'][i])
    if i % 1000 == 0:
        print("i: ", i)
        
tempInd = newDataFrame.index[newDataFrame['newTarih'] == '0001-01-01'].tolist()[0]
newDataFrame = newDataFrame.drop([tempInd], axis=0)
newDataFrame = newDataFrame.reset_index(drop=True)
head_gen.sort_values(by = ['newTarih'], inplace = True)
head_gen = head_gen.reset_index(drop=True)
for i in range(len(head_gen['newTarih'])):
    if i % 10 == 0:
        print("i: ", i)
    for j in head_gen.columns:
        if j not in excluded_columns:
            try:
                index = newDataFrame.index[newDataFrame['newTarih'] == head_gen['newTarih'][i]].tolist()[0]
                if head_gen['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head_gen['Fon Kodu'][i] + '_' + j] = np.nan
                newDataFrame[head_gen['Fon Kodu'][i] + '_' + j][index] = head_gen[j][i]
            except IndexError:
                newDataFrame = newDataFrame.append(pd.Series([np.nan for k in range(len(newDataFrame.columns))], index=newDataFrame.columns), ignore_index=True)
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc('newTarih')] = head_gen['newTarih'][i]
                if head_gen['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head_gen['Fon Kodu'][i] + '_' + j] = np.nan
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc(head_gen['Fon Kodu'][i] + '_' + j)] = head_gen[j][i]
                
stt_len = len(newDataFrame['newTarih']) - 1
for i in range(stt_len):
    if i % 10 == 0:
        print("i: ", i)
    if newDataFrame['newTarih'][stt_len - i - 1] == newDataFrame['newTarih'][stt_len - i]:
        for j in newDataFrame.columns:
            if pd.isna(newDataFrame[j][stt_len - 1 - i]):
                newDataFrame[j][stt_len - 1 - i] = newDataFrame[j][stt_len - i]
        newDataFrame = newDataFrame.drop(index = stt_len - i)
newDataFrame = newDataFrame.reset_index(drop=True)
newDataFrame.replace(np.nan, 0, inplace=True) 
daily_fon_db.addDf(newDataFrame)