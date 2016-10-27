# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 17:50:37 2016

@author: Hugo
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:50:05 2016

@author: Hugo
"""

from pymongo import MongoClient
from datetime import datetime, timedelta as td

def GetAnalyticsFromMongo(stock,startDate='',endDate=''):
   
    print("hi")
    client = MongoClient()
    db = client.Project
    
    if startDate=='' and endDate=='':
        mongoData = list(db.HistSignals.find({'BBGTicker':stock})) 
    else:
        d1 = datetime.strptime(startDate, '%Y-%m-%d')
        d2 = datetime.strptime(endDate, '%Y-%m-%d') 
        delta = (d2-d1).days+1
        dateList=[]
        
        for i in range(delta):
            dateList.append((d1+td(days=i)).strftime('%Y-%m-%d'))
            
        mongoData = list(db.HistSignals.find({'Date':{"$in":dateList},'BBGTicker':stock})) 
    
    headers= list(mongoData[0].keys())   
    dataList=[]
    dataList.append(headers)
    for key in headers:
        dataList.append(mongoData[0].get(key))
        
    return dataList