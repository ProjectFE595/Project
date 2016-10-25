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
            start = (datetime.strptime(startDate, '%Y-%m-%d') - td(days=90)).strftime('%Y-%m-%d')
            data = GetDataSerieFromMongo(s,start,endDate)
            
        indexClose = numpy.where(data[0]=='Close')[0][0]
        indexOpen = numpy.where(data[0]=='Open')[0][0]
        indexLow = numpy.where(data[0]=='Open')[0][0]
        indexHigh = numpy.where(data[0]=='Open')[0][0]

        data = data[data[:,indexClose]!=0,:] #Remove 0 prices
        data = data[data[:,indexOpen]!=0,:] #Remove 0 prices
        data = data[data[:,indexLow]!=0,:] #Remove 0 prices
        data = data[data[:,indexHigh]!=0,:] #Remove 0 prices
 
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
        header.append('STOCHSLOWK')
        header.append('STOCHSLOWD')
        header.append('MOM')
        header.append('ROC')
        header.append('BOLLINGERUPPER')
        header.append('BOLLINGERMIDDLE')
        header.append('BOLLINGERLOWER')
        header.append('HILBERTTRENDLINE')
        header.append('WILLIAMR')
        header.append('RETURN')
        header.append('RETURNCLASSIFICATION')
        
        
        if len(data)>1:
            
            closeP = numpy.array(data[1:,numpy.where(data[0]=='Close')[0][0]], dtype='f8')
            #openP = numpy.array(data[1:,6], dtype='f8')
            highP = numpy.array(data[1:,numpy.where(data[0]=='High')[0][0]], dtype='f8')
            lowP = numpy.array(data[1:,numpy.where(data[0]=='Low')[0][0]], dtype='f8')
            volume = numpy.array(data[1:,numpy.where(data[0]=='Volume')[0][0]], dtype='f8')    
            
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

            returnClose = numpy.diff(closeP.astype(float), axis=0)/closeP[:-1].astype(float)
            returnClose = numpy.insert(returnClose,0,0)
            where_are_NaNs = numpy.isnan(returnClose)
            returnClose[where_are_NaNs] = 0
            
            returnClassification = numpy.empty([returnClose.size],dtype="S20")

            for i in range(returnClose.size):
                
                if returnClose[i]<-0.5:
                    returnClassification[i]='[,-0.5]'
                if -0.5<= returnClose[i] < -0.45 :
                    returnClassification[i]='[-0.5,-0.45]'
                if -0.45<= returnClose[i] < -0.40 :
                    returnClassification[i]='[-0.45,-0.40]'
                if -0.4<= returnClose[i] < -0.35 :
                    returnClassification[i]='[-0.40,-0.35]'
                if -0.35<= returnClose[i] < -0.3 :
                    returnClassification[i]='[-0.35,-0.30]'
                if -0.3<= returnClose[i] < -0.25 :
                    returnClassification[i]='[-0.30,-0.25]'
                if -0.25<= returnClose[i] < -0.20 :
                    returnClassification[i]='[-0.25,-0.20]'
                if -0.2<= returnClose[i] < -0.15 :
                    returnClassification[i]='[-0.20,-0.15]'
                if -0.15<= returnClose[i] < -0.10 :
                    returnClassification[i]='[-0.15,-0.10]'
                if -0.1<= returnClose[i] < -0.05 :
                    returnClassification[i]='[-0.10,-0.05]'
                if -0.05<= returnClose[i] < 0 :
                    returnClassification[i]='[-0.05,0]'
                if 0<= returnClose[i] < 0.05 :
                    returnClassification[i]='[0,0.05]'
                if 0.05<= returnClose[i] < 0.1 :
                    returnClassification[i]='[0.05,0.1]'
                if 0.1<= returnClose[i] < 0.15 :
                    returnClassification[i]='[0.1,0.15]'
                if 0.15<= returnClose[i] < 0.2 :
                    returnClassification[i]='[0.15,0.2]'
                if 0.2<= returnClose[i] < 0.25 :
                    returnClassification[i]='[0.2,0.25]'
                if 0.25<= returnClose[i] < 0.3 :
                    returnClassification[i]='[0.25,0.30]'
                if 0.3<= returnClose[i] < 0.35 :
                    returnClassification[i]='[0.30,0.35]'
                if 0.35<= returnClose[i] < 0.4 :
                    returnClassification[i]='[0.35,0.40]'
                if 0.4<= returnClose[i] < 0.45 :
                    returnClassification[i]='[0.40,0.45]'
                if 0.45<= returnClose[i] < 0.5 :
                    returnClassification[i]='[0.45,0.50]'
                if 0.5<= returnClose[i] :
                    returnClassification[i]='[0.5,]'
            
            res = numpy.c_[data[1:,:],
                           sma,
                           ema,
                           kama,
                           adx,
                           rsi,
                           cci,
                           macd,
                           signal,
                           hist,
                           mfi,
                           ad,
                           adOscillator,
                           atr,
                           obv,
                           slowk,
                           slowd,
                           mom,
                           roc,
                           upperBB,
                           middleBB,
                           lowerBB,
                           hilbertTL,
                           williamR,
                           returnClose,
                           returnClassification]

            
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
