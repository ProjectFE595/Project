# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo
"""

import datetime
from LoadPricesInMongo import LoadPricesInMongo
from GetDataSerieFromMongo import GetDataSerieFromMongo
from CalculateIndicators import CalculateIndicators


today = datetime.date.today()
today = '2016-09-29'
#LoadPricesInMongo(today)
#LoadPricesInMongo()
CalculateIndicators()

