# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo
"""

import datetime
from PricesLoading import PricesLoading
from Indicators import Indicators
from Portfolios import Portfolios
from Predictor import Predictor
import matplotlib.pyplot as plt
import pandas
import numpy
import math


today = datetime.date.today()
today = '2016-09-29'
quandlKey="vXqo1CSCZ6a7eESaKXEu"
benchmark='NASDAQOMX/NDX'

p=PricesLoading(quandlKey)
#p.LoadPricesInMongo()
i = Indicators()
#i.CalculateIndicators()

date='2010-02-05'
horizon=20

TIs=['KAMA','MACDHIST','CCI','RSI','WILLIAMR','MFI','EMA','ROC','STOCHSLOWD','ADX']

prY = Predictor('YHOO',date,horizon,TIs)
prC = Predictor('CSCO',date,horizon,TIs)
prA = Predictor('AAPL',date,horizon,TIs)
prG = Predictor('GOOGL',date,horizon,TIs)

ErYHOO,pYHOO = prY.GetReturnPredictions()
ErCSCO,pCSCO = prC.GetReturnPredictions()
ErAAPL,pAAPL = prA.GetReturnPredictions()
ErGOOGL,pGOOGL = prG.GetReturnPredictions()

print(ErYHOO) 
print(ErCSCO)
print(ErAAPL)
print(ErGOOGL)

print(pYHOO)
print(pCSCO)
print(pAAPL)
print(pGOOGL)

startDate='2010-02-05'
endDate='2015-10-30'
histWindow=120
rebalanceFrequency=500

stockView = ['YHOO','CSCO','AAPL','GOOGL']
stockViewReturn = [ErYHOO,ErCSCO,ErAAPL,ErGOOGL]
stockConfidence = [pYHOO,pCSCO,pAAPL,pGOOGL]

rf = 0.0001
tau = 0.025         

excludedStocks =  ['GOOG','AVGO','BRCM','CHTR','CMCSK','DISCK','FB','GMCR','KHC','LMCA','LVNTA','SNDK','TSLA','TRIP','VRSK','WBA']
   
pt = Portfolios(startDate,endDate,histWindow,rebalanceFrequency)

h,portValue,mu = pt.GetOptimalPortfolio(excludedStocks)
benchmarkValue = pt.GetBenchmarkPortfolio(benchmark,quandlKey)

# Risk aversion of the market 
delta = (252*numpy.mean(benchmarkValue.pct_change().dropna())-rf)/(math.sqrt(252)*numpy.std(benchmarkValue.pct_change().dropna()))
delta = delta[0]

hBL,portBLValue = pt.GetBLPortfolio(stockView,stockViewReturn,stockConfidence,tau,delta,excludedStocks)

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

