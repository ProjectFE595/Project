# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 15:59:16 2016

@author: Hugo
"""
import numpy
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split
from GetAnalyticsFromMongo import GetAnalyticsFromMongo

def GetReturnPredictions(s,date,horizon):
    
    dataMongo = GetAnalyticsFromMongo(s)
    headers = dataMongo[0]
    data = dataMongo[1:] #Remove headers
    filterIndex = data[headers.index('Date')].index(date)
    
    indexClose = headers.index('Close')
    indexKama=headers.index('KAMA')
    indexMACD=headers.index('MACD')
    indexCCI=headers.index('CCI')
    indexRSI=headers.index('RSI')
    indexWILLIAMR=headers.index('WILLIAMR')
    indexMFI=headers.index('MFI')
    indexEMA=headers.index('EMA')
    indexOBV=headers.index('OBV')
    indexROC=headers.index('ROC')
    indexSTOCHSLOWD=headers.index('STOCHSLOWD')
    indexADX=headers.index('ADX')
    
    Xpred = numpy.asarray([data[indexKama][filterIndex],
             data[indexMACD][filterIndex],
             data[indexCCI][filterIndex],
             data[indexRSI][filterIndex],
             data[indexWILLIAMR][filterIndex],
             data[indexMFI][filterIndex],
             data[indexEMA][filterIndex],
             data[indexOBV][filterIndex],
             data[indexROC][filterIndex],
             data[indexSTOCHSLOWD][filterIndex],
             data[indexADX][filterIndex]])
    Xpred = Xpred.T
    
#must be numpy here with n rows             
    X = numpy.asarray([data[indexKama][:filterIndex],
             data[indexMACD][:filterIndex],
             data[indexCCI][:filterIndex],
             data[indexRSI][:filterIndex],
             data[indexWILLIAMR][:filterIndex],
             data[indexMFI][:filterIndex],
             data[indexEMA][:filterIndex],
             data[indexOBV][:filterIndex],
             data[indexROC][:filterIndex],
             data[indexSTOCHSLOWD][:filterIndex],
             data[indexADX][:filterIndex]])
    X = X.T
    #changeto drop values                   
    imr = Imputer(missing_values='NaN',strategy='mean',axis=0)
    imr.fit(X)
    X = imr.transform(X)
    
    futureReturn = numpy.copy(data[indexClose][:filterIndex])
    for i in range(len(futureReturn)-horizon):
        temp=1
        for k in range(horizon):
            temp=temp*(futureReturn[k+i+1]/futureReturn[k+i]) #Compound returns
        
        futureReturn[i]=(temp-1) #yearly return

    for i in range(horizon):
        futureReturn[len(futureReturn)-horizon+i]=0
                
    returnClassification = numpy.empty([len(futureReturn)],dtype="S20")

    for i in range(futureReturn.size):               
        if futureReturn[i]<-0.5:
            returnClassification[i]='[,-0.5]'
        if -0.5<= futureReturn[i] < -0.45 :
            returnClassification[i]='[-0.5,-0.45]'
        if -0.45<= futureReturn[i] < -0.40 :
            returnClassification[i]='[-0.45,-0.40]'
        if -0.4<= futureReturn[i] < -0.35 :
            returnClassification[i]='[-0.40,-0.35]'
        if -0.35<= futureReturn[i] < -0.3 :
            returnClassification[i]='[-0.35,-0.30]'
        if -0.3<= futureReturn[i] < -0.25 :
            returnClassification[i]='[-0.30,-0.25]'
        if -0.25<= futureReturn[i] < -0.20 :
            returnClassification[i]='[-0.25,-0.20]'
        if -0.2<= futureReturn[i] < -0.15 :
            returnClassification[i]='[-0.20,-0.15]'
        if -0.15<= futureReturn[i] < -0.10 :
            returnClassification[i]='[-0.15,-0.10]'
        if -0.1<= futureReturn[i] < -0.05 :
            returnClassification[i]='[-0.10,-0.05]'
        if -0.05<= futureReturn[i] < 0 :
            returnClassification[i]='[-0.05,0]'
        if 0<= futureReturn[i] < 0.05 :
            returnClassification[i]='[0,0.05]'
        if 0.05<= futureReturn[i] < 0.1 :
            returnClassification[i]='[0.05,0.1]'
        if 0.1<= futureReturn[i] < 0.15 :
            returnClassification[i]='[0.1,0.15]'
        if 0.15<= futureReturn[i] < 0.2 :
            returnClassification[i]='[0.15,0.2]'
        if 0.2<= futureReturn[i] < 0.25 :
            returnClassification[i]='[0.2,0.25]'
        if 0.25<= futureReturn[i] < 0.3 :
            returnClassification[i]='[0.25,0.30]'
        if 0.3<= futureReturn[i] < 0.35 :
            returnClassification[i]='[0.30,0.35]'
        if 0.35<= futureReturn[i] < 0.4 :
            returnClassification[i]='[0.35,0.40]'
        if 0.4<= futureReturn[i] < 0.45 :
            returnClassification[i]='[0.40,0.45]'
        if 0.45<= futureReturn[i] < 0.5 :
            returnClassification[i]='[0.45,0.50]'
        if 0.5<= futureReturn[i] :
            returnClassification[i]='[0.5,]'                
    
    Y = returnClassification
    
    class_le = LabelEncoder()
    Y = class_le.fit_transform(Y)
    
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.2, random_state=1)    
    pipe_lr = Pipeline([
                ('scl', StandardScaler()),
                ('pca', PCA(n_components=5)),
                ('clf', LogisticRegression(penalty='l1',C=0.1,random_state=1))    
                ])
                
    pipe_lr.fit(Xtrain,Ytrain)
    Ypred = pipe_lr.predict(Xpred)
    proba = pipe_lr.predict_proba(Xpred)
    print(s)
    print(Ypred)
    print(proba)
    proba = proba[0][Ypred[0]]
    interval = class_le.inverse_transform(Ypred)[0].decode()
    lowReturn = float(interval[1+interval.index('['):interval.index(',')])
    highReturn = float(interval[1+interval.index(','):interval.index(']')])
    returnPredict = (lowReturn+highReturn)/2
    
    #ADD hyperparameter TUNING for parameter C of Logistic regression
    scores= cross_val_score(estimator=pipe_lr,
                            X=Xtrain,
                            y=Ytrain,
                            cv=10,
                            n_jobs=1)

    return returnPredict,proba,numpy.mean(scores),numpy.std(scores)