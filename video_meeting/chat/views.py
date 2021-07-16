from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
import pandas as pd
import os
import json
from .uploadhandler import *

def load_results(file, n):
    data = pd.read_csv(file)
    subData = data.tail(n)
    return subData['engagement'].mean(), subData['confusion'].mean(), subData['boredom'].mean(), subData['frustration'].mean(),subData['comprehension'].mean()

def main_view(request):
    return render(request, 'chat/index.html', context={})

def create_csv(request):
    filename = request.GET.get('username')
    states = {
        "engagement":[],
        "confusion":[],
        "boredom":[],
        "frustration":[],
        "comprehension":[]
    }
    df = pd.DataFrame(states)
    df.to_csv('tmp/'+filename+'.csv', index = False)
    return HttpResponse('created successfully', status=200)

def model_view(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES)
    return HttpResponse('uploaded successfully', status=200)

def states_view(request):
    results = []
    for file in os.listdir('tmp'):
        filepath = 'tmp/'+file
        states = load_results(filepath, 25)
        results.append({
            'username': file[:-4],
            'engagement':states[0],
            'confusion':states[1],
            'boredom':states[2],
            'frustration':states[3],
            'comprehension':states[4]
        })
    return HttpResponse(json.dumps(results), status=200)
    
