from django.shortcuts import render
# To call the view, we need to map it to a URL - and for this we need a URLconf.
# Create your views here.
from django.http import HttpResponse

def home(request):
    #context = {'latest_question_list': latest_question_list}
    return render(request, 'interface/index.html', {})

