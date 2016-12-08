# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 17:46:28 2016

@author: Hugo
"""

from Report import Report
from pymongo import MongoClient

hostc='localhost'
#hostc='155.246.104.19'
portn = 27017
sDate = '2009-02-05'

client = MongoClient(host=hostc, port=portn)
db = client.Project 

rep = Report(sDate,db)
rep.PopulateReport()