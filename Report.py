# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 19:04:23 2016

@author: Hugo
"""

from Predictor import Predictor
from DataHandler import DataHandler
import pandas

class Report(object):
    
    def __init__(self,sDate,db):

        self.startDate = sDate
        self.db=db        
        
    def PopulateReport(self):
        
        stocks =[x['BBGTicker'] for x in list(self.db.Stocks.find({}))]
        
        dfHeaders = ['Dummy']
        df = pandas.DataFrame([''],index=['1900-01-01'])
        
        for s in stocks:
            
            horizon=10
            r = self.db.Returns.find_one({'BBGTicker' : s},{'FUTURERETURN'+str(horizon)+'DAYS' : 1})               
            returns=r['FUTURERETURN'+str(horizon)+'DAYS']
            
            dfHeaders.append(s+' Predict return horizon '+str(horizon)+'days') #Stock Predicted return header
            dfHeaders.append(s+' Real return horizon '+str(horizon)+'days') #Stock Real return header
            
            dataMongo = self.db.Prices.find_one({'BBGTicker' : s},{'Adj Close' : 1})
            if 'Adj Close' not in list(dataMongo.keys()):
                dataMongo = self.db.Prices.find_one({'BBGTicker' : s},{'Close' : 1})
                data=dataMongo['Close']
            else:
                data=dataMongo['Adj Close']
            dates = sorted(data.keys())            
            
            dh = DataHandler
            self.startDate = dh.HandleIncorrectDate(self.startDate,'',dates)
            
            filterDate='2009-02-05'
            indexDate = dates.index(filterDate) 
            filterDates = dates[indexDate:] 
            
            dates=dates[dates.index(self.startDate):]
            
            reportPred=[] 
            reportReal = []
            dateReturns = sorted(returns.keys())
            dateReturns = dateReturns[dateReturns.index(self.startDate):]
            pr = Predictor(s,self.startDate,horizon,self.db)
            #Get machine learning numpy array inputs        
            X,unused = pr.GetMLInputs(filterDates)
                        
            #Get machine learning numpy array outputs
            Y = pr.GetMLOutputs(dateReturns)
            

            for dt in dates:
                
                print(dt)
                Xpred = X[dates.index(dt)][:]
                Xtrain=X[:dates.index(dt)-1][:]
                Ytrain=Y[:dates.index(dt)-1]
                print(Xpred)
                print(Xtrain[:][:])
                print(X)
                #Predict future return at time 'self.date'              
                rPred = pr.PredictKNN(Xtrain,Ytrain,Xpred)                       
                reportPred.append(rPred)
                if dt in dateReturns:
                    reportReal.append(returns[dt])
                else:
                    reportReal.append(0)
            
            dfList=[]
            dfList.append(reportPred)
            dfList.append(reportReal)
            dfList.append(dates)
            
            #Transform list to dataframe and concatenate
            tempdf = pandas.DataFrame(s[0],s[1],index=s[2])
            df = pandas.concat([df, tempdf], axis=1,join='outer')
            print(s)
                
        df.columns = dfHeaders #set dataframe headers
        df = df.drop('Dummy',1) #Drop initial dummy column
