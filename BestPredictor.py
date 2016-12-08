# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 17:36:37 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

This file uses machine learning to calculate the best combination of technical indicators and KNN such
that the standard deviation of the time serie Y = (Future return real - future return)
is minimum
"""
import numpy
from sklearn.preprocessing import Imputer
from sklearn.neighbors import KNeighborsRegressor
import itertools
import math
from datetime import datetime
from DataHandler import DataHandler
from pymongo import MongoClient

class BestPredictor(object):
    """Constructor"""
    def __init__(self,TIs):
        self.TIs = TIs
    
    """Find the best combination of TIs and KNN for each future return horizon"""
    """such that the prediction - real returns standard deviation is minimum"""
    """Inserts the results in Mongo DB Scores collection"""
    def GetExhaustivePredictorsKNN(self,s):
        
        client = MongoClient()
        db = client.Project   
        
        #Print time to monitor execution time
        rTime=datetime.now()    
        print(rTime)
        print(s)
        
        #Retrieve all available dates using close price
        dataMongo = db.Prices.find_one({'BBGTicker' : s},{'Close' : 1})
        data = dataMongo['Close']
        dates = sorted(data.keys()) #sort dates
        
        #Use data only after 2010-01-04, handle date if doesn't exist
        filterDate = '2010-01-04'
        dh = DataHandler
        filterDate = dh.HandleIncorrectDate(filterDate,'',dates)       
        dates = dates[dates.index(filterDate):]
        
        #Score will contain standard deviation value, corresponding TIs, KNN and horizon combination
        record={'HEADERS' : ['StdScore','TIs','Horizon','KNN'],'BBGTicker':s}
        
        #Retrieve TIs value for 1 stock s
        TIsValues = db.Analytics.find_one({'BBGTicker' : s})
        
        #Retrieve future returns value for 1 stock s
        r = db.Returns.find_one({'BBGTicker' : s})
        
        #For each horizon find the best score
        for horizon in range(15):
            horizon=horizon+1                
            scoreResults=[]     
            Kmax = 10 #We do not consider more than 10 KNN points
            
            #Populate future returns numpy array using dictionary from Mongo DB
            futReturn = numpy.zeros(shape=(len(dates),))                             
            returns=r['FUTURERETURN'+str(horizon)+'DAYS']
            i = 0
            for dt in dates:
                if i<len(dates)-horizon:
                    futReturn[i] = returns[dt]
                i=i+1
            futReturn = futReturn[:futReturn.shape[0]-horizon]            
            
            #Populate test and train output data set (70% train, 30% test)
            L=futReturn.shape[0]
            Ytrain = futReturn[:math.ceil(0.7*L)]
            Ytest = futReturn[math.ceil(0.7*L):]
            
            #For each neighbor and each TIs combination calculate prediction and find the best predictor
            for neighbor in range(Kmax-3):
                for k in range(len(self.TIs)-1):
                    for comb in itertools.combinations(range(len(self.TIs)),k+1):
                        
                        #Keep TIs name in the list inputNames
                        inputNames = []
                        for j in comb:
                            inputNames.append(self.TIs[j])                           
                        
                        #Populate numpy array of TIs input X using Mongo DB dictionary
                        X = numpy.zeros(shape=(len(dates),len(comb)))
                        j=0
                        for ti in comb:
                            t = TIsValues[self.TIs[ti]]
                            i=0
                            for dt in dates:                                                      
                                X[i][j] = t[dt]
                                i=i+1
                            j=j+1
                            
                        #Filter by removing last TIs given the horizon
                        X = X[:X.shape[0]-horizon][:]
                        
                        #Use the mean of TIs when NaN is found
                        imr = Imputer(missing_values='NaN',strategy='mean',axis=0)
                        imr.fit(X)
                        X = imr.transform(X)
                        
                        #We use minimum 3 KNN and max 10
                        K=neighbor+3

                        #Populate test and train input data set (70% train, 30% test)
                        Xtrain = X[:math.ceil(0.7*L)]
                        Xtest = X[math.ceil(0.7*L):] 
                         
                        #Use scikit learn KNN regressor to make prediction on the test dataset
                        neigh = KNeighborsRegressor(n_neighbors=K, weights='distance')
                        neigh.fit(Xtrain,Ytrain) 
                        Ypred = neigh.predict(Xtest)
                        
                        #Calculate the standard deviation of (Yreal - Ypred)
                        #and store result in list scoreResults
                        sco = Ytest - Ypred
                        score = numpy.std(sco)
                        scoreResults.append([score,inputNames,horizon,K])           
            
            #Find the combination of TIs and KNN given a horizon having a minimum standard deviation 
            minn=scoreResults[0][0]
            for k in range(len(scoreResults)):
                if scoreResults[k][0]<minn:
                    minn=scoreResults[k][0]
                    index = k            
            record.update({ 'BEST_SCORE_HORIZON_'+str(horizon)+'_DAYS': scoreResults[index]})
        
        #Insert the best predictor in Mongo DB
        db.Scores.delete_many({'BBGTicker':s})
        mongoRecord=[record]
        db.Scores.insert_many(mongoRecord)
        print(s)                