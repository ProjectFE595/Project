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

def LoadPricesInMongo(today=''):
    
    client = MongoClient()
    db = client.HistPrices
    
    quandlIDs= []
    quandlIDDict = list(db.Stocks.find({},{"QuandlID":1,"BBGTicker":1,"Name":1,"_id":0}))
    for i in range(len(quandlIDDict)):
        quandlIDs.append([quandlIDDict[i]['BBGTicker'],
                        quandlIDDict[i]['QuandlID'],
                        quandlIDDict[i]['Name']])
        
    if today=='':
        db.HistPrices.delete_many({})
    else:
        db.HistPrices.delete_many({'Date':str(today)})
    apiCall=1
    
    for stock in quandlIDs:
        print(stock)
        if apiCall%19 == 0:
            time.sleep(15*60) #sleep 15 min
        quandl.ApiConfig.api_key = "vXqo1CSCZ6a7eESaKXEu"
        apiCall = apiCall+1
        if today=='':
            histPrice = quandl.get(stock[1])
        else:
            histPrice = quandl.get(stock[1], start_date=today, end_date=today)
        histPrice['Date'] = histPrice.index.values
        histPrice['Date'] = histPrice['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        histPrice = histPrice[['Date','Close','Open','High','Low','Volume']]
        histPrice['BBGTicker'] = stock[0]
        histPrice['Name'] = stock[2]
        histPrice['QuandlID'] = stock[1]
        if not histPrice.empty:
            records = loads(histPrice.to_json(orient='records'))
            db.HistPrices.insert_many(records)
            db.Stocks.delete_many({"BBGTicker": stock[0]})
    
    ReloadStocks()