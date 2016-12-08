# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 14:00:23 2016
@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

This file implements a Portfolios class to calculate the Optimal tangent portfolio, 
tangent to the efficient frontier or maximal sharpe ratio. The class also
calculates the Black Litterman portfolio

"""

import numpy
import math
import quandl
from scipy.optimize import minimize
import pandas
from BlackLitterman import bl_omega
from BlackLitterman import altblacklitterman
from Predictor import Predictor
from DataHandler import DataHandler
from functools import partial
from multiprocessing.dummy import Pool

class Portfolios(object):
    
    """Constructor"""
    def __init__(self,sDate,eDate,window,rebalance,h,db):
        self.startDate = sDate
        self.endDate = eDate
        self.window=window
        self.rebalanceFrequency=rebalance
        self.horizon = h
        self.db=db        
    
    """Return Benchmark value from Quandl"""
    def GetBenchmarkPortfolio(self,benchmark,apiKey):
        quandl.ApiConfig.api_key = apiKey
        data = quandl.get(benchmark,start_date=self.startDate, end_date=self.endDate)
        benchmarkData = data[['Index Value']]
        benchmarkData = benchmarkData.dropna() #Remove NaN data
    
        return benchmarkData    
    
    """Calculate tangent portfolio (max sharpe ratio) using machine learning for expected returns"""
    def GetOptimalPortfolio(self,excludedStocks):
        
        #Get list of all stocks excluding some stocks because missing data
        stocks = [x['BBGTicker'] for x in list(self.db.Stocks.find({}))]
        stocks = [x for x in stocks if x not in excludedStocks]
        
        Xtot ={}
        Ytot ={}
        dh = DataHandler
        
        #Download machine learning features technical indicators for each stock and insert in dictionary
        for s in stocks:
            #Get the list of dates using prices 
            dataMongo = self.db.Prices.find_one({'BBGTicker' : s},{'Close' : 1})
            data=dataMongo['Close']
            dates = sorted(data.keys())
            
            #Use data only from 2009-02-04, earlier data are irrelevant
            filterDate='2009-02-04'
            filterDate = dh.HandleIncorrectDate(filterDate,'',dates)
            indexDate = dates.index(filterDate) 
            dates = dates[indexDate:len(dates)-1-self.horizon]
            
            #For each stock insert features into dictionary Xtot and output future return into dictionary Ytot
            pr = Predictor(s,self.endDate,self.horizon,self.db)
            Xtot[s]= {"ANALYTICS": pr.GetMLInputs(dates) , "DATES" : dates}
            Ytot[s]= {"RETURNS": pr.GetMLOutputs(dates) , "DATES" : dates}
        
        #Get a dataframe with date as index and prices for each stock (columns)
        df = self.GetPricesDataFrame(stocks)
        #Get matrix (array) of return, removing NaN numbers
        ret = self.GetCleanReturns(df) 

        n=ret.shape[0] #Number of rows, or number of return for each stock
        m=ret.shape[1] #number of stocks
        
        #Given number of dates and frequency (every h days), get the number of time we want to rebalance
        self.rebalanceFreq=min(n,self.rebalanceFrequency)
        rebalanceTotal = math.floor((n - n%self.rebalanceFreq-self.window)/self.rebalanceFreq)
         
        portValue=[]
        htot=[]
        mutot=[]

        #for eachbtime portfolio is rebalanced calculate optimal weights
        for k in range(rebalanceTotal+1):   
            st=0
            mu = numpy.empty(m) #expected return vector for each stock

            #Define partial function to use multi thread pool
            func = partial(self.GetExpectedReturns,Xtot,Ytot,k)
            pool = Pool(len(stocks))

            #Calculate expected returns using parallel programming multithreading
            results = pool.map(func, stocks)
            
            #close the pool and wait for the work to finish
            pool.close()
            pool.join()
            
            #Ensure we map the expected return to the correct stock and store in numpy array mu
            for s in stocks:
                for res in results:
                    if res[0]==s:
                        mu[st] = res[1]
                        st=st+1
                        break
                     
            #Calculate covariance matrix
            V = numpy.cov(ret[k*self.rebalanceFreq:k*self.rebalanceFreq+self.window].T)    
            
            #Insert expected return vector for each rebalancing
            mutot.append(mu)

            #Set optimization constraints (sum of weights = 1) and boundaries (0 <= weight <= 1)
            bnds = ((0,1),)*m
            cons = ({'type': 'eq', 'fun': lambda x:  numpy.sum(x)-1.0})
            h0 = numpy.ones(m)
            
            #Minimize the inverse of sharpe ratio to get optimal weights h
            res= minimize(self.sharpe, h0, args=(V,mu,0.001,)
                                        ,method='SLSQP',constraints=cons,bounds=bnds)
            h=res.x            
            htot.append(h) #append weights for each rebalancing 
            
            #Apply optimal weights to dataframe price to get the portfolio values for each date
            #Handle the reinvestment when the portfolio is rebalanced
            if (k==rebalanceTotal):
                temp = df[k*self.rebalanceFreq+self.window:df.shape[0]-1].dot(h)
            else:
                temp = df[k*self.rebalanceFreq + self.window:(k+1)*self.rebalanceFreq + self.window].dot(h) 
            if k==0:    
                temp = temp/temp[0]
            elif k>0:
                temp = temp/temp[0] * portValue[k-1][portValue[k-1].size-1]
            portValue.append(temp)             
        
        portValue = self.GetDataFrameFromList(portValue) #Get a dataframe instead of list

        return htot,portValue,mutot,stocks
    
    """Return stock expected return using this function in order to use multithreading"""
    def GetExpectedReturns(self,Xtot,Ytot,k,stock):
        #Retrieve the dates for each adjustment close price or close price
        dataMongo = self.db.Prices.find_one({'BBGTicker' : stock},{'Adj Close' : 1})
        if 'Adj Close' not in list(dataMongo.keys()):
            dataMongo = self.db.Prices.find_one({'BBGTicker' : stock},{'Close' : 1})
            data=dataMongo['Close']
        else:
            data=dataMongo['Adj Close']
        dates = sorted(data.keys())
        
        #Handle incorrect start and end date entered by user       
        dh = DataHandler
        self.startDate = dh.HandleIncorrectDate(self.startDate,'',dates)
        self.endDate = dh.HandleIncorrectDate('',self.endDate,dates)
        dates = dates[dates.index(self.startDate):dates.index(self.endDate)]
  
        #Prediction must consider the window for covariance matrix
        startDate = dates[k*self.rebalanceFreq + self.window]
        pr = Predictor(stock,startDate,self.horizon,self.db)
        
        #Lookup output and features and
        TIsDates = Xtot[stock]["DATES"]
        Xtrain = Xtot[stock]["ANALYTICS"][:TIsDates.index(startDate)]
        Ytrain = Ytot[stock]["RETURNS"][:TIsDates.index(startDate)]
        Xpred = Xtot[stock]["ANALYTICS"][TIsDates.index(startDate)]
        mu = [stock,pr.PredictKNN(Xtrain,Ytrain,Xpred)/self.horizon]
        
        return mu

            
    """Return the Black Litterman portfolio with view applied to the machine learning tangent portfolio"""
    def GetBLPortfolio(self,stockView,stockViewReturn,stockConfidence,tau,delta,excludedStocks):

        #Get list of all stocks excluding some stocks because missing data
        stocks = [x['BBGTicker'] for x in list(self.db.Stocks.find({}))]
        stocks = [x for x in stocks if x not in excludedStocks]

        #Get a dataframe with date as index and prices for each stock (columns)
        df = self.GetPricesDataFrame(stocks)
        #Get matrix (array) of return, removing NaN numbers
        ret = self.GetCleanReturns(df)
        
        n=ret.shape[0] #Number of rows, or number of return for each stock
        m=ret.shape[1] #number of stocks
        
        v=len(stockView) #Number of stocks in the view
        
        P = numpy.zeros((v,m)) # v×m matrix of the asset weights within each view
        Q = numpy.zeros((v,1)) # v×1 vector of the returns for each view
        
        indexh=[]
        #Populate view matrix P and Q given user inputs stockView and stockViewReturn
        for item in stockView:
            i = stockView.index(item)
            j = stocks.index(item)    
            P[i][j] = 1        
            Q[i] = stockViewReturn[i] #+mu[j]
            indexh.append(j)            
          
        portBLValue=[]
        
        self.rebalanceFrequency=n+1 #Only 1 rebalancing
        #Get tangent portfolio weights 
        h,unused,unused,unused = self.GetOptimalPortfolio(excludedStocks) 
        
        #Calculate covariance matrix
        V = numpy.cov(ret[:self.window].T)    
                  
        # Coefficient of uncertainty in the prior estimate of the mean
        # from footnote (8) on page 11               
        tauV = tau * V
        
        # k×k matrix of the covariance of the views. Ω is diagonal as the views are required to be
        #independent and uncorrelated
        Omega = numpy.zeros((v,v))
        for c in range(v):
            Omega[c][c] = bl_omega(stockConfidence[c], P[c], tauV)
            
        #Call Black Litterman function from .org website
        er, hBL, lmbda = altblacklitterman(delta, h[0], V, tau, P, Q, Omega)        
        htemp = numpy.reshape(hBL,(1,len(stocks)))
        hBL = htemp[0]
        
        #Adjust weights such that the sum of weights = 1
        hBL = self.AdjustBLWeights(h[0],hBL,indexh)            
        tempBL = df[self.window:].dot(hBL)                 
        portBLValue= [tempBL/tempBL[0]] #Adjust portfolio value
                  
        portBLValue = self.GetDataFrameFromList(portBLValue) #Get a dataframe instead of list
        
        return hBL,portBLValue
        
    """Adjust BL weights such that they sum to 1"""
    def AdjustBLWeights(self,h,hBL,indexh):
        summ=0
        summ2=0
        for ind in indexh:
            summ+= hBL[ind]
            summ2+= h[ind]
                
        for ind in indexh:
            hBL[ind] = hBL[ind] * summ2/summ
            
        return hBL
    
    """Return a merged dataframe for the list of stock 'stocks' """         
    def GetPricesDataFrame(self,stocks):
        
        #Initial dummy dataframe
        df = pandas.DataFrame([''],index=['1900-01-01'])
        dfHeaders = ['Dummy']
        
        #For each stock retrieve dataframe then merge
        for stock in stocks:
            dfHeaders.append(stock+' Close') #Stock close price header
            
            #If Adjusted close price is available then use it, else use Close price
            dataMongo = self.db.Prices.find_one({'BBGTicker' : stock},{'Adj Close' : 1})
            if 'Adj Close' not in list(dataMongo.keys()):
                dataMongo = self.db.Prices.find_one({'BBGTicker' : stock},{'Close' : 1})
                data=dataMongo['Close']
            else:
                data=dataMongo['Adj Close']
            
            dates = sorted(data.keys()) #Get sorted list of dates for each price
            
            #Handle incorrect date entered by users
            dh = DataHandler
            self.startDate = dh.HandleIncorrectDate(self.startDate,'',dates)
            self.endDate = dh.HandleIncorrectDate('',self.endDate,dates)
            
            #Filter date set
            dates = dates[dates.index(self.startDate):dates.index(self.endDate)]
            
            #Build list of prices
            close=[]            
            for dt in dates:
                close.append(data[dt])           
            s = [stock+' Close']
            s.append(close)
            s.append(dates)
            
            #Transform list to dataframe and concatenate
            tempdf = pandas.DataFrame(s[1],index=s[2])
            df = pandas.concat([df, tempdf], axis=1,join='outer')
                
        df.columns = dfHeaders #set dataframe headers
        df = df.drop('Dummy',1) #Drop initial dummy column
        df = df.sort_index() #Sort dataframe by date
        df = df.dropna(axis=0, how='any') #Drop line with NaN prices
        
        return df
    
    """Given a dataframe returns a multi dimensional array of clean returns"""
    def GetCleanReturns(self,df):
        
        ret = df.as_matrix() #Define matrix
        ret = ret[:len(ret)-1,:] 
        ret = numpy.diff(ret.astype(float), axis=0)/ret[:-1].astype(float) #Calculate daily returns
        ret = ret[~numpy.isnan(ret).any(axis=1)] #Remove NaN returns
        ret = ret[numpy.all(numpy.abs(ret) < 1, axis=1)] #Remove outlier

        return ret
    
    """Given a list of list of portfolio value return a dataframe"""
    def GetDataFrameFromList(self,portValue):
        
        #For each list of portfolio value in list transform to dataframe
        temp = portValue[0]
        for p in range(len(portValue)-1):
            temp = pandas.concat([pandas.DataFrame(temp),pandas.DataFrame(portValue[p+1])],axis=0)
        
        portValue = pandas.DataFrame(temp)
        portValue.index = pandas.to_datetime(portValue.index)        
        
        return portValue
    
    """Inverse of shrpe ratio function of covariance matrix Sig, """
    """portfolio weights w, vector of expected returns Er, and risk free rate rf"""
    def sharpe(self,w,Sig,Er,rf):
    
        return numpy.dot(w,numpy.dot(Sig,w))/(numpy.dot(Er,w) - rf)             