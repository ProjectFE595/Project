# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:50:05 2016

@author: Hugo
"""

import numpy
from pymongo import MongoClient
from datetime import datetime, timedelta as td

def GetDataSerieFromMongo(stock,startDate='',endDate=''):
   
    client = MongoClient()
    db = client.Project
    
    if startDate=='' and endDate=='':
        data = list(db.HistPrices.find({'BBGTicker':stock})) 
    else:
        d1 = datetime.strptime(startDate, '%Y-%m-%d')
        d2 = datetime.strptime(endDate, '%Y-%m-%d') 
        delta = (d2-d1).days+1
        dateList=[]
        
        for i in range(delta):
            dateList.append((d1+td(days=i)).strftime('%Y-%m-%d'))
            
        data = list(db.HistPrices.find({'Date':{"$in":dateList},'BBGTicker':stock})) 
    
    headers= list(data[0].keys())   
    records=[]
    records.append(headers)
    for i in range(len(data)):
        row=[]
        for h in headers:
            row.append(data[i][h])
        records.append(row)
        
    return numpy.asarray(records)