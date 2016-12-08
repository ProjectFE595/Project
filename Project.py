# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 23:03:57 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""

import datetime
from PricesLoading import PricesLoading
from Indicators import Indicators
from Portfolios import Portfolios
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas
import numpy
import math
from PortfolioAnalysis import PortfolioAnalysis
 
today = datetime.date.today()
today = '2016-09-29'
quandlKey="vXqo1CSCZ6a7eESaKXEu"
benchmark='NASDAQOMX/NDX'

hostc='localhost'
#hostc='155.246.104.19'
portn = 27017

client = MongoClient(host=hostc, port=portn)
db = client.Project 

p=PricesLoading(quandlKey,db)
#p.LoadPricesInMongo()
i = Indicators(db)
#i.CalculateIndicators()

horizon=15

TIs=['KAMA','MACDHIST','CCI','RSI','WILLIAMR','MFI','EMA','ROC','STOCHSLOWD','ADX']

startDate='2012-02-08'
endDate='2015-10-28'
histWindow=120
rebalanceFrequency=10
rf = 0.0001
tau = 0.025         

excludedStocks =  ['GOOG','AVGO','BRCM','CHTR','CMCSK','DISCK','FB','GMCR','KHC','LMCA','LVNTA','SNDK','TSLA','TRIP','VRSK','WBA']
   
pt = Portfolios(startDate,endDate,histWindow,rebalanceFrequency,horizon,db)

h,portValue,mu,stocks = pt.GetOptimalPortfolio(excludedStocks)
benchmarkValue = pt.GetBenchmarkPortfolio(benchmark,quandlKey) 

# Risk aversion of the market 
delta = (252*numpy.mean(benchmarkValue.pct_change().dropna())-rf)/(math.sqrt(252)*numpy.std(benchmarkValue.pct_change().dropna()))
delta = delta[0]

stockView = ['YHOO','CSCO','AAPL','GOOGL']
stockViewReturn = [0.3,0.2,-0.05,0.1]
stockConfidence = [0.5,0.7,0.3,0.6]

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

PortRets = dfClean.pct_change().dropna()
PortRets = PortRets.tz_localize('UTC')
PortRets=PortRets.rename(columns = {'Index Value':'Benchmark'})
horizon=1

pa = PortfolioAnalysis(PortRets["OptimalPort"],PortRets["Benchmark"], horizon)
#pa.RunAnalysis()

