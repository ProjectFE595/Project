# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 17:42:53 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

This file implements a DataHandler class. In particular it implements a function
to handle incorrect date.
"""

from datetime import datetime, timedelta as td

class DataHandler(object):
    """Constructor"""
    def __init__(self):
        pass
    
    """If sDate does not belong to list dates then it selects the next existing date in list dates"""
    """If eDate does not belong to list dates then it selects the former existing date in list dates"""    
    def HandleIncorrectDate(sDate,eDate,dates):
        #Handle sDate equivalent to start date
        if sDate != '' and eDate=='':
            #Increment sDate by 1 day until we find a date in the list dates
            while sDate not in dates:
                temp = datetime.strptime(sDate, "%Y-%m-%d")
                temp = temp + td(days=1)
                sDate=temp.strftime('%Y-%m-%d')
            correctDate = sDate
        
        #Handle eDate equivalent to end date
        if eDate != '' and sDate=='':
            #Decrement eDate by 1 day until we find a date in the list dates
            while eDate not in dates:
                temp = datetime.strptime(eDate, "%Yy-%m-%d")
                temp = temp + td(days=-1)
                eDate=temp.strftime('%Y-%m-%d')
            correctDate=eDate
                
        return correctDate
                