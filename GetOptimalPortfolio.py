# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 14:00:23 2016

@author: Hugo
"""
import quandl
import numpy
import math
from numpy.linalg import inv
import pandas
from pymongo import MongoClient
from GetDataSerieFromMongo import GetDataSerieFromMongo

def GetOptimalPortfolio(benchmark,apiKey,startDate,endDate):

    quandl.ApiConfig.api_key = apiKey
    data = quandl.get(benchmark,start_date=startDate, end_date=endDate)
    benchmarkData = data[['Index Value']]
    benchmarkData = benchmarkData.dropna()
    
    init = (benchmarkData.iloc[0].values)[0]
    benchmarkData[['Index Value']] = benchmarkData[['Index Value']]/init
    
    client = MongoClient()
    db = client.Project
    
    stocks =[x['BBGTicker'] for x in list(db.Stocks.find({}))]

    df = pandas.DataFrame([''],index=['1900-01-01'])
    dfHeaders = ['Dummy']
    
    for stock in stocks:
        if stock not in ['GOOG','AVGO','BRCM','CHTR','CMCSK','DISCK','FB','GMCR','KHC','LMCA','LVNTA','SNDK','TSLA','TRIP','VRSK','WBA']:      
            dfHeaders.append(stock)
            s = GetDataSerieFromMongo(stock,startDate,endDate)   
            s[0,1] = stock+' Close'
            tempdf = pandas.DataFrame(s[:,[1]],index=s[:,2])
            df = pandas.concat([df, tempdf], axis=1,join='outer')
            
    df.columns = dfHeaders
    df = df.drop('Dummy',1)
    df = df.sort_index()
    df.to_csv('test.csv', sep=',', encoding='utf-8')
    
    s = df.as_matrix()
    s = s[:len(s)-1,:]
    s = numpy.diff(s.astype(float), axis=0)/s[:-1].astype(float)
    s = s[~numpy.isnan(s).any(axis=1)]

    window=120
    rebalanceFreq=min(s.shape[0],250)
    rebalanceTotal = math.floor((s.shape[0] - s.shape[0]%rebalanceFreq-window)/rebalanceFreq)
    i=numpy.ones(s.shape[1])
    rf=0.00001
   
    portValue=[]
    htot=[]
    mutot=[]
    for k in range(rebalanceTotal+1):
        Q = numpy.cov(s[k*rebalanceFreq:k*rebalanceFreq+window].T)    
        Qm1 = inv(Q)
        mu=numpy.mean(s[k*rebalanceFreq:k*rebalanceFreq+window],axis=0)
        muP=numpy.mean(mu)
        muE = mu - rf*i
        A = numpy.transpose(mu).dot(Qm1.dot(mu))
        B = numpy.transpose(mu).dot(Qm1.dot(i))
        C = numpy.transpose(i).dot(Qm1.dot(i))
        D = A*C-B*B

        h = (C * muP - B)/D * Qm1.dot(mu) + (A - B*muP)/D * Qm1.dot(i)
        #h=1/(numpy.transpose(i).dot(Qm1.dot(muE))) * (Qm1.dot(muE))
        if (k==rebalanceTotal):
            temp = df[k*rebalanceFreq+window:df.shape[0]-1].pct_change().dropna().dot(h)
        else:
            temp = df[k*rebalanceFreq+window:(k+1)*rebalanceFreq+window].pct_change().dropna().dot(h)                
        portValue.append(temp)  
        htot.append(h)
        mutot.append(mu)

    temp = portValue[0]
    for p in range(len(portValue)-1):
        temp = pandas.concat([pandas.DataFrame(temp),pandas.DataFrame(portValue[p+1])],axis=0)
    
    portValue = temp
    portValue.index = pandas.to_datetime(portValue.index)
    
    portValue[0][0]=1
    for r in range(portValue.shape[0]-1):
        if (abs(portValue[0][r+1])>1):
            portValue[0][r+1]=0
        portValue[0][r+1]=portValue[0][r]*(1+portValue[0][r+1])
    
    return portValue,benchmarkData,htot,mutot
    
    