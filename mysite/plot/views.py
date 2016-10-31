# import numpy as np
# import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt
import quandl
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

import PIL
import PIL.Image
import io
from io import *
import datetime
import pandas
import numpy
import math
from plot.functions.GetBenchmarkPortfolio import GetBenchmarkPortfolio
from plot.functions.GetOptimalPortfolio import GetOptimalPortfolio
from plot.functions.GetAnalyticsFromMongo import GetAnalyticsFromMongo
from plot.functions.GetReturnPredictions import GetReturnPredictions
from plot.functions.LoadPricesInMongo import LoadPricesInMongo
from plot.functions.CalculateIndicators import CalculateIndicators
from plot.functions.GetDataSerieFromMongo import GetDataSerieFromMongo


def graphic(request):
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    d = datetime.datetime.strptime(startDate, '%m/%d/%Y')
    startDate =  d.strftime('%Y-%m-%d')
    d = datetime.datetime.strptime(endDate, '%m/%d/%Y')
    endDate = d.strftime('%Y-%m-%d')
    histWindow = int(request.POST['histWindow'])
    rebalanceFrequency = int(request.POST['rebalanceFrequency'])
    rf = float(request.POST['rf'])/100
    tau = float(request.POST['tau'])
    # stockList = request.POST.getlist('stockList')
    futureHorizon= int(request.POST['futureHorizon'])



    today = datetime.date.today()
    today = '2016-09-29'
    quandlKey = "yJRsZwcETsegkLY-PThM"
    benchmark = 'NASDAQOMX/NDX'
    # LoadPricesInMongo(apiKey=quandlKey,today)
    # LoadPricesInMongo(apiKey=quandlKey)
    # CalculateIndicators()

    ErYHOO, pYHOO, meanScores, stdScores = GetReturnPredictions('YHOO', startDate, futureHorizon)
    ErCSCO, pCSCO, meanScores, stdScores = GetReturnPredictions('CSCO', startDate, futureHorizon)
    ErAAPL, pAAPL, meanScores, stdScores = GetReturnPredictions('AAPL', startDate, futureHorizon)
    ErGOOGL, pGOOGL, meanScores, stdScores = GetReturnPredictions('GOOGL', startDate, futureHorizon)

    ErYHOO = float(request.POST['YHOO']) / 100
    ErCSCO = float(request.POST['CSCO']) / 100
    ErAAPL = float(request.POST['AAPL']) / 100
    ErGOOGL = float(request.POST['GOOGL']) / 100

    #startDate = '2010-02-05'
    #endDate = '2013-10-30'
    #histWindow = 120
    #rebalanceFrequency = 2500

    stockView = ['YHOO', 'CSCO', 'AAPL', 'GOOGL']
    # stockViewReturn = [-0.055,0.05,0.06,0.1]
    # stockConfidence = [0.9,0.8,0.5,0.8]
    stockViewReturn = [ErYHOO, ErCSCO, ErAAPL, ErGOOGL]
    stockConfidence = [pYHOO, pCSCO, pAAPL, pGOOGL]

    #rf = 0.0001
    #tau = 0.025

    benchmarkValue = GetBenchmarkPortfolio(benchmark, quandlKey, startDate, endDate)
    # Risk aversion of the market
    delta = (252 * numpy.mean(benchmarkValue.pct_change().dropna()) - rf) / (
    math.sqrt(252) * numpy.std(benchmarkValue.pct_change().dropna()))
    delta = delta[0]
    portValue, portBLValue, h, hBL = GetOptimalPortfolio(benchmark,
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

    dfConcatenate = pandas.concat([portValue, portBLValue, benchmarkValue], axis=1, join='inner')
    init = dfConcatenate['Index Value'][0]
    dfConcatenate['Index Value'] = dfConcatenate['Index Value'] / init
    dfClean = dfConcatenate[['OptimalPort', 'BlackLittermanPort', 'Index Value']]

    # Plot benchmark and optimal portfolio
    plt.figure(figsize=(20, 7))
    # plt.xticks( dfConcatenate[0], dfConcatenate.index.values )
    port, = plt.plot(dfClean['OptimalPort'], 'r', label='Optimal Portfolio')
    portBL, = plt.plot(dfClean['BlackLittermanPort'], 'g', label='Black-Litterman Portfolio')
    ben, = plt.plot(dfClean['Index Value'], 'b', label='Benchmark')

    plt.legend(handles=[port, portBL, ben])

    buffer = io.BytesIO()
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    graphIMG = PIL.Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
    graphIMG.save(buffer, "JPEG")

    return HttpResponse(buffer.getvalue(), content_type="Image/png")
 #   return render(request, 'plot/plot.html', {'plot.jpg': buffer})


