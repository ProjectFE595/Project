# import numpy as np
# import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt
import quandl
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

import PIL
import PIL.Image
import io
from io import *
import datetime
import pandas
import numpy
import math
import ast

from plot.functions.PricesLoading import PricesLoading
from plot.functions.Indicators import Indicators
from plot.functions.Portfolios import Portfolios
from plot.functions.Predictor import Predictor

def graphic(request):
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    d = datetime.datetime.strptime(startDate, '%m/%d/%Y')
    startDate =  d.strftime('%Y-%m-%d')
    d = datetime.datetime.strptime(endDate, '%m/%d/%Y')
    endDate = d.strftime('%Y-%m-%d')
    histWindow = int(request.POST['histWindow'])
    rebalanceFrequency = int(request.POST['rebalanceFrequency'])
    rf = float(request.POST['rf100'])/100
    tau = float(request.POST['tau'])
    horizon= int(request.POST['futureHorizon'])
    stockList = str(request.POST['stockList']).split( '"')
    stockList = [n for n in stockList if n not in [' [',  ', ', '] ']]

    n = len(stockList)

    quandlKey = "yJRsZwcETsegkLY-PThM"
    benchmark = 'NASDAQOMX/NDX'

    TIs=['KAMA','MACDHIST','CCI','RSI','WILLIAMR','MFI','EMA','ROC','STOCHSLOWD','ADX'] 
	
    excludedStocks =  ['GOOG','AVGO','BRCM','CHTR','CMCSK','DISCK','FB','GMCR','KHC','LMCA','LVNTA','SNDK','TSLA','TRIP','VRSK','WBA']


    pt = Portfolios(startDate,endDate,histWindow,rebalanceFrequency)
    h,portValue,mu,stocks = pt.GetOptimalPortfolio(excludedStocks)

    #userViewMu = [0]*n
    #pr = [0] * n
    Er = [0] * n
    p = [0] * n

    for i in range(0, n):
        Er[i] = float(request.POST[stockList[i]])/100
        p[i] = float(request.POST['cfl'+stockList[i]])/100


    #prY = Predictor('YHOO',startDate,horizon,TIs)
    #prC = Predictor('CSCO',startDate,horizon,TIs)
    #prA = Predictor('AAPL',startDate,horizon,TIs)
    #prG = Predictor('GOOGL',startDate,horizon,TIs)
    
    #ErYHOO,pYHOO = prY.GetReturnPredictions()
    #ErCSCO,pCSCO = prC.GetReturnPredictions()
    #ErAAPL,pAAPL = prA.GetReturnPredictions()
    #ErGOOGL,pGOOGL = prG.GetReturnPredictions()
    
    #ErYHOO = ErYHOO + float(request.POST['YHOO']) / 100
    #ErCSCO = ErCSCO + float(request.POST['CSCO']) / 100
    #ErAAPL = ErAAPL + float(request.POST['AAPL']) / 100
    #ErGOOGL = ErGOOGL + float(request.POST['GOOGL']) / 100

    #startDate = '2010-02-05'
    #endDate = '2013-10-30'
    #histWindow = 120
    #rebalanceFrequency = 2500

    #stockView = ['YHOO', 'CSCO', 'AAPL', 'GOOGL']
    stockView = stockList
    # stockViewReturn = [-0.055,0.05,0.06,0.1]
    # stockConfidence = [0.9,0.8,0.5,0.8]
    #stockViewReturn = [ErYHOO, ErCSCO, ErAAPL, ErGOOGL]
    stockViewReturn = Er
    #stockConfidence = [pYHOO, pCSCO, pAAPL, pGOOGL]
    stockConfidence = p

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
    dfClean = dfClean.dropna(how='any')

    timeList = dfClean.index.tolist()
    Dates = [0] * len(timeList)
    for i in range(0, len(timeList)):
        Dates[i] = timeList[i].strftime('%Y-%m-%d')

    context = {
        'OptimalPort': dfClean['OptimalPort'].tolist(),
        'BlackLittermanPort': dfClean['BlackLittermanPort'].tolist(),
        'Benchmark': dfClean['Index Value'].tolist(),
        'Dates': mark_safe(Dates)

    }

    return render(request, 'plot/plot.html', context)
    




