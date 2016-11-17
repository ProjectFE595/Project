# import numpy as np
# import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt
import quandl
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

import PIL
import PIL.Image
import io
from io import *
import datetime
import pandas
import numpy
import math

from plot.functions.PricesLoading import PricesLoading
from plot.functions.Indicators import Indicators
from plot.functions.Portfolios import Portfolios
from plot.functions.Predictor import Predictor


def expreturn(request):
    # --Request the POST from interface(home.html)
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    d = datetime.datetime.strptime(startDate, '%m/%d/%Y')
    startDate = d.strftime('%Y-%m-%d')
    d = datetime.datetime.strptime(endDate, '%m/%d/%Y')
    endDate = d.strftime('%Y-%m-%d')
    histWindow = int(request.POST['histWindow'])
    rebalanceFrequency = int(request.POST['rebalanceFrequency'])
    rf100 = float(request.POST['rf100'])
    tau = float(request.POST['tau'])
    stockList = request.POST.getlist('stockList')
    horizon = int(request.POST['futureHorizon'])
    n = len(stockList)


    excludedStocks = ['GOOG', 'AVGO', 'BRCM', 'CHTR', 'CMCSK', 'DISCK', 'FB', 'GMCR', 'KHC', 'LMCA', 'LVNTA', 'SNDK',
                      'TSLA', 'TRIP', 'VRSK', 'WBA']
    TIs = ['KAMA', 'MACDHIST', 'CCI', 'RSI', 'WILLIAMR', 'MFI', 'EMA', 'ROC', 'STOCHSLOWD', 'ADX']
    pt = Portfolios(startDate, endDate, histWindow, rebalanceFrequency)
    h, portValue, mu, stocks = pt.GetOptimalPortfolio(excludedStocks)


    Er = [0] * n
    p = [0] * n

    for i in range(n):
        pr = Predictor(stockList[i], startDate,horizon,TIs)
        Er[i], p[i] = pr.GetReturnPredictions()


    # --Convert mu and stocks into a dictionary
    muDic = dict(zip(stocks, mu))
    # --Make a list of returns of the user-selected stocks and convert it to percentage. This returns can be adjusted in html form
    muAdj100 = [muDic[x]*100 for x in stockList]
    #muAdj100 = [x*100 for x in Er]

    # --The predicted value of confidence level
    cflAdj100 = [x*100 for x in p]

    # --Convert the date format: .'%Y-%m-%d' is in python; '%m/%d/%Y' is in html
    d = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    startDate = d.strftime('%m/%d/%Y')
    d = datetime.datetime.strptime(endDate, '%Y-%m-%d')
    endDate = d.strftime('%m/%d/%Y')

    # --Convert the list stockList into a string. Then the html will parse the string into json object.
    stockList2 = '\", \"'.join(stockList)
    stockList2 = '[\"' + stockList2 + '\"]'

    # --Build another stock list for the name of each confidence level
    cflStockList = [0] * n
    for i in range(n):
        cflStockList[i] = 'cfl' + stockList[i]
    cflStockList2 = '\", \"'.join(cflStockList)
    cflStockList2 = '[\"' + cflStockList2 + '\"]'


    context = {
        'startDate': startDate,
        'endDate': endDate,
        'histWindow': histWindow,
        'rebalanceFrequency': rebalanceFrequency,
        'futureHorizon': horizon,
        'rf100': rf100,
        'tau': tau,
        'stockList' : mark_safe(stockList2),
        'cflStockList' : mark_safe(cflStockList2),
        'muAdj100': mark_safe(muAdj100),
		'cflAdj100': mark_safe(cflAdj100)

    }

    return render(request, 'expreturn/expreturn.html', context)



