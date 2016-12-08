# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

This file implements a PricesLoading class to automatically downloads Quandl
data like prices and volumes into local mongo DB for all the stocks. Note that
Quandl does not allow to download more than 20 stocks per 10 min so the program
has to sleep 10 min to download all the 100 stocks available
"""

import quandl
import time
import numpy
import pandas
from ReloadStocks import ReloadStocks

class PricesLoading(object):
    """Constructor"""
    def __init__(self,apiKey,db,date=''):
        self.apiKey=apiKey
        self.db=db
    
    """Transforms a dataframe from Quandl into a list of 1 dictionary"""
    def AdjustDataFormat(self,df,stock):
        
        #Remove the '.' for the adjustment price and volume because mongo DB
        #does not accept dictionay key with a dot
        df = df.rename(index=str, columns={"Adj. Close": "Adj Close", 
                                      "Adj. Open": "Adj Open", 
                                      "Adj. High": "Adj High",
                                      "Adj. Low": "Adj Low",
                                      "Adj. Volume": "Adj Volume"})    
        #Clean the data, remove negative prices, NaN prices
        df = df[:][(df['Close']>0)]
        df = df[:][(df['Open']>0)]
        df = df[:][(df['High']>0)]
        df = df[:][(df['Low']>0)]          
        df = df.dropna(how='any')
        
        #Transform dataframe key into a string
        df=df.set_index(numpy.array([pandas.to_datetime(str(i)).strftime('%Y-%m-%d') for i in df.index.values]))
        
        #Transform dataframe into dctionary and set some keys
        dic= df.to_dict(orient='dict')   
        dic['BBGTicker']=stock['BBGTicker']
        dic['QuandlID']=stock['QuandlID']
        dic['Name']=stock['Name']

        record = [dic]
                       
        return record
    
    """Download data from Quandl and insert into local Mongo DB"""            
    def LoadPricesInMongo(self):
        
        #Return all available stocks from Mongo
        quandlIDDict = list(self.db.Stocks.find({},{"QuandlID":1,"BBGTicker":1,"Name":1,"_id":0}))
        
        #For each stock remove the data to entirely reload
        for s in quandlIDDict:
            self.db.Prices.delete_many({'BBGTicker':s['BBGTicker']})
    
        apiCall=1
        
        #For each stock call Quandl API 
        for stock in quandlIDDict: #quandlIDs:
            print(stock['BBGTicker'])
            if apiCall%20 == 0:
                time.sleep(11*60) #sleep 10 min if 20 calls have been made
            quandl.ApiConfig.api_key = self.apiKey
            apiCall = apiCall+1
            
            #Call Quandl API to download price dataframe
            histPrice = quandl.get(stock['QuandlID'])
            
            #Transform Quandl dataframe into a list of 1 dictionary
            record = self.AdjustDataFormat(histPrice,stock)
 
            #Insert in Mongo Quandl data               
            self.db.Prices.insert_many(record)     
            #Remove current stock, it will be reloaded later
            self.db.Stocks.delete_many({"BBGTicker": stock['BBGTicker']})
        
        ReloadStocks()