# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 15:59:16 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

This file implements machine learning predictors, KNN in particular. The future returns
are predicted given a set of features which are technical indicators
"""

import numpy
from sklearn.preprocessing import Imputer
from sklearn.neighbors import KNeighborsRegressor
import warnings
warnings.filterwarnings('ignore')

class Predictor(object):
    
    """Constructor"""
    def __init__(self,s,dt,h,db):
        self.stock=s
        self.date=dt
        self.horizon=h
        self.db=db    
    
    """
    Return a set of technical indicators for the train set and the vector
    of technical indicator we need for the date we want to predict future return
    """
    def GetMLInputs(self,dates):
        
        #Find best combination of TIs and K nearesrt neighbors for the given stock and horizon
        TIs,K = self.GetBestPredictorsKNN(self.stock,self.horizon)

        #Technical indicator inputs for machine learning (features)
        X = numpy.zeros(shape=(len(dates),len(TIs)))

        #For each indicator, get time serie (dictionary) and populate numpy array X
        for j in range(len(TIs)):
            t = self.db.Analytics.find_one({'BBGTicker' : self.stock},{TIs[j] : 1})         
            TIsValues = t[TIs[j]]
            i=0
            for dt in dates:               
                X[i][j] = TIsValues[dt]
                i=i+1
        
        #Clean NaN value by using average
        imr = Imputer(missing_values='NaN',strategy='mean',axis=0)
        imr.fit(X)
        X = imr.transform(X)
        
        return X   
        
    """Populate numpy array containing future return given the horizon"""
    def GetMLOutputs(self,dates):  
        
        #Lookup future returns in mongo DB given horizon
        r = self.db.Returns.find_one({'BBGTicker' : self.stock},{'FUTURERETURN'+str(self.horizon)+'DAYS' : 1})               
        returns=r['FUTURERETURN'+str(self.horizon)+'DAYS']
        
        #Populate numpy array Y by looking up in future return dictionary from Mongo
        Y = numpy.zeros(len(dates))
        i=0
        for dt in dates:
            Y[i] = returns[dt]
            i=i+1
            
        return Y

    """Predict future return given input Xpred and training data X and Y"""
    def PredictKNN(self,Xtrain,Ytrain,Xpred):
        
        #Get the best combination of TIs and K nearest neighbors
        TIs,K = self.GetBestPredictorsKNN(self.stock,self.horizon)
        
        #Use scikit learn to fit the estimator and make prediction
        neigh = KNeighborsRegressor(n_neighbors=K, weights='distance')
        neigh.fit(Xtrain,Ytrain) 
        Ypred = neigh.predict(Xpred)

        return Ypred

    def GetBestPredictorsKNN(self,stock,horizon):
        
        #Lookup combination of TIs having best score
        pred = list(self.db.Scores.find({'BBGTicker':stock}))
        headers=pred[0]['HEADERS']
        
        dicKeys = list(pred[0].keys())
        
        #Lookup up for the corresponding closest horizon available
        maxH=0
        for k in dicKeys:
            if 'BEST_SCORE_HORIZON_' in k:
                h = k
                h = h.replace('BEST_SCORE_HORIZON_','')
                h = h.replace('_DAYS','')
                h = int(h)
                if h>maxH:
                    maxH=h 
                    
        #Combination of K nearest neighbor and TIs having best score       
        bestScore = 'BEST_SCORE_HORIZON_'+str(maxH)+'_DAYS'
        
        for k in dicKeys:
            if str(horizon) in k:
                bestScore=k
        
        TIsIndex = headers.index('TIs')
        KNNIndex = headers.index('KNN')
        
        return pred[0][bestScore][TIsIndex],pred[0][bestScore][KNNIndex]