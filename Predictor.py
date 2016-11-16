# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 15:59:16 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""
import numpy
from pymongo import MongoClient
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import cross_val_score
from MongoDataGetter import MongoDataGetter
from DataHandler import DataHandler
import itertools
import warnings
warnings.filterwarnings('ignore')

class Predictor(object):
    
    def __init__(self,s,dt,h,tis,db):
        self.stock=s
        self.date=dt
        self.horizon=h
        self.db=db  
        self.TIs=self.GetBestPredictors(s,h)       
        
    def GetMLInputs(self,data,headers):
        
        datePred = data[headers.index('Dates')].index(self.date)
        
        """
        Prepare inputs for machine learning, select TIs, transpose data, convert list to array 
        """
    
        #Select TIs corresponding index
        TIsIndex=[]    
        for i in range(len(self.TIs)):
            TIsIndex.append(headers.index(self.TIs[i]))
    
        #Select all TIs data and append in list
        XpredList=[]
        XList=[]
        for index in TIsIndex:
            XpredList.append(data[index][datePred])
            XList.append(data[index][:datePred])
            
        #Convert to array and transpose    
        Xpred=numpy.asarray(XpredList)
        Xpred = Xpred.T
                    
        X=numpy.asarray(XList)
        X = X.T
                                   
        #Remove NaN and replace by the mean
        imr = Imputer(missing_values='NaN',strategy='mean',axis=0)
        imr.fit(X)
        X = imr.transform(X)

        return X,Xpred   
        
    def GetMLOutputs(self,data,headers):  

        datePred = data[headers.index('Dates')].index(self.date)  
        
        """
        Calculate the outputs (future returns) and classify them in intervals
        Future returns are calculated base on an horizon (x days future returns)
        """

        indexClose=headers.index('Close')
        prices = numpy.copy(data[indexClose][:datePred])
        avgFutureReturn = numpy.empty(len(prices))
        for i in range(len(prices)-self.horizon):               
            temp=0                
            for k in range(self.horizon):
                temp+= prices[k+i] #Average price for the trend        
            avgFutureReturn[i]= temp/(self.horizon*prices[i])-1
    
        #the last futures cannot be calculated, set to the mean
        for i in range(self.horizon):
            avgFutureReturn[len(avgFutureReturn)-self.horizon+i]=numpy.mean(avgFutureReturn)
                   
        Y,countMinus,countStable,countPlus = self.ClassifyReturns(avgFutureReturn)
        
        return Y,countMinus,countStable,countPlus


    def ClassifyReturns(self,futureReturn):
        
        returnClassification = numpy.empty([len(futureReturn)],dtype="S100")
            
        halfSigma = 0.5*numpy.std(futureReturn)
        halfSigmaStr=str(halfSigma)
        halfSigmaStrMin=str(-halfSigma)        
            
        countMinus=0
        countStable=0
        countPlus=0
        for i in range(futureReturn.size):               
            if  futureReturn[i] < -halfSigma :
                countMinus=countMinus+1
                returnClassification[i]='[-0.3;'+halfSigmaStrMin+']'
            if -halfSigma <= futureReturn[i] < halfSigma :
                countStable=countStable+1
                returnClassification[i]='['+halfSigmaStrMin+';'+halfSigmaStr+']'            
            if halfSigma <= futureReturn[i] :
                countPlus=countPlus+1
                returnClassification[i]='['+halfSigmaStr+';0.3]'
                
        return returnClassification,countMinus,countStable,countPlus
        
    def FitModelWithStratifiedKFold(self,X,Y):
        skf = StratifiedKFold(n_folds=10, y=Y)
        
        for train, test in skf:
            #Pipeline standardize, apply LDA for dimension reduction and apply Logistic regression    
            pipe_lr = Pipeline([
                    ('scl', StandardScaler()),
                    ('clf', LogisticRegression(penalty='l1',C=0.1,random_state=1))
                                ])                               
            pipe_lr.fit(X[train], Y[train]) 
            
        return pipe_lr
        
    def Predict(self,X,Y,Xpred):
        
        """
        Run machine learning algorithm to fit the data
        """
        
        #Stratified sampling to make classes evenly distributed across all folds
        #Use scikit Label encoder to classify the outputs
        class_le = LabelEncoder()
        Y = class_le.fit_transform(Y)
        
        pipe_lr = self.FitModelWithStratifiedKFold(X,Y)
            
        #Predict the data for date (predict interval)
        Ypred = pipe_lr.predict(Xpred)
        proba = pipe_lr.predict_proba(Xpred)
        probaMax = proba[0][Ypred[0]]
        
        #Take middle of the interval for the prediction
        interval = class_le.inverse_transform(Ypred)[0].decode()
        lowReturn = float(interval[1+interval.index('['):interval.index(';')])
        highReturn = float(interval[1+interval.index(';'):interval.index(']')])
        returnPredict = (lowReturn+highReturn)/2
            
        return returnPredict,probaMax


    def GetReturnPredictions(self):

        """
        Download the analytics TIs data from Mongo
        """
        mg = MongoDataGetter(self.db,sDate='2008-01-05')
        dataMongo = mg.GetDataFromMongo(self.stock,'TIs')
        
        headers = dataMongo[0]
        data = dataMongo[1:] #Remove headers
        
        dh = DataHandler(self.date,'')
        self.date,unused = dh.HandleIncorrectDate(data[headers.index('Dates')])
        
        X,Xpred = self.GetMLInputs(data,headers)
        
        Y,countMinus,countStable,countPlus = self.GetMLOutputs(data,headers)
        
        returnPredict,probaMax = self.Predict(X,Y,Xpred)
                                    
        return returnPredict,probaMax
        
        
    def GetBestPredictors(self,stock,horizon):
    
        pred = list(self.db.Scores.find({'BBGTicker':stock}))
        headers=pred[0]['HEADERS']
        
        dicKeys = list(pred[0].keys())
        
        maxH=0
        for k in dicKeys:
            if 'BEST_SCORE_HORIZON_' in k:
                h = k
                h = h.replace('BEST_SCORE_HORIZON_','')
                h = h.replace('_DAYS','')
                h = int(h)
                if h>maxH:
                    maxH=h
                
        bestScore = 'BEST_SCORE_HORIZON_'+str(maxH)+'_DAYS'
        
        for k in dicKeys:
            if str(horizon) in k:
                bestScore=k
    
        TIsIndex = headers.index('TIs')
        
        return pred[0][bestScore][TIsIndex]
                
    
    def GetExhaustivePredictors(self,s,TIs):
        
        mg = MongoDataGetter(self.db,sDate='2002-01-04',eDate='')
        dataMongo = mg.GetDataFromMongo(s,'TIs')  
        
        headers = dataMongo[0]
           
        data = dataMongo[1:] #Remove headers
        
        #Select TIs corresponding index
        TIsIndex=[]    
        for i in range(len(TIs)):
            TIsIndex.append(headers.index(TIs[i]))
    
        inputs=[]
        #Select all TIs data and append in list
        for index in TIsIndex:
            inputs.append(index)
        
        print(s)
        record={'HEADERS' : ['MeanScore','StdScore',
                                          'CountMinus','CountStable','CountPlus','TIs','Horizon','Classes'],
                                          'BBGTicker':s}
        
        tempo = range(1)
        for h in tempo:
            horizon=h+20                    
                
            indexClose=headers.index('Close')
            
            prices = numpy.copy(data[indexClose])
            avgFutureReturn = numpy.empty(len(prices))
            for i in range(len(prices)-horizon):               
                temp=0                
                for k in range(horizon):
                    temp+= prices[k+i] #Average price for the trend        
                avgFutureReturn[i]= temp/(horizon*prices[i])-1   

            for i in range(horizon):
                avgFutureReturn[len(avgFutureReturn)-horizon+i]=numpy.mean(avgFutureReturn) 
            
            Y,countMinus,countStable,countPlus = self.ClassifyReturns(avgFutureReturn)
            
            class_le = LabelEncoder()
            Y = class_le.fit_transform(Y)
            scoreResults=[]     
            
            
            for k in range(len(inputs)-1):
                for c in itertools.combinations(inputs,k+1):
                    
                    inputName=[]
                    XList=[]
                    for index in c:
                        XList.append(data[index])
                        inputName.append(headers[index])
                    
                    X=numpy.asarray(XList)
                    X = X.T
                                   
                    imr = Imputer(missing_values='NaN',strategy='mean',axis=0)
                    imr.fit(X)
                    X = imr.transform(X)
                    
                    pipe_lr = self.FitModelWithStratifiedKFold(X,Y)
                    
                    scores= cross_val_score(estimator=pipe_lr,
                                    X=X,
                                    y=Y,
                                    cv=10,
                                    n_jobs=1)
                    
                    scoreResults.append([
                                         numpy.mean(scores),
                                         numpy.std(scores),
                                         countMinus,
                                         countStable,
                                         countPlus,
                                         inputName,
                                         horizon,
                                         list(class_le.inverse_transform(pipe_lr.classes_))
                                         ])             
                        
            maxx=0
            for k in range(len(scoreResults)):
                if scoreResults[k][1]>maxx:
                    maxx=scoreResults[k][1]
                    index = k            
            
            record.update({ 'BEST_SCORE_HORIZON_'+str(horizon)+'_DAYS': scoreResults[index]})
        
        self.db.Scores.delete_many({'BBGTicker':s})
        mongoRecord=[record]
        self.db.Scores.insert_many(mongoRecord)
        print(s)        