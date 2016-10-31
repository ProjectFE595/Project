# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:50:05 2016

@author: Hugo
"""

from pymongo import MongoClient
from datetime import datetime, timedelta as td

def GetDataSerieFromMongo(stock,startDate='',endDate=''):
   
    client = MongoClient()
    db = client.Project
    
    mongoData = list(db.HistPrices.find({'BBGTicker':stock})) 

    headers= list(mongoData[0].keys())   
    dataList=[]
    dataList.append(headers)
    if startDate=='' and endDate=='':
        for key in headers:
            dataList.append(mongoData[0].get(key))
    else:
        indexStartDate = mongoData[0]['Date'].index(startDate)
        indexEndDate = mongoData[0]['Date'].index(endDate)
        for key in headers:
            temp=mongoData[0].get(key)
            if isinstance(temp, list):
                dataList.append(mongoData[0].get(key)[indexStartDate:indexEndDate+1])
            else:
                dataList.append(mongoData[0].get(key))
        
    return dataList