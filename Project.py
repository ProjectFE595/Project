# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo
"""

import numpy
import talib
import datetime
from LoadPricesInMongo import LoadPricesInMongo
from GetDataSerieFromMongo import GetDataSerieFromMongo

from pymongo import MongoClient
from bson.json_util import loads

today = datetime.date.today()
today = '2016-09-29'
LoadPricesInMongo(today)

"""

data = GetDataSerieFromMongo('YHOO','2016-08-01','2016-09-26') 

header = data[0].tolist()
header.append('SMA')
inputs = numpy.array(data[1:,1], dtype='f8')
output = talib.SMA(inputs,4)

res = numpy.c_[data[1:,:],output]

records = res.tolist()

client = MongoClient()
db = client.HistPrices

jsonDict = []

for item in records:
    jsonDict.append(dict(zip(header,item)))

db.HistSignals.insert_many(jsonDict)

"""