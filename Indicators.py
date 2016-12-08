# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 15:22:15 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

This file implements an Indicators class which calculates many different
technical indicators using TA-Lib library and insert results into Mongo
DB collection "Analytics"
"""

import numpy
import talib
from talib import MA_Type
      
class Indicators(object):
    
    """Constructor"""
    def __init__(self, db):
        self.db = db       
    
    """Calculate indicators and future returns for all available dates and insert resultsin Mongo DB"""
    def CalculateIndicators(self):
      
        #Get all available stocks
        stocks =[x['BBGTicker'] for x in list(self.db.Stocks.find({}))]
        
        #For each stocks get price and volume and calculate analytics
        for s in stocks:
            
            print(s)
            
            #Get adjusted close price if available else close price
            c = self.db.Prices.find_one({'BBGTicker' : s},{'Adj Close' : 1})
            if 'Adj Close' not in list(c.keys()):
                c = self.db.Prices.find_one({'BBGTicker' : s},{'Close' : 1})
                close=c['Close']
            else:
                close=c['Adj Close']
            
            #Get adjusted low price if available else low price
            l = self.db.Prices.find_one({'BBGTicker' : s},{'Adj Low' : 1})
            if 'Adj Low' not in list(l.keys()):
                l = self.db.Prices.find_one({'BBGTicker' : s},{'Low' : 1})          
                low=l['Low']
            else:
                low=l['Adj Low']
            
            #Get adjusted high price if available else high price
            h = self.db.Prices.find_one({'BBGTicker' : s},{'Adj High' : 1})
            if 'Adj High' not in list(h.keys()):
                h = self.db.Prices.find_one({'BBGTicker' : s},{'High' : 1})     
                high=h['High']
            else:
                high=h['Adj High']
                
            #Get adjusted volume if available else volume
            v = self.db.Prices.find_one({'BBGTicker' : s},{'Adj Volume' : 1})
            if 'Adj Volume' not in list(v.keys()):
                v = self.db.Prices.find_one({'BBGTicker' : s},{'Volume' : 1})           
                vol=v['Volume']
            else:
                vol=v['Adj Volume']
                
            dates = sorted(close.keys())                        
            
            #Transform dictionary into numpy array
            closeP = numpy.zeros(shape=(len(dates),))
            highP = numpy.zeros(shape=(len(dates),))
            lowP = numpy.zeros(shape=(len(dates),))
            volume = numpy.zeros(shape=(len(dates),))
            
            i=0
            for dt in dates:              
                closeP[i] = close[dt]
                highP[i] = high[dt]
                lowP[i] = low[dt]
                volume[i] = vol[dt]
                i=i+1
            
            #Calculate different moving average
            rawsma = talib.SMA(closeP,timeperiod=14)
            rawema = talib.EMA(closeP,timeperiod=30)
            rawkama = talib.KAMA(closeP,timeperiod=30)
    
            sma=numpy.copy(rawsma)
            ema=numpy.copy(rawema)
            kama=numpy.copy(rawkama)
            
            #Transform moving average into signal (MA - close price)
            for k in range(len(closeP)):
                sma[k] = rawsma[k]-closeP[k]
                ema[k] = rawema[k]-closeP[k]
                kama[k] = rawkama[k]-closeP[k]
            
            #Calculate different analytics (RSI, ADX, MFI, CCI OBV etc)
            adx = talib.ADX(highP,lowP,closeP,timeperiod=14)
            rsi = talib.RSI(closeP,timeperiod=14)
            cci = talib.CCI(highP,lowP,closeP,timeperiod=14)
            macd, signal, hist = talib.MACD(closeP,fastperiod=12,slowperiod=26,signalperiod=9)          
            mfi = talib.MFI(highP,lowP,closeP,volume,timeperiod=14)
            ad = talib.AD(highP,lowP,closeP,volume)
            adosc = talib.ADOSC(highP,lowP,closeP,volume,fastperiod=3, slowperiod=10)
            atr = talib.ATR(highP,lowP,closeP,timeperiod=14)
            obv = talib.OBV(closeP,volume)
            slowk, slowd = talib.STOCH(highP,lowP,closeP,fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
           
            mom = talib.MOM(closeP,timeperiod=10)
            roc = talib.ROC(closeP,timeperiod=10)
            upperBB, middleBB, lowerBB = talib.BBANDS(closeP, matype=MA_Type.T3)
        
            ht = talib.HT_TRENDLINE(closeP)
            willR = talib.WILLR(highP,lowP,closeP,timeperiod=14)
            
            #Define dictionary keys
            analytics = {'BBGTicker' : s}
            analytics['RAWSMA']={}
            analytics['RAWEMA']={}
            analytics['RAWKAMA']={}
            analytics['SMA']={}
            analytics['EMA']={}
            analytics['KAMA']={}
            analytics['ADX']={}
            analytics['RSI']={}
            analytics['CCI']={}
            analytics['MACD']={}
            analytics['MACDSIGNAL']={}
            analytics['MACDHIST']={}
            analytics['MFI']={}
            analytics['AD']={}
            analytics['ADOSCILLATOR']={}
            analytics['ATR']={}
            analytics['OBV']={}
            analytics['STOCHSLOWD']={}
            analytics['STOCHSLOWK']={}
            analytics['MOM']={}
            analytics['ROC']={}
            analytics['LOWERBB']={}
            analytics['MIDDLEBB']={}
            analytics['UPPERBB']={}
            analytics['HILBERT']={}
            analytics['WILLIAMR']={}
            
            #For each date dt insert into corresponding dictionary
            i=0
            for dt in dates:
                analytics['RAWSMA'][dt]=rawsma[i]
                analytics['RAWEMA'][dt]=rawema[i]
                analytics['RAWKAMA'][dt]=rawkama[i]
                analytics['SMA'][dt]=sma[i]
                analytics['EMA'][dt]=ema[i]
                analytics['KAMA'][dt]=kama[i]
                analytics['ADX'][dt]=adx[i]
                analytics['RSI'][dt]=rsi[i]
                analytics['CCI'][dt]=cci[i]
                analytics['MACD'][dt]=macd[i]
                analytics['MACDSIGNAL'][dt]=signal[i]
                analytics['MACDHIST'][dt]=hist[i]
                analytics['MFI'][dt]=mfi[i]
                analytics['AD'][dt]=ad[i]
                analytics['ADOSCILLATOR'][dt]=adosc[i]
                analytics['ATR'][dt]=atr[i]
                analytics['OBV'][dt]=obv[i]
                analytics['STOCHSLOWD'][dt]=slowd[i]
                analytics['STOCHSLOWK'][dt]=slowk[i]
                analytics['MOM'][dt]=mom[i]
                analytics['ROC'][dt]=roc[i]
                analytics['LOWERBB'][dt]=lowerBB[i]
                analytics['MIDDLEBB'][dt]=middleBB[i]
                analytics['UPPERBB'][dt]=upperBB[i]
                analytics['HILBERT'][dt]=ht[i]
                analytics['WILLIAMR'][dt]=willR[i]
                i=i+1
            
            #Insert data into mongo DB
            record = [analytics]
            
            self.db.Analytics.delete_many({'BBGTicker' : s})
            self.db.Analytics.insert_many(record)
            
            #Calculate future returns for horizon between 1 and 30 days
            futureReturn = {'BBGTicker' : s}
            for k in range(60):             
                k=k+1
                futureReturn['FUTURERETURN'+str(k)+'DAYS'] = {}               
                for dt in dates:
                    p1 = close[dt]
                    dateIndex = dates.index(dt)
                    if dateIndex + k < len(dates):
                        d2 = dates[dateIndex + k]  #Lookup corresponding future date for horizon k           
                        p2 = close[d2]
                        futureReturn['FUTURERETURN'+str(k)+'DAYS'][dt] = p2/p1-1 #Calculate future return       
            
            #Insert future returns into Mongo DB
            record = [futureReturn]
            
            self.db.Returns.delete_many({'BBGTicker' : s})
            self.db.Returns.insert_many(record)            
            