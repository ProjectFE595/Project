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
import numpy
import math
from GetBenchmarkPortfolio import GetBenchmarkPortfolio
from GetAnalyticsFromMongo import GetAnalyticsFromMongo
from GetReturnPredictions import GetReturnPredictions

today = datetime.date.today()
today = '2016-09-29'
quandlKey="yJRsZwcETsegkLY-PThM"
benchmark='NASDAQOMX/NDX'
#LoadPricesInMongo(apiKey=quandlKey,today)
#LoadPricesInMongo(apiKey=quandlKey)
# CalculateIndicators()

ErYHOO,pYHOO,meanScores,stdScores = GetReturnPredictions('YHOO','2010-02-05',20)
ErCSCO,pCSCO,meanScores,stdScores = GetReturnPredictions('CSCO','2010-02-05',20)
ErAAPL,pAAPL,meanScores,stdScores = GetReturnPredictions('AAPL','2010-02-05',20)
ErGOOGL,pGOOGL,meanScores,stdScores = GetReturnPredictions('GOOGL','2010-02-05',20)

print(ErYHOO)
print(ErCSCO)
print(ErAAPL)
print(ErGOOGL)

print(pYHOO)
print(pCSCO)
print(pAAPL)
print(pGOOGL)

startDate='2010-02-05'
endDate='2013-10-30'
histWindow=120
rebalanceFrequency=2500

stockView = ['YHOO','CSCO','AAPL','GOOGL']
#stockViewReturn = [-0.055,0.05,0.06,0.1]
#stockConfidence = [0.6,0.8,0.5,0.4]
stockViewReturn = [ErYHOO,ErCSCO,ErAAPL,ErGOOGL]
stockConfidence = [pYHOO,pCSCO,pAAPL,pGOOGL]

rf = 0.0001
tau = 0.025         
   
benchmarkValue = GetBenchmarkPortfolio(benchmark,quandlKey,startDate,endDate)
# Risk aversion of the market 
delta = (252*numpy.mean(benchmarkValue.pct_change().dropna())-rf)/(math.sqrt(252)*numpy.std(benchmarkValue.pct_change().dropna()))
delta = delta[0]
portValue,portBLValue,h,hBL = GetOptimalPortfolio(benchmark,
                                                  startDate,
                                                  endDate,
                                                  histWindow,
                                                  rebalanceFrequency,
                                                  tau,
                                                  stockView,
                                                  stockViewReturn,
                                                  stockConfidence,
                                                  delta)


portValue.columns = ['OptimalPort']
portBLValue.columns = ['BlackLittermanPort'] 

dfConcatenate = pandas.concat([portValue,portBLValue,benchmarkValue], axis=1, join='inner')
init=dfConcatenate['Index Value'][0]
dfConcatenate['Index Value']=dfConcatenate['Index Value']/init
dfClean=dfConcatenate[['OptimalPort','BlackLittermanPort','Index Value']]

# Convert result to dict



#Plot benchmark and optimal portfolio
plt.figure(figsize=(20,7))
#plt.xticks( dfConcatenate[0], dfConcatenate.index.values )


print(type(dfClean))
print(type(dfClean['OptimalPort']))
print(dfClean.to_dict())