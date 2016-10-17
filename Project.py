# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo
"""

import datetime
from LoadPricesInMongo import LoadPricesInMongo
from CalculateIndicators import CalculateIndicators
from GetOptimalPortfolio import GetOptimalPortfolio
import matplotlib.pyplot as plt
import pandas

today = datetime.date.today()
today = '2016-09-29'
quandlKey="vXqo1CSCZ6a7eESaKXEu"
benchmark='NASDAQOMX/NDX'
#LoadPricesInMongo(apiKey=quandlKey,today)
#LoadPricesInMongo(apiKey=quandlKey)
#CalculateIndicators()

startDate='2010-02-05'
endDate='2013-10-14'
portValue,benchmarkValue,h,mu = GetOptimalPortfolio(benchmark,quandlKey,startDate,endDate)


dfConcatenate = pandas.concat([portValue,benchmarkValue], axis=1, join='inner')
dfClean=dfConcatenate[[0,'Index Value']]

#Plot benchmark and optimal portfolio
plt.figure(figsize=(20,7))
#plt.xticks( dfConcatenate[0], dfConcatenate.index.values )
port, = plt.plot(dfClean[0],'r',label='Optimal Portfolio')
ben, = plt.plot(dfClean['Index Value'],'b',label='Benchmark')

plt.legend(handles=[port,ben])

plt.show()
