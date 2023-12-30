# Multi-frame tkinter application v2.3
import os
import sys
sys.path.insert(0, "..")
import shelve
from pathlib import Path
import pandas as pd
import numpy as np

# all the thing and new columns and new df should be sorted before introduced. otherwise it wont work.

class fonDb():
    # def __init__(self, df):
    #mode 1 is new db mode 2 is update to db in address mem_path
    def __init__(self, df, mem_path = 'mem\\fonDb', mode = 1):
        self.df = df
        self.mem_path = mem_path
        isDbTended = False
        p = Path(__file__).parents[1]
        # self.path = os.path.join(p, 'mem\\fonDb')
        self.path = os.path.join(p, mem_path)
        print("self.path: ", self.path)
        if mode == 1:
            try:
                print("bu path: ", self.path)
                with shelve.open(self.path, writeback=True) as fonDb:
                    newCols = []
                    for i in range(len(df)):
                        if df[i] not in fonDb:
                            newCols.append(df[i])
                            # self.addColumn(df[i])
                    if len(newCols):
                        self.addColumn(columnNames)
                fonDb.close()
            except:
                print("boyle bi db yok dolayısıyla yeni oluşturuluyor")
                self.makeDb()
                print("DB OLUŞTURULDU")
        

    def addColumn(self, columnNames):
        for i in range(len(newCols)):
            fonDb[newCols[i]] = [None] * len(fonDb['newTarih'])
        ind = 0
        for i in range(len(self.df[newCols[i]])):
            ch = True
            if self.df['newTarih'][i] > fonDb['newTarih'][-1]:
                for o in fonDb:
                    if o in self.df:
                        fonDb[o].append(self.df[o][i])
                    else:
                        fonDb[o].append(None)
            elif self.df['newTarih'][i] < fonDb['newTarih'][0]:
                for o in fonDb:
                    if o in self.df:
                        fonDb[o].insert(0, self.df[o][i])
                    else:
                        fonDb[o].insert(0, None)
            else:
                while ch:
                    if self.df['newTarih'][i] >= fonDb['newTarih'][ind]:
                        if self.df['newTarih'][i] > fonDb['newTarih'][ind]:
                            ind = last_ind
                            for o in fonDb:
                                if o in self.df:
                                    fonDb[o].insert(last_ind, self.df[o][i])
                                else:
                                    fonDb[o].insert(last_ind, None)
                            ch = False
                            break
                        else:
                            last_ind = ind
                            chc_loc = True
                            while chc_loc:
                                if fonDb['newTarih'][ind] < fonDb['newTarih'][last_ind] or last_ind == len(fonDb['newTarih']) - 1:
                                    break
                                else:
                                    last_ind += 1
                            for j in range(last_ind - ind):
                                if self.df['Fon Kodu'][i] == fonDb['Fon Kodu'][ind + j]:
                                    for k in range(len(newCols)):
                                        fonDb[newCols[k]][i] = self.df[newCols[k]][i]
                                    ch = False
                                    break
                            ind = last_ind
                            for o in fonDb:
                                if o in self.df:
                                    fonDb[o].insert(last_ind, self.df[o][i])
                                else:
                                    fonDb[o].insert(last_ind, None)
                            ch = False
                            break
                    else:
                        ind += 1
                
    def makeDb(self):
        fonDb = shelve.open(self.path, writeback=True)
        with shelve.open(self.path, writeback=True) as fonDb:
            for o in self.df:
                fonDb[o] = self.df[o]
        fonDb.close()
        self.fonDb = fonDb
        print("DB oluşturuldu")
        
    def tendDb(self):
        print("Henüz bu fonksiyon yazılmadı")

    def showSome(self):
        with shelve.open(self.path) as fonDb:
            rng = 2
            ctr = 0
            for i in fonDb:
                print(i , " ")
                ctr += 1
                if ctr > rng:   
                    break
            print("\n")
            ctr = 0
            for i in fonDb:
                print("\n")
                ctr_sucks = 0
                for j in range(rng):
                    print(fonDb[i][j], " ")
                    ctr_sucks += 1
                    if ctr_sucks > rng:
                        break
                ctr += 1
                if ctr > rng:   
                    break
        fonDb.close()
        
    def showCell(self, col, row):
        with shelve.open(self.path) as fonDb:
            print(fonDb[col][row])
        fonDb.close()
        
    def showColumns(self):
        with shelve.open(self.path) as fonDb:
            ctr = 0
            firstVal = None
            for i in fonDb:
                if ctr == 0:
                    firstVal = len(fonDb[i])
                if ctr > 0 and len(fonDb[i]) != firstVal:
                    print(i, " length: ", len(fonDb[i])," used to be: ", firstVal, "\n")
                firstVal = len(fonDb[i])
                ctr += 1
        fonDb.close()
        
    def fixKisiSayisi(self):
        with shelve.open(self.path, writeback=True) as fonDb:
            ctr = 0
            for i in fonDb:
                if '_Kişi Sayısı' in i:
                    print("fixing ", i, " as ", ctr, " th iteration\n")
                    ctr += 1
                    for j in range(len(fonDb[i])):
                        # print("numpy.float64 to int is: ", int(fonDb[i][j]))
                        tempArr = str(fonDb[i][j]).split('.')
                        lng = len(tempArr)
                        tempNum = 0
                        if tempArr[-1] == '0':
                            tempNumStr = tempArr[0]
                            for s in range(lng-2):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        elif len(tempArr[-1]) == 2:
                            tempArr[-1] += '0'
                            tempNumStr = tempArr[0]
                            for s in range(lng-1):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        elif len(tempArr[-1]) > 2:
                            tempArr[-1] = tempArr[-1][0:3]
                            tempNumStr = tempArr[0]
                            for s in range(lng-1):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        fonDb[i][j] = tempNum
        fonDb.close()
        
    def fixFonToplam(self):
        with shelve.open(self.path, writeback=True) as fonDb:
            ctr = 0
            for i in fonDb:
                if '_Fon Toplam' in i:
                    print("fixing ", i, " as ", ctr, " th iteration\n")
                    ctr += 1
                    for j in range(len(fonDb[i])):
                        # print("numpy.float64 to int is: ", int(fonDb[i][j]))
                        tempArr = str(fonDb[i][j]).split('.')
                        lng = len(tempArr)
                        tempNum = 0
                        if tempArr[-1] == '0':
                            tempNumStr = tempArr[0]
                            for s in range(lng-2):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        elif len(tempArr[-1]) == 2:
                            tempArr[-1] += '0'
                            tempNumStr = tempArr[0]
                            for s in range(lng-1):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        elif len(tempArr[-1]) > 2:
                            tempArr[-1] = tempArr[-1][0:3]
                            tempNumStr = tempArr[0]
                            for s in range(lng-1):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        fonDb[i][j] = tempNum
        fonDb.close()
        
    def fixPaySayisi(self):
        with shelve.open(self.path, writeback=True) as fonDb:
            ctr = 0
            for i in fonDb:
                if '_Tedavüldeki Pay Sayısı' in i:
                    print("fixing ", i, " as ", ctr, " th iteration\n")
                    ctr += 1
                    for j in range(len(fonDb[i])):
                        # print("numpy.float64 to int is: ", int(fonDb[i][j]))
                        tempArr = str(fonDb[i][j]).split('.')
                        lng = len(tempArr)
                        tempNum = 0
                        if tempArr[-1] == '0':
                            tempNumStr = tempArr[0]
                            for s in range(lng-2):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        elif len(tempArr[-1]) == 2:
                            tempArr[-1] += '0'
                            tempNumStr = tempArr[0]
                            for s in range(lng-1):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        elif len(tempArr[-1]) > 2:
                            tempArr[-1] = tempArr[-1][0:3]
                            tempNumStr = tempArr[0]
                            for s in range(lng-1):
                                tempNumStr += tempArr[s+1]
                            tempNum = int(tempNumStr)
                            # print("was: ", fonDb[i][j], " now: ", tempNum, "\n")
                        fonDb[i][j] = tempNum
        fonDb.close()
        
    def fixAbnormalİncDec(self):
        with shelve.open(self.path, writeback=True) as fonDb:
            for i in fonDb:
                lgt = len(fonDb[i])
                if '_Tedavüldeki Pay Sayısı' in i:
                    currentTedavuldekiPaySayisi = fonDb[i][lgt - 1]
                    for j in range(len(fonDb[i]) - 2):
                        if fonDb[i][lgt - 2 - j] != 0 and fonDb[i][lgt - 1 - j] != 0:
                            thrs = fonDb[i][lgt - 1 - j] / fonDb[i][lgt - 2 - j]
                            if thrs > 9 or thrs < 1/9:
                                tStr = i.split('_')[0] + '_Fon Toplam Değer'
                                tFiyatStr = i.split('_')[0] + '_Fiyat'
                                if fonDb[tStr][lgt - 1 - j] != 0 and fonDb[tStr][lgt - 2 - j] != 0:
                                    thrs2 = fonDb[tStr][lgt - 1 - j] / fonDb[tStr][lgt - 2 - j]
                                    if thrs2/thrs > 5 or thrs2/thrs < 0.2:
                                        print(i, " thrs value: ", thrs, " +day: ", fonDb[i][lgt - 1 - j], " -day: ", fonDb[i][lgt - 2 - j])
                                        print(tFiyatStr, " +day(", fonDb['newTarih'][lgt - 1 - j], ")", fonDb[tFiyatStr][lgt - 1 - j], " -day(", fonDb['newTarih'][lgt - 2 - j], ")",fonDb[tFiyatStr][lgt - 2 - j])
                if '_Fon Toplam' in i:
                    currentFonToplam = fonDb[i][lgt - 1]
                    for j in range(len(fonDb[i]) - 2):
                        if fonDb[i][lgt -2 - j] != 0 and fonDb[i][lgt - 1 - j] != 0:
                            thrs = fonDb[i][lgt - 1 - j] / fonDb[i][lgt - 2 - j]
                            if thrs > 9 or thrs < 1/9:
                                tStr = i.split('_')[0] + '_Tedavüldeki Pay Sayısı'
                                tFiyatStr = i.split('_')[0] + '_Fiyat'
                                if fonDb[tStr][lgt - 1 - j] != 0 and fonDb[tStr][lgt - 2 - j] != 0:
                                    thrs2 = fonDb[tStr][lgt - 1 - j] / fonDb[tStr][lgt - 2 - j]
                                    if thrs2/thrs > 5 or thrs2/thrs < 0.2:
                                        print(i, " thrs value: ", thrs, " +day: ", fonDb[i][lgt - 1 - j], " -day: ", fonDb[i][lgt - 2 - j])
                                        print(tFiyatStr, " +day(", fonDb['newTarih'][lgt - 1 - j], ")", fonDb[tFiyatStr][lgt - 1 - j], " -day(", fonDb['newTarih'][lgt - 2 - j], ")",fonDb[tFiyatStr][lgt - 2 - j])
                        
                
                
                
    def showDate(self, newTarih, col = '_Fiyat'):
        with shelve.open(self.path) as fonDb:
            tarihExist = False
            for i in range(len(fonDb['newTarih'])):
                # print(i, " ", newTarih)
                if newTarih in fonDb['newTarih'][i].strftime("%Y-%m-%d"):
                    tarihExist = True
                    for j in fonDb:
                        if col in j:
                            print(j.split('_')[0], " ", j.split('_')[1], ": ", fonDb[j][i])
                    break
            if not tarihExist:
                print(newTarih, " e ait bir kayıt yok! \n")
        fonDb.close()

    def addDf(self, df):
        # with shelve.open(self.path, writeback=True) as fonDb:
        with shelve.open(self.path, writeback=True) as fonDb:
            newCols = []
            print("fonDb: \n", fonDb)
            print("df.columns: \n", df.columns)
            for i in range(len(df.columns)):
                if df.columns[i] not in fonDb:
                # if df[i] not in fonDb:
                    newCols.append(df.columns[i])
                    # newCols.append(df[i])
                    # self.addColumn(df[i])
            if len(newCols):
                self.addColumn(columnNames)
            else:
                isUpdate = False
                if fonDb['newTarih'][-1] >= df['newTarih'][len(df['newTarih'])-1] and fonDb['newTarih'][0] <= df['newTarih'][0]:
                    pass
                else:
                    isUpdate = True
                    self.updateWithDf(df)
        fonDb.close()
        
    def updateWithDf(self, df):
        pass
  

if __name__ == "__main__":
    app = SampleApp()
    
    app.mainloop()
