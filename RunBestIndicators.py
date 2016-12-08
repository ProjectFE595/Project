# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 21:48:21 2016

@author: Hugo
"""


#C:\Users\Hugo\AppData\Local\Programs\Python\Python35-32\
#C:\Users\Hugo\AppData\Local\Programs\Python\Python35-32\Scripts\
#import os
#import sys
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
import multiprocessing
from BestPredictor import BestPredictor

if __name__ == '__main__':
    
    TIs=['KAMA','MACDHIST','CCI','RSI','WILLIAMR','MFI','EMA','ROC','STOCHSLOWD','ADX']
    hostc='localhost'
    #hostc='155.246.104.19'
    portn = 27017
    
    client = MongoClient(host=hostc, port=portn)
    db = client.Project     
    stocks = ['VOD','AAPL']  
    epr = BestPredictor(TIs)
    
    jobs = []
    for s in stocks:
        p = multiprocessing.Process(target=epr.GetExhaustivePredictorsKNN, args=(s,))
        jobs.append(p)
        p.start()
        
    for j in jobs:
        j.join()

    stocks = ['ORLY','JNJ']  
    
    jobs = []
    for s in stocks:
        p = multiprocessing.Process(target=epr.GetExhaustivePredictorsKNN, args=(s,))
        jobs.append(p)
        p.start()
        
    for j in jobs:
        j.join()