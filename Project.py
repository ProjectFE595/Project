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
from GetBenchmarkPortfolio import GetBenchmarkPortfolio

today = datetime.date.today()
today = '2016-09-29'
quandlKey="vXqo1CSCZ6a7eESaKXEu"
benchmark='NASDAQOMX/NDX'
LoadPricesInMongo(apiKey=quandlKey,today)
LoadPricesInMongo(apiKey=quandlKey)
CalculateIndicators()

startDate='2010-02-05'
endDate='2013-10-30'
histWindow=250
rebalanceFrequency=2500

stockView = ['YHOO','CSCO','AAPL','GOOGL']
stockViewReturn = [0.000015,-0.000002,-0.00006,0.00001]
stockConfidence = [0.1,0.1,0.1,0.1]
tau = 0.025 

benchmarkValue = GetBenchmarkPortfolio(benchmark,quandlKey,startDate,endDate)
portValue,portBLValue,h,hBL = GetOptimalPortfolio(benchmark,quandlKey,startDate,endDate,histWindow,rebalanceFrequency,
                                                  tau,stockView,stockViewReturn,stockConfidence)


portValue.columns = ['OptimalPort']
portBLValue.columns = ['BlackLittermanPort'] 

dfConcatenate = pandas.concat([portValue,portBLValue,benchmarkValue], axis=1, join='inner')
init=dfConcatenate['Index Value'][0]
dfConcatenate['Index Value']=dfConcatenate['Index Value']/init
dfClean=dfConcatenate[['OptimalPort','BlackLittermanPort','Index Value']]

#Plot benchmark and optimal portfolio
plt.figure(figsize=(20,7))
#plt.xticks( dfConcatenate[0], dfConcatenate.index.values )
port, = plt.plot(dfClean['OptimalPort'],'r',label='Optimal Portfolio')
portBL, = plt.plot(dfClean['BlackLittermanPort'],'g',label='Black-Litterman Portfolio')
ben, = plt.plot(dfClean['Index Value'],'b',label='Benchmark')

plt.legend(handles=[port,portBL,ben])

plt.show()




