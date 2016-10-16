# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo
"""

import datetime
from LoadPricesInMongo import LoadPricesInMongo
from CalculateIndicators import CalculateIndicators
from GetOptimalPortfolio import GetOptimalPortfolio

today = datetime.date.today()
today = '2016-09-29'
quandlKey="vXqo1CSCZ6a7eESaKXEu"
#LoadPricesInMongo(apiKey=quandlKey,today)
#LoadPricesInMongo(apiKey=quandlKey)
#CalculateIndicators()

GetOptimalPortfolio('NASDAQOMX/NDX',quandlKey)
