# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 17:42:53 2016

@author: Hugo
"""

from datetime import datetime, timedelta as td

class DataHandler(object):

    def __init__(self, sDate, eDate):
        self.startDate=sDate
        self.endDate=eDate

    def HandleIncorrectDate(self,dates):
        if self.startDate != '':
            while self.startDate not in dates:
                temp = datetime.strptime(self.startDate, "%Y-%m-%d")
                temp = temp + td(days=1)
                self.startDate=temp.strftime('%Y-%m-%d')

        if self.endDate != '':
            while self.endDate not in dates:
                temp = datetime.strptime(self.endDate, "%Yy-%m-%d")
                temp = temp + td(days=-1)
                self.endDate=temp.strftime('%Y-%m-%d')
                
        return self.startDate,self.endDate
                
                
    def GetListFromDictionary(self, dic):
        headers= list(dic.keys())  
        dataList=[]
        dataList.append(headers)
        
        self.startDate,self.endDate = self.HandleIncorrectDate(dic['Dates'])        
        
        if self.startDate!='':
            indexStartDate = dic['Dates'].index(self.startDate)
        else:
            indexStartDate=0

        if self.endDate!='':
            indexEndDate = dic['Dates'].index(self.endDate)
        else:
            indexEndDate=len(dic['Dates'])          
    
        if self.startDate=='' and self.endDate=='':
            for key in headers:
                dataList.append(dic.get(key))        
        else:
            for key in headers:
                temp=dic.get(key)
                if isinstance(temp, list):
                    dataList.append(dic.get(key)[indexStartDate:indexEndDate])
                else:
                    dataList.append(dic.get(key))       
                    
        return dataList