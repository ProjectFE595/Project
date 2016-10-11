# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 15:22:15 2016

@author: Hugo
"""

import numpy
import talib

from talib import MA_Type
from talib import ADX
from pymongo import MongoClient

stocks = list(db.HistPrices.find({'Date':"2016-09-23",'BBGTicker':'YHOO'}).distinct("BBGTicker")) 

"""
    close = numpy.random.random(100)
    output = talib.SMA(close)
    
    
    upper, middle, lower = talib.BBANDS(close, matype=MA_Type.T3)
    real = ADX(upper, lower, close, timeperiod=14)
    print(real)
"""