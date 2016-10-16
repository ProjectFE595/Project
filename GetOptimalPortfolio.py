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

def GetOptimalPortfolio(benchmark,apiKey):

    quandl.ApiConfig.api_key = apiKey
    data = quandl.get(benchmark)
    data['Date'] = data.index.values
    data['Date'] = data['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    benchmarkData = data[['Date','Index Value']]
    benchmarkData['Returns'] = benchmarkData['Index Value'].pct_change()
    benchmarkData = benchmarkData.dropna()

    client = MongoClient()
    db = client.Project
    
    stocks =[x['BBGTicker'] for x in list(db.Stocks.find({}))]

    df = pandas.DataFrame([''],index=['1900-01-01'])
    
    for stock in stocks:
        if stock not in ['GOOG','AVGO','BRCM','CHTR','CMCSK','DISCK','FB','GMCR','KHC','LMCA','LVNTA','SNDK','TSLA','TRIP','VRSK','WBA']:      
            s = GetDataSerieFromMongo(stock,startDate='2007-01-03',endDate='2016-10-14')
            s[0,1] = stock+' Close'
            tempdf = pandas.DataFrame(s[:,[1]],index=s[:,2])
            df = pandas.concat([df, tempdf], axis=1,join='outer')
    
    df = df.sort_index(ascending=False)
#    df.to_csv('test.csv', sep=',', encoding='utf-8')
    
    df = df[1:]
    s = df.as_matrix()
    s = s[:len(s)-1,1:]
    s = numpy.diff(s.astype(float), axis=0)
    s = s[~numpy.isnan(s).any(axis=1)]

         
    Q = numpy.cov(s.T)    
    Qm1 = inv(Q);
    i=numpy.ones(Q.shape);
    mu=numpy.mean(s[0:120],axis=1)
    rf=0.01
    muE = mu - rf*i;

    h=1/(numpy.transpose(i).dot(Qm1.dot(muE))) * (Qm1.dot(muE));
    sig2 = numpy.transpose(h).dot(Q.dot(h));
    rp = numpy.transpose(h).dot(mu);
    #return h, rp, math.sqrt(sig2)    

    return df
    
    