# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 15:59:16 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""
import numpy
from pymongo import MongoClient
import itertools
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split
from MongoDataGetter import MongoDataGetter
import warnings
warnings.filterwarnings('ignore')


"""
Stratified K folds
Other scores F1, confusion matrix etc
Use output it in Predictor class
"""

def GetBestPredictors(stock,horizon):

    client = MongoClient()
    db = client.Project
    pred = list(db.Scores.find({'BBGTicker':stock}))
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
    
    return pred[0][bestScore][TIsIndex-1]
                
    
def GetExhaustivePredictors(s,TIs):
    
    client = MongoClient()
    db = client.Project
    
    mg = MongoDataGetter(sDate='2002-01-04',eDate='')
    dataMongo = mg.GetDataFromMongo(s,'TIs')  
    
    headers = dataMongo[0]
       
    data = dataMongo[1:] #Remove headers
    
    #Select TIs corresponding index
    TIsIndex=[]    
    for i in range(len(TIs)):
        TIsIndex.append(headers.index(TIs[i]))
            
    indexClose=headers.index('Close')

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
        
        prices = numpy.copy(data[indexClose])
        print(len(prices))
        avgFutureReturn = numpy.empty(len(prices))
        for i in range(len(prices)-horizon):               
            temp=0                
            for k in range(horizon):
                temp+= prices[k+i] #Average price for the trend        
            avgFutureReturn[i]= temp/(horizon*prices[i])-1   

        for i in range(horizon):
            avgFutureReturn[len(avgFutureReturn)-horizon+i]=numpy.mean(avgFutureReturn)            
                
        returnClassification = numpy.empty([len(avgFutureReturn)],dtype="S100")
        
        halfSigma = 0.5*numpy.std(avgFutureReturn)
        halfSigmaStr=str(halfSigma)
        halfSigmaStrMin=str(-halfSigma)        
        
        print(halfSigma)
        
        countMinus=0
        countStable=0
        countPlus=0
        for i in range(avgFutureReturn.size):               
            if  avgFutureReturn[i] < -halfSigma :
                countMinus=countMinus+1
                returnClassification[i]='[-0.3;'+halfSigmaStrMin+']'
            if -halfSigma <= avgFutureReturn[i] < halfSigma :
                countStable=countStable+1
                returnClassification[i]='['+halfSigmaStrMin+'];'+halfSigmaStr+']'            
            if halfSigma <= avgFutureReturn[i] :
                countPlus=countPlus+1
                returnClassification[i]='['+halfSigmaStr+';0.3]'
                       
        Y = returnClassification
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
        
                """
                for train_index, test_index in kf:
                    Xtrain, Xtest = X[train_index], X[test_index]
                    Ytrain, Ytest = Y[train_index], Y[test_index]
                """
                
                Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.2, random_state=1)   
                
                pipe_lr = Pipeline([
                            ('scl', StandardScaler()),
                            ('clf', LogisticRegression(penalty='l1',C=0.1,random_state=1))    
                                    ])
                    
                pipe_lr.fit(Xtrain,Ytrain)

                
                scores= cross_val_score(estimator=pipe_lr,
                                X=Xtrain,
                                y=Ytrain,
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
    
    db.Scores.delete_many({'BBGTicker':s})
    mongoRecord=[record]
    db.Scores.insert_many(mongoRecord)
    print(s)
                