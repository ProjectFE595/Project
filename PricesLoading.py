# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""

import quandl
from pymongo import MongoClient
import time
from ReloadStocks import ReloadStocks

class PricesLoading(object):
    
    def __init__(self,apiKey,date=''):
        self.apiKey=apiKey
        client = MongoClient()
        self.db = client.Project
        
    def AdjustDataFormat(self,df,stock):

        df['Dates'] = df.index.values
        df['Dates'] = df['Dates'].apply(lambda x: x.strftime('%Y-%m-%d'))
        df = df[:][(df['Close']>0)]
        
        dates = list(df['Dates'])
        
        c = list(df.columns)
        #if 'Adj. Close' in c and 'Adj. Open' in c and 'Adj. High' in c  and 'Adj. Low' in c:
        if 'Adj. Close' in c:
            close=list(df['Adj. Close'])
        else:
            close=list(df['Close'])
            
        if 'Adj. Open' in c:
            ope=list(df['Adj. Open'])
        else:
            ope=list(df['Open'])      
            
        if 'Adj. High' in c:
            high=list(df['Adj. High'])
        else:
            high=list(df['High'])  
            
        if 'Adj. Low' in c:
            low=list(df['Adj. Low'])
        else:
            low=list(df['Low'])
            
        if 'Adj. Volume' in c:
            vol=list(df['Adj. Volume'])
        else:
            vol=list(df['Volume'])
    
        
    
        if not df.empty:
            record = [{'BBGTicker' : stock['BBGTicker'], 
                       'QuandlID' : stock['QuandlID'], 
                       'Name' : stock['Name'], 
                       'Dates' : dates, 
                       'Close' : close, 
                       'Open': ope, 
                       'High' : high, 
                       'Low' : low , 
                       'Volume' : vol}]
                       
        return record
                
    def LoadPricesInMongo(self):
       
        quandlIDDict = list(self.db.Stocks.find({},{"QuandlID":1,"BBGTicker":1,"Name":1,"_id":0}))
            
        for s in quandlIDDict:
            self.db.HistPrices.delete_many({'BBGTicker':s['BBGTicker']})
    
        apiCall=1
        
        for stock in quandlIDDict: #quandlIDs:
            print(stock['BBGTicker'])
            if apiCall%19 == 0:
                time.sleep(11*60) #sleep 15 min
            quandl.ApiConfig.api_key = self.apiKey
            apiCall = apiCall+1
            histPrice = quandl.get(stock['QuandlID'])
            
            record = self.AdjustDataFormat(histPrice,stock)
                
            self.db.HistPrices.insert_many(record)
                
            self.db.Stocks.delete_many({"BBGTicker": stock['BBGTicker']})
        
        ReloadStocks()