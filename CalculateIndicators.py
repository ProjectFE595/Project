# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 15:22:15 2016

@author: Hugo
"""

import numpy
import talib
from datetime import datetime, timedelta as td
from talib import MA_Type
from pymongo import MongoClient
from GetDataSerieFromMongo import GetDataSerieFromMongo

def CalculateIndicators(startDate = '',endDate=''):
    
    client = MongoClient()
    db = client.Project
  
    stocks =[x['BBGTicker'] for x in list(db.Stocks.find({}))]
    
    
    if startDate=='' and endDate=='':
        db.HistSignals.delete_many({})
    else:
        d1 = datetime.strptime(startDate, '%Y-%m-%d')
        d2 = datetime.strptime(endDate, '%Y-%m-%d') 
        delta = (d2-d1).days+1
        for i in range(delta):
            db.HistSignals.delete_many({'Date':(d1+td(days=i)).strftime('%Y-%m-%d')})
        
        
    for s in stocks:
        
        print(s)
        if startDate=='' and endDate=='':
            data = GetDataSerieFromMongo(s) 
        else:
            d = (datetime.strptime(startDate, '%Y-%m-%d') - td(days=90)).strftime('%Y-%m-%d')
            data = GetDataSerieFromMongo(s,d,endDate)
            
        header = data[0].tolist()
        
        header.append('SMA')
        header.append('EMA')
        header.append('KAMA')
        header.append('ADX')
        header.append('RSI')
        header.append('CCI')
        header.append('MACD')
        header.append('MACDSIGNAL')
        header.append('MACDHIST')    
        header.append('MFI')
        header.append('AD')
        header.append('ADOSCILLATOR')
        header.append('ATR')
        header.append('OBV')
        header.append('STOCH')
        header.append('MOM')
        header.append('ROC')
        header.append('BOLLINGERUPPER')
        header.append('BOLLINGERMIDDLE')
        header.append('BOLLINGERLOWER')
        header.append('HILBERTTRENDLINE')
        header.append('WILLIAMR')
        
        if len(data)>1:
            
            closeP = numpy.array(data[1:,1], dtype='f8')
            #openP = numpy.array(data[1:,6], dtype='f8')
            highP = numpy.array(data[1:,3], dtype='f8')
            lowP = numpy.array(data[1:,4], dtype='f8')
            volume = numpy.array(data[1:,7], dtype='f8')    
            
            sma = talib.SMA(closeP,timeperiod=14)
            ema = talib.EMA(closeP,timeperiod=30)
            kama = talib.KAMA(closeP,timeperiod=30)
            adx = talib.ADX(highP,lowP,closeP,timeperiod=14)
            rsi = talib.RSI(closeP,timeperiod=14)
            cci = talib.CCI(highP,lowP,closeP,timeperiod=14)
            macd, signal, hist = talib.MACD(closeP,fastperiod=12,slowperiod=26,signalperiod=9)
            mfi = talib.MFI(highP,lowP,closeP,volume,timeperiod=14)
            ad = talib.AD(highP,lowP,closeP,volume)
            adOscillator = talib.ADOSC(highP,lowP,closeP,volume,fastperiod=3, slowperiod=10)
            atr = talib.ATR(highP,lowP,closeP,timeperiod=14)
            obv = talib.OBV(closeP,volume)
            slowk, slowd = talib.STOCH(highP,lowP,closeP,fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
            mom = talib.MOM(closeP,timeperiod=10)
            roc = talib.ROC(closeP,timeperiod=10)
            upperBB, middleBB, lowerBB = talib.BBANDS(closeP, matype=MA_Type.T3)
            hilbertTL = talib.HT_TRENDLINE(closeP)
            williamR = talib.WILLR(highP,lowP,closeP,timeperiod=14)
            
            res = numpy.c_[data[1:,:],sma,ema,kama,adx,rsi,cci,macd,signal,hist,mfi,ad,adOscillator,atr,
                           obv,slowk,slowd,mom,roc,upperBB,middleBB,lowerBB,hilbertTL,williamR]
            
            records = res.tolist()
            
            jsonDict = []
            
            for item in records:
                jsonDict.append(dict(zip(header,item)))
    
            if startDate=='' and endDate=='':        
                db.HistSignals.insert_many(jsonDict)
            else:
                jsonDictFilter = [a for a in jsonDict if datetime.strptime(startDate, '%Y-%m-%d')
                <=datetime.strptime(a['Date'], '%Y-%m-%d')
                <=datetime.strptime(endDate, '%Y-%m-%d')]
                
                db.HistSignals.insert_many(jsonDictFilter)
