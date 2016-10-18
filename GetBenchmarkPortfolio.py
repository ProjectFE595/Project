# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 18:45:36 2016

@author: Hugo
"""
import quandl

def GetBenchmarkPortfolio(benchmark,apiKey,startDate,endDate):
    quandl.ApiConfig.api_key = apiKey
    data = quandl.get(benchmark,start_date=startDate, end_date=endDate)
    benchmarkData = data[['Index Value']]
    benchmarkData = benchmarkData.dropna()
    
    #init = (benchmarkData.iloc[0].values)[window]
    #benchmarkData[['Index Value']] = benchmarkData[['Index Value']]/init

    return benchmarkData    