# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 15:22:15 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""

import numpy
import talib
from datetime import datetime, timedelta as td
from talib import MA_Type
from pymongo import MongoClient
from MongoDataGetter import MongoDataGetter
from DataHandler import DataHandler

class Indicators(object):

    def __init__(self, db, sDate='', eDate=''):
        self.startDate=sDate
        self.endDate=eDate
        self.db = db       
        
                
    def PopulateHeaders(self,headers):
        headers.append('RAWSMA')
        headers.append('RAWEMA')
        headers.append('RAWKAMA')        
        headers.append('SMA')
        headers.append('EMA')
        headers.append('KAMA')
        headers.append('ADX')
        headers.append('RSI')
        headers.append('CCI')
        headers.append('MACD')
        headers.append('MACDSIGNAL')
        headers.append('MACDHIST')    
        headers.append('MFI')
        headers.append('AD')
        headers.append('ADOSCILLATOR')
        headers.append('ATR')
        headers.append('OBV')
        headers.append('STOCHSLOWK')
        headers.append('STOCHSLOWD')
        headers.append('MOM')
        headers.append('ROC')
        headers.append('BOLLINGERUPPER')
        headers.append('BOLLINGERMIDDLE')
        headers.append('BOLLINGERLOWER')
        headers.append('HILBERTTRENDLINE')
        headers.append('WILLIAMR')
        headers.append('RETURN')
        
    def InsertAnalyticsIntoMongo(self,headers,analytics):
        res={}
        for key in headers:
            if len(analytics[headers.index(key)].shape)==0:
                res[key] = numpy.atleast_1d(analytics[headers.index(key)])[0]
            else:
                res[key] = list(analytics[headers.index(key)])
                
        record = [res]
                    
        self.db.HistSignals.insert_many(record)
                
    def CalculateIndicators(self):
      
        stocks =[x['BBGTicker'] for x in list(self.db.Stocks.find({}))]
        
        self.db.HistSignals.delete_many({})
                   
        for s in stocks:
            
            print(s)
            mg = MongoDataGetter(self.db)
            dataMongo = mg.GetDataFromMongo(s,'Prices')
            
            headers = dataMongo[0]
            data = dataMongo[1:] #get rid of header
            
            dates = data[headers.index('Dates')]
            dh = DataHandler(self.startDate,self.endDate)
            self.startDate,self.endDate = dh.HandleIncorrectDate(dates)
            
            self.PopulateHeaders(headers)
                       
            analytics=[numpy.array(d) for d in data]
            
            indexClose = headers.index('Close')
            indexLow = headers.index('Low')
            indexHigh = headers.index('High')
            indexVolume = headers.index('Volume')
    
            if len(data)>1:
                
                closeP = numpy.array(data[indexClose], dtype='f8')
                #openP = numpy.array(data[1:,6], dtype='f8')
                highP = numpy.array(data[indexHigh], dtype='f8')
                lowP = numpy.array(data[indexLow], dtype='f8')
                volume = numpy.array(data[indexVolume], dtype='f8')    
                
                rawsma = talib.SMA(closeP,timeperiod=14)
                rawema = talib.EMA(closeP,timeperiod=30)
                rawkama = talib.KAMA(closeP,timeperiod=30)
                
                analytics.append(rawsma)
                analytics.append(rawema)
                analytics.append(rawkama)
    
                sma=numpy.copy(rawsma)
                ema=numpy.copy(rawema)
                kama=numpy.copy(rawkama)
                
                for k in range(len(closeP)):
                        sma[k] = rawsma[k]-closeP[k]
                        ema[k] = rawema[k]-closeP[k]
                        kama[k] = rawkama[k]-closeP[k]
                        
                analytics.append(sma)
                analytics.append(ema)
                analytics.append(kama)
                analytics.append(talib.ADX(highP,lowP,closeP,timeperiod=14))
                analytics.append(talib.RSI(closeP,timeperiod=14))
                analytics.append(talib.CCI(highP,lowP,closeP,timeperiod=14))
                macd, signal, hist = talib.MACD(closeP,fastperiod=12,slowperiod=26,signalperiod=9)
                analytics.append(macd)
                analytics.append(signal)
                analytics.append(hist)            
                analytics.append(talib.MFI(highP,lowP,closeP,volume,timeperiod=14))
                analytics.append(talib.AD(highP,lowP,closeP,volume))
                analytics.append(talib.ADOSC(highP,lowP,closeP,volume,fastperiod=3, slowperiod=10))
                analytics.append(talib.ATR(highP,lowP,closeP,timeperiod=14))
                analytics.append(talib.OBV(closeP,volume))
                slowk, slowd = talib.STOCH(highP,lowP,closeP,fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
                analytics.append(slowk)
                analytics.append(slowd)            
                analytics.append(talib.MOM(closeP,timeperiod=10))
                analytics.append(talib.ROC(closeP,timeperiod=10))
                upperBB, middleBB, lowerBB = talib.BBANDS(closeP, matype=MA_Type.T3)
                analytics.append(upperBB)
                analytics.append(middleBB)
                analytics.append(lowerBB)            
                analytics.append(talib.HT_TRENDLINE(closeP))
                analytics.append(talib.WILLR(highP,lowP,closeP,timeperiod=14))
    
                returnClose = numpy.diff(closeP.astype(float), axis=0)/closeP[:-1].astype(float)
                returnClose = numpy.insert(returnClose,0,0)
                where_are_NaNs = numpy.isnan(returnClose)
                returnClose[where_are_NaNs] = 0
                analytics.append(returnClose)
                
                self.InsertAnalyticsIntoMongo(headers,analytics)
    

            