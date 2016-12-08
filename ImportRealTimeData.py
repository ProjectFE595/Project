# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 13:40:15 2016

@author: Hugo
"""
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
from pymongo import MongoClient

def ImportRealTimeData():

    client = MongoClient()
    db = client.Project 
    stocks = [x['BBGTicker'] for x in list(db.Stocks.find({}))]
    stocks.remove('BRCM')
    stocks.remove('CMCSK')
    stocks.remove('GMCR')
    stocks.remove('SNDK')
    
    k=0
    rTime=datetime.now()    
    
    print(rTime)

    while (rTime.hour >= 9 and rTime.hour <= 16):
        k=k+1
        print(rTime)
        for s in stocks:
            try:
                headers = ["Quote","BestBid","BestAsk","CurrentLow","CurrentHigh","Volume","ShareOutstanding"
                    ,"AvgVolume50Days", "PreviousClose","PE","EPS", "CurrentYield"]
                realTimeData=[]
                page = urlopen("http://www.nasdaq.com/symbol/"+s)        
                o = BeautifulSoup(page)
                ex = o.find("div",{"class" : "notTradingIPO"})
                if ex == None:
                    rTime = datetime.now()
                    realTime = str(rTime).replace(".",":")
                
                    quote = o.find("div",{"id" : "qwidget_lastsale"}).contents[0].replace("$","")
                    bidask = o.find("a",{"id" : "best_bid_ask"}).findNext("td").contents[0]
                    bidask = bidask.replace("$","").replace("\xa0","")
                    bestBid = bidask[:bidask.index("/")]
                    bestAsk = bidask[bidask.index("/")+1:]
                
                    highlow = o.find("a",{"id" : "todays_high_low"}).findNext("td")
                    temphigh = highlow.findNext("label").contents[0].replace("$","").replace("\xa0","")
                    templow = highlow.findNext("label").findNext("label").contents[0].replace("$","").replace("\xa0","")
                    
                    low = min(templow,temphigh)
                    high = max(templow,temphigh)
                    
                    sharesVol = o.find("a",{"id" : "share_volume"}).findNext("label").contents[0].replace(",","")    
                    avgVol50Days = o.find("a",{"id" : "50_day_avg"}).findNext("td").contents[0].replace(",","")
                    previousClose = o.find("a",{"id" : "previous_close"}).findNext("td").contents[0].replace("$","").replace(" ","").replace("\xa0","")                
                    sharesOut = o.find("a",{"id" : "share_outstanding"}).findNext("td").contents[0].replace("$","").replace(" ","").replace(",","")
                                        
                    y = o.find("a",{"id" : "current_yield"}).findNext("td").contents[0].replace("%","").replace("\xa0","").replace(" ","")
                    
                    realTimeData.append(quote)
                    realTimeData.append(bestBid)
                    realTimeData.append(bestAsk)
                    realTimeData.append(low)
                    realTimeData.append(high)
                    realTimeData.append(sharesVol)
                    realTimeData.append(sharesOut)
                    realTimeData.append(avgVol50Days)
                    realTimeData.append(previousClose)
    
                    pe = o.find("a",{"id" : "pe_ratio"})
                    if pe!= None:
                        pe = pe.findNext("td").contents[0].replace("$","").replace("\xa0","")
                        realTimeData.append(pe)
                    else:
                        headers.remove("PE")
                    
                    eps = o.find("a",{"id" : "eps"})
                    if eps!= None:
                        eps = eps.findNext("td").contents[0].replace("$","").replace("\xa0","")
                        realTimeData.append(eps)
                    else:
                        headers.remove("EPS")
    
                    realTimeData.append(y)    
                            
                    db.RealTime.update_one({"STOCK":s}
                    ,{'$set' : {realTime : realTimeData, "HEADERS" : headers} }
                    ,upsert=True)
                else:
                    print(s + " not found ")
            
            except AttributeError:
                print('Error for ' + s)
                continue
