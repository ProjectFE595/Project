# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 14:00:23 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""

import numpy
import math
import quandl
from scipy.optimize import minimize
import pandas
from pymongo import MongoClient
from MongoDataGetter import MongoDataGetter
from BlackLitterman import bl_omega
from BlackLitterman import altblacklitterman

class Portfolios(object):
    
    def __init__(self,sDate,eDate,window,rebalance,db):
        self.startDate = sDate
        self.endDate = eDate
        self.window=window
        self.rebalanceFrequency=rebalance
        self.db=db
        
    def GetBenchmarkPortfolio(self,benchmark,apiKey):
        quandl.ApiConfig.api_key = apiKey
        data = quandl.get(benchmark,start_date=self.startDate, end_date=self.endDate)
        benchmarkData = data[['Index Value']]
        benchmarkData = benchmarkData.dropna()
    
        return benchmarkData    
    
    def GetOptimalPortfolio(self,excludedStocks):
        
        stocks = [x['BBGTicker'] for x in list(self.db.Stocks.find({}))]
        stocks = [x for x in stocks if x not in excludedStocks]
        
        df = self.GetPricesDataFrame(stocks)
        ret = self.GetCleanReturns(df)
        
        n=ret.shape[0]
        m=ret.shape[1]

        self.rebalanceFreq=min(n,self.rebalanceFrequency)
        rebalanceTotal = math.floor((n - n%self.rebalanceFreq-self.window)/self.rebalanceFreq)
         
        portValue=[]
    
        for k in range(rebalanceTotal+1):
            V = 252*numpy.cov(ret[k*self.rebalanceFreq:k*self.rebalanceFreq+self.window].T)    
            mu = 252*numpy.mean(ret[k*self.rebalanceFreq:k*self.rebalanceFreq+self.window],axis=0)
            muP = numpy.mean(mu)
    
            # Solve for optimal portfolio weights
            bnds = ((0,1),)*m
            cons = ({'type': 'eq', 'fun': lambda x:  numpy.sum(x)-1.0},
                    {'type': 'eq', 'fun': lambda x:  numpy.sum(x*mu)-muP})
            h0 = numpy.ones(m)
            res= minimize(self.variance, h0, args=(V,)
                                        ,method='SLSQP',constraints=cons,bounds=bnds)
            h=res.x         
            
            if (k==rebalanceTotal):
                temp = df[k*self.rebalanceFreq+self.window:df.shape[0]-1].dot(h)
            else:
                temp = df[k*self.rebalanceFreq + self.window:(k+1)*self.rebalanceFreq + self.window].dot(h) 
            
            if k==0:    
                temp = temp/temp[0]
            elif k>0:
                temp = temp/temp[0] * portValue[k-1][portValue[k-1].size-1]
            portValue.append(temp)  
        
        portValue = self.GetDataFrameFromList(portValue)

        return h,portValue,mu,stocks
            
    def GetBLPortfolio(self,stockView,stockViewReturn,stockConfidence,tau,delta,excludedStocks):

        stocks = [x['BBGTicker'] for x in list(self.db.Stocks.find({}))]
        stocks = [x for x in stocks if x not in excludedStocks]

        df = self.GetPricesDataFrame(stocks)
        ret = self.GetCleanReturns(df)
        
        n=ret.shape[0]
        m=ret.shape[1]
        
        v=len(stockView)
        
        P = numpy.zeros((v,m))
        Q = numpy.zeros((v,1))
        
        indexh=[]
        for item in stockView:
            i = stockView.index(item)
            j = stocks.index(item)    
            P[i][j] = 1        
            Q[i] = stockViewReturn[i] #+mu[j]
            indexh.append(j)            
          
        portBLValue=[]
        
        h,portValue,unused,unusedd = self.GetOptimalPortfolio(excludedStocks) 
        rebalanceTotal = math.floor((n - n%self.rebalanceFreq-self.window)/self.rebalanceFreq)
        
    
        for k in range(rebalanceTotal+1):
            V = 252*numpy.cov(ret[k*self.rebalanceFreq:k*self.rebalanceFreq+self.window].T)    
                  
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
            
            hBL = self.AdjustBLWeights(h,hBL,indexh)
            
            if (k==rebalanceTotal):
                tempBL = df[k*self.rebalanceFreq+self.window:df.shape[0]-1].dot(hBL)
            else:
                tempBL = df[k*self.rebalanceFreq+self.window:(k+1)*self.rebalanceFreq+self.window].dot(hBL)
                
            if k==0:    
                tempBL = tempBL/tempBL[0]
            elif k>0:
                tempBL = tempBL/tempBL[0] * portBLValue[k-1][portBLValue[k-1].size-1]
            portBLValue.append(tempBL)
                  
        portBLValue = self.GetDataFrameFromList(portBLValue)
        
        return hBL,portBLValue
        
        
    def AdjustBLWeights(self,h,hBL,indexh):
        summ=0
        summ2=0
        for ind in indexh:
            summ+= hBL[ind]
            summ2+= h[ind]
                
        for ind in indexh:
            hBL[ind] = hBL[ind] * summ2/summ
            
        return hBL
                
    def GetPricesDataFrame(self,stocks):
        
        df = pandas.DataFrame([''],index=['1900-01-01'])
        dfHeaders = ['Dummy']
        
        for stock in stocks:
            dfHeaders.append(stock+' Close')
            mg = MongoDataGetter(self.db, self.startDate,self.endDate)
            data = mg.GetDataFromMongo(stock,'Prices')
            headers = data[0]
            temp = data[1:]
            indexClose=headers.index('Close')
            indexDate=headers.index('Dates')
            s = [stock+' Close']
            s.append(temp[indexClose])
            s.append(temp[indexDate])
            tempdf = pandas.DataFrame(s[1],index=s[2])
            df = pandas.concat([df, tempdf], axis=1,join='outer')
                
        df.columns = dfHeaders
        df = df.drop('Dummy',1)
        df = df.sort_index()
        
        return df
        
    def GetCleanReturns(self,df):
        
        ret = df.as_matrix()
        ret = ret[:len(ret)-1,:]
        ret = numpy.diff(ret.astype(float), axis=0)/ret[:-1].astype(float)
        ret = ret[~numpy.isnan(ret).any(axis=1)]
        ret = ret[numpy.all(numpy.abs(ret) < 1, axis=1)]

        return ret
        
    def GetDataFrameFromList(self,portValue):
    
        temp = portValue[0]
        for p in range(len(portValue)-1):
            temp = pandas.concat([pandas.DataFrame(temp),pandas.DataFrame(portValue[p+1])],axis=0)
        
        portValue = pandas.DataFrame(temp)
        portValue.index = pandas.to_datetime(portValue.index)        
        
        return portValue
    
    def variance(self,x,Sig):
    
        return numpy.dot(x,numpy.dot(Sig,x))