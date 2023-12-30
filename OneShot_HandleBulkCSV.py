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
# data_file_dist = 'dummy2.csv'

# df_dist = pd.read_csv('5YearsDistribution.csv')
# head = pd.read_csv('5YearsDistribution.csv', nrows=200)
head = pd.read_csv(data_file_dist)
# print("head.columns first: ",head.columns)

excluded_columns = ['newTarih', 'Tarih', 'Fon Adı', 'Fon Kodu']

# with open(data_file_dist, "r", encoding='utf-8') as myfile:
    # head = list(islice(myfile, 10))
# print(head)
# 
# print(head.head(5))
head = head.iloc[: , 1:]
# head.reset_index(drop=True, inplace=True)
# print(head.head(5))

# head["newTarih"] = ""
head["newTarih"] = np.nan
head.replace('', np.nan, inplace=True)

# print("head.columns before: ",head.columns)
cols = head.columns.tolist()
# cols = cols[-1:] + cols[:-1]
ind_Tarih = cols.index("Tarih")
ind_newTrh = cols.index("newTarih")
cols.insert(ind_Tarih, cols.pop(ind_newTrh))
head = head[cols]
# print("head.columns after: ",head.columns)

# print("before: \n")

for i in range(len(head['Tarih'])):
    head['newTarih'][i] = readDate(head['Tarih'][i])
    # if i < 20:
        # print(head['Tarih'][i] , " ", head['Fon Kodu'][i], " ", head['newTarih'][i],"\n")
# print(head.head(5))

head.sort_values(by = ['newTarih'], inplace = True)
head = head.reset_index(drop=True)

# print("\n after: \n")
# print(head.head(5))

# for i in range(len(head['Tarih'])):
    # print(head['Tarih'][i] , " ", head['Fon Kodu'][i], " ", head['newTarih'][i],"\n")
    
# fonDb = fonDb(head)

# fonDb.showSome()

data = ['0001-01-01']
newDataFrame = pd.DataFrame(data, columns=['newTarih'])
# print("newDataFrame bu şekil:")
# print(newDataFrame.head(5))
# newData = {'newTarih': []}
# newDataFrame = pd.DataFrame(newData)

for i in range(len(head['newTarih'])):
    for j in head.columns:
        if j not in excluded_columns:
            # if head['newTarih'][i] not in newDataFrame['newTarih']:
            if head['newTarih'][i] not in newDataFrame.newTarih:
                # print(head['newTarih'][i], " could not found in: ", newDataFrame['newTarih'])
                # print("pd series bu şekil:")
                # print(pd.Series([np.nan for k in range(len(newDataFrame.columns))], index=newDataFrame.columns))
                newDataFrame = newDataFrame.append(pd.Series([np.nan for k in range(len(newDataFrame.columns))], index=newDataFrame.columns), ignore_index=True)
                # print("after adding new row: \n", newDataFrame.head(10))  
                # newData['newTarih'].append(head['newTarih'][i])
                # print("head['newTarih'][i]: ", head['newTarih'][i])
                # newDataFrame['newTarih'][-1] = head['newTarih'][i]
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc('newTarih')] = head['newTarih'][i]
                # newDataFrame.at[-1,'newTarih'] = head['newTarih'][i]
                # newDataFrame.at[newDataFrame.index[-1],'newTarih'] = head['newTarih'][i]
                # print("after changing the last newTarih: \n", newDataFrame.head(10))
                # print("newDataFrame['newTarih'][i]: ", newDataFrame['newTarih'][i])
                if head['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head['Fon Kodu'][i] + '_' + j] = np.nan
                # newDataFrame[head['Fon Kodu'][i] + '_' + j][-1] = head[j][i]
                newDataFrame.iloc[-1, newDataFrame.columns.get_loc(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
                # newDataFrame.at[-1,newDataFrame.columns.get_loc(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
                # newDataFrame.at[newDataFrame.index[-1],newDataFrame.columns.get_loc(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
                # print("after fon işleri: \n", newDataFrame.head(10)) 
            else:
                if head['Fon Kodu'][i] + '_' + j not in newDataFrame.columns:
                    newDataFrame[head['Fon Kodu'][i] + '_' + j] = np.nan
                newDataFrame[head['Fon Kodu'][i] + '_' + j][newDataFrame['newTarih'].index(head['Fon Kodu'][i] + '_' + j)] = head[j][i]
                # newDataFrame.at[newDataFrame['newTarih'].index(head['Fon Kodu'][i] + '_' + j), head['Fon Kodu'][i] + '_' + j] = head[j][i]
                

print("\n new DataFrame: \n")
print(newDataFrame.head(10))     

stt_len = len(newDataFrame['newTarih']) - 1
for i in range(stt_len):
    if newDataFrame['newTarih'][stt_len - i - 1] == newDataFrame['newTarih'][stt_len - i]:
        # row_to_del.append(i)
        for j in newDataFrame.columns:
            # if newDataFrame[j][stt_len - 1 - i] == np.nan:
            if pd.isna(newDataFrame[j][stt_len - 1 - i]):
            # if newDataFrame.iloc[stt_len - 1 - i,j] == pd.np.nan:
                # print("newDataFrame[",j,",][",stt_len - 1 - i,"] == np.nan")
                newDataFrame[j][stt_len - 1 - i] = newDataFrame[j][stt_len - i]
        newDataFrame = newDataFrame.drop(index = stt_len - i)
        # newDataFrame = newDataFrame.reset_index(drop=True)
newDataFrame = newDataFrame.reset_index(drop=True)
            
newDataFrame.replace(np.nan, 0, inplace=True)
            
print("\n newest DataFrame: \n")
print(newDataFrame.head(10)) 

print("columns: \n")
print(newDataFrame.columns)
            

# for i in range(len(head('newTarih'))):
    # if 

