# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:50:05 2016

@author: Hugo
"""

from pymongo import MongoClient
from .DataHandler import DataHandler

class MongoDataGetter(object):
    
    def __init__(self, sDate='', eDate=''):
        self.startDate=sDate
        self.endDate=eDate
        client = MongoClient()
        self.db = client.Project     
                
    def GetDataFromMongo(self,stock,dataType):
        
        if dataType=='TIs':
            mongoData = list(self.db.HistSignals.find({'BBGTicker':stock})) 
        if dataType=='Prices':
            mongoData = list(self.db.HistPrices.find({'BBGTicker':stock})) 
            
        dic = mongoData[0]
        dh = DataHandler(self.startDate,self.endDate)

        self.startDate,self.endDate = dh.HandleIncorrectDate(dic['Dates'])
        res = dh.GetListFromDictionary(dic)

        return res