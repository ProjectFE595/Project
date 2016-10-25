# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 14:00:23 2016

@author: Hugo
"""
import numpy
import math
import scipy
from scipy.optimize import minimize
from numpy.linalg import inv
import pandas
from pymongo import MongoClient
from GetDataSerieFromMongo import GetDataSerieFromMongo
from BlackLitterman import bl_omega
from BlackLitterman import altblacklitterman

def GetOptimalPortfolio(benchmark,apiKey,startDate,endDate,window,rebalanceFrequency,
                        tau,stockView,stockViewReturn,stockConfidence,delta):
    
    client = MongoClient()
    db = client.Project
    
    stocks =[x['BBGTicker'] for x in list(db.Stocks.find({}))]
    stocks = [x for x in stocks if x not in ['GOOG','AVGO','BRCM','CHTR','CMCSK','DISCK','FB','GMCR','KHC','LMCA','LVNTA','SNDK','TSLA','TRIP','VRSK','WBA']]

    df = pandas.DataFrame([''],index=['1900-01-01'])
    dfHeaders = ['Dummy']
    
    for stock in stocks:
        dfHeaders.append(stock)
        s = GetDataSerieFromMongo(stock,startDate,endDate) 
        indexDate= numpy.where(s[0]=='Date')[0][0]
        indexClose = numpy.where(s[0]=='Close')[0][0]
        s[0,indexClose] = stock+' Close'
        tempdf = pandas.DataFrame(s[:,[indexClose]],index=s[:,indexDate])
        df = pandas.concat([df, tempdf], axis=1,join='outer')
            
    df.columns = dfHeaders
    df = df.drop('Dummy',1)
    df = df.sort_index()
    
    s = df.as_matrix()
    s = s[:len(s)-1,:]
    s = numpy.diff(s.astype(float), axis=0)/s[:-1].astype(float)
    s = s[~numpy.isnan(s).any(axis=1)]
    s = s[numpy.all(numpy.abs(s) < 1, axis=1)]
    #numpy.savetxt('test.csv', X=s, delimiter=',')

    n=s.shape[0]
    m=s.shape[1]
    v=len(stockView)
    rebalanceFreq=min(n,rebalanceFrequency)
    rebalanceTotal = math.floor((n - n%rebalanceFreq-window)/rebalanceFreq)
    i=numpy.ones(m)

    P = numpy.zeros((v,m))
    Q = numpy.zeros((v,1))
     
    portValue=[]
    portBLValue=[]

    for k in range(rebalanceTotal+1):
        V = 252*numpy.cov(s[k*rebalanceFreq:k*rebalanceFreq+window].T)    
        Vm1 = inv(V)
        mu = 252*numpy.mean(s[k*rebalanceFreq:k*rebalanceFreq+window],axis=0)
        muP = numpy.mean(mu)
        A = numpy.transpose(mu).dot(Vm1.dot(mu))
        B = numpy.transpose(mu).dot(Vm1.dot(i))
        C = numpy.transpose(i).dot(Vm1.dot(i))
        D = A*C-B*B

        h = (C * muP - B)/D * Vm1.dot(mu) + (A - B*muP)/D * Vm1.dot(i)  
        print(h)
        print(sum(h))
        # Solve for optimal portfolio weights
        bnds = ((0.0005,1),)*m
        cons = ({'type': 'eq', 'fun': lambda x:  numpy.sum(x)-1.0},
                {'type': 'eq', 'fun': lambda x:  numpy.sum(x*mu)-muP})
        h0 = numpy.ones(m)
        res= minimize(variance, h0, args=(V,)
                                    ,method='SLSQP',constraints=cons,bounds=bnds)
        h=res.x        
        print(h)
        print(sum(h))
        indexh=[]
        for item in stockView:
            i = stockView.index(item)
            j = stocks.index(item)    
            P[i][j] = 1        
            Q[i] = mu[j]+stockViewReturn[i]
            indexh.append(j)
              
        # Coefficient of uncertainty in the prior estimate of the mean
        # from footnote (8) on page 11               
        tauV = tau * V
        
        Omega = numpy.zeros((v,v))
        for c in range(v):
            Omega[c][c] = bl_omega(stockConfidence[c], P[c], tauV)
            
        #Omega = numpy.dot(numpy.dot(P,tauV),P.T)
        er, hBL, lmbda = altblacklitterman(delta, h, V, tau, P, Q, Omega)        
        htemp = numpy.reshape(hBL,(1,len(stocks)))
        hBL = htemp[0]
        
        summ=0
        summ2=0
        for ind in indexh:
            summ+= hBL[ind]
            summ2+= h[ind]
            
        for ind in indexh:
            hBL[ind] = hBL[ind] * summ2/summ
        
        if (k==rebalanceTotal):
            temp = df[k*rebalanceFreq+window:df.shape[0]-1].pct_change().dropna().dot(h)
            tempBL = df[k*rebalanceFreq+window:df.shape[0]-1].pct_change().dropna().dot(hBL)
        else:
            temp = df[k*rebalanceFreq+window:(k+1)*rebalanceFreq+window].pct_change().dropna().dot(h) 
            tempBL = df[k*rebalanceFreq+window:(k+1)*rebalanceFreq+window].pct_change().dropna().dot(hBL)
            
        portValue.append(temp)
        portBLValue.append(tempBL)

    temp = portValue[0]
    for p in range(len(portValue)-1):
        temp = pandas.concat([pandas.DataFrame(temp),pandas.DataFrame(portValue[p+1])],axis=0)
    
    portValue = pandas.DataFrame(temp)
    portValue.index = pandas.to_datetime(portValue.index)
    
    portValue[0][0]=1
    for r in range(portValue.shape[0]-1):
        if (abs(portValue[0][r+1])>1):
            portValue[0][r+1]=0
        portValue[0][r+1]=portValue[0][r]*(1+portValue[0][r+1])
    
    
    tempBL = portBLValue[0]
    for p in range(len(portBLValue)-1):
        tempBL = pandas.concat([pandas.DataFrame(tempBL),pandas.DataFrame(portBLValue[p+1])],axis=0)
    
    portBLValue = pandas.DataFrame(tempBL)
    portBLValue.index = pandas.to_datetime(portBLValue.index)
    
    portBLValue[0][0]=1
    for r in range(portBLValue.shape[0]-1):
        if (abs(portBLValue[0][r+1])>1):
            portBLValue[0][r+1]=0
        portBLValue[0][r+1]=portBLValue[0][r]*(1+portBLValue[0][r+1])
    
    return portValue,portBLValue, h , hBL
    
def variance(x,Sig):
    
    return numpy.dot(x,numpy.dot(Sig,x))