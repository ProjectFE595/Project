from django.shortcuts import render
# To call the view, we need to map it to a URL - and for this we need a URLconf.
# Create your views here.
from django.http import HttpResponse
from pymongo import MongoClient
from django import forms
import json
from django.utils.safestring import mark_safe

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

def home(request):
    # --Connect to MongoDB to get all stock tickers
    client = MongoClient()
    db = client.Project
    stocks = [x['BBGTicker'] for x in list(db.Stocks.find({}, {"_id": 0, "BBGTicker": 1}).sort("BBGTicker",1))]
    # stocks = [x for x in list(db.Stocks.find({}, {"_id": 0, "BBGTicker": 1}))]
    # stocks = json.dumps(stocks)
    excludedStocks = ['GOOG', 'AVGO', 'BRCM', 'CHTR', 'CMCSK', 'DISCK', 'FB', 'GMCR', 'KHC', 'LMCA', 'LVNTA', 'SNDK',
                      'TSLA', 'TRIP', 'VRSK', 'WBA',
                      'SBUX', 'TXN', 'ORLY', 'MU', 'REGN', 'STX', 'VIP', 'MYL']   # exclude more stocks since they result GetBestPredictors error

    stocks = [n for n in stocks if n not in excludedStocks]

    # --Convert stocks list into a string. Then the html will parse the string into json object.
    stocks = '\", \"'.join(stocks)
    stocks = '[\"'+stocks+'\"]'


    context = {
        'stocks': mark_safe(stocks),
    }
    return render(request, 'interface/home.html', context)

