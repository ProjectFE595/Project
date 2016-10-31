# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo
"""

import quandl
from pymongo import MongoClient
from bson.json_util import loads
import time
from ReloadStocks import ReloadStocks

def LoadPricesInMongo(apiKey,today=''):
    
    client = MongoClient()
    db = client.Project
    
    quandlIDDict = list(db.Stocks.find({},{"QuandlID":1,"BBGTicker":1,"Name":1,"_id":0}))
        
    if today=='':
        for s in quandlIDDict:
            db.HistPrices.delete_many({'BBGTicker':s['BBGTicker']})
    else:
        for s in quandlIDDict:
            db.HistPrices.delete_many({'BBGTicker':s['BBGTicker'],'Date':str(today)})
    
    apiCall=1
    
    for stock in quandlIDDict: #quandlIDs:
        print(stock['BBGTicker'])
        if apiCall%19 == 0:
            time.sleep(11*60) #sleep 15 min
        quandl.ApiConfig.api_key = apiKey
        apiCall = apiCall+1
        if today=='':
            histPrice = quandl.get(stock['QuandlID'])
        else:
            histPrice = quandl.get(stock['QuandlID'], start_date=today, end_date=today)
        
        histPrice['Date'] = histPrice.index.values
        histPrice['Date'] = histPrice['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        histPrice = histPrice[['Date','Close','Open','High','Low','Volume']]
        histPrice = histPrice[:][(histPrice['Close']>0)]

        if not histPrice.empty:
            record = [{'BBGTicker' : stock['BBGTicker'], 
            'QuandlID' : stock['QuandlID'], 
            'Name' : stock['Name'], 
            'Date' : list(histPrice['Date'].values), 
            'Close' : list(histPrice['Close'].values), 
            'Open': list(histPrice['Open'].values), 
            'High' : list(histPrice['High'].values), 
            'Low' : list(histPrice['Low'].values) , 
            'Volume' : list(histPrice['Volume'].values)}]
            
            #records = loads(histPrice.to_json(orient='records'))
            #db.HistPrices.insert_many(records)
            db.HistPrices.insert_many(record)
            
            db.Stocks.delete_many({"BBGTicker": stock['BBGTicker']})
    
    ReloadStocks()