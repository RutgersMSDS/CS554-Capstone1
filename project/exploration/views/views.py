from django.shortcuts import render
import json
from django.http import JsonResponse
from django.template import RequestContext

from exploration import load_fact_table_helper_SQL as ftable
from exploration import helperPlot as hp
import pandas as pd

# response = ftable.gather_all_data()

# Create your views here.
def render_Home(request):
    return render(request,'exploration/Home.html')

def get_GSEview(request):
    return render(request, 'exploration/UI.html')

def render_Data(request):
    # dataresponse = ftable.getdata()
    # json_string = json.dumps(response)
    return render(request, 'exploration/Data.html')

def render_exploration(request):
    json_string = json.dumps(response)
    return render(request, 'exploration/Exploration.html', {"res" : json_string})

def get_plot_data(request):
    a = request.body
    incoming_data = json.loads(a.decode('utf-8'))
    
    if(incoming_data["analysis"] == "univariate"):
        tableName = incoming_data["tableName"]
        attrType = incoming_data["columns"][0]["columnType"]
        columnName = incoming_data["columns"][0]["columnName"]
        
        res = hp.get_univariate_data(attrType, columnName, tableName)
        return JsonResponse(res)

    else:
        tableName = incoming_data["tableName"]
        attrType_x = incoming_data["columns"][0]["columnType"]
        columnName_x = incoming_data["columns"][0]["columnName"]
        attrType_y = incoming_data["columns"][1]["columnType"]
        columnName_y = incoming_data["columns"][1]["columnName"]
        
        res = hp.get_bivariate_data(attrType_x,attrType_y, columnName_x,columnName_y, tableName)
        return JsonResponse(res)
    
    return JsonResponse("")

def GetGSEData(request):
    dataresponse = ftable.getdata()
    return JsonResponse(dataresponse, safe=False)

def DeleteGSE(request):
    gsevalue= request.GET.get('GSE',1)
    # gsevalue=json.load(request)['GSE']
    dbresponse=ftable.DeleteGSE(gsevalue)
    return render('data', 'exploration/Data.html')

def SaveGSEData(request):
    dict={}
    dict['GSE'] = request.GET.get('data[GSE]')
    dict['Year'] = request.GET.get('data[Year]');
    dict['Samples'] = request.GET.get('data[Samples]');
    dict['Subject'] = request.GET.get('data[Subject]');
    dict['Platform'] = request.GET.get('data[Platform]');
    dict['URL'] = request.GET.get('data[URL]');
    dict['Title'] = request.GET.get('data[Title]');
    dict['Public'] = request.GET.get('data[Public]');
    dict['Private'] = request.GET.get('data[Private]');
    dict['Source'] = request.GET.get('data[Source]');
    dict['Organ'] = request.GET.get('data[Organ]');
    dict['Assay'] = request.GET.get('data[Assay]');

    dbresp= ftable.SaveGSEData(dict)
    return JsonResponse("success", safe=False)

def GetDatafromDB(request):
    GSEValue= request.GET.get('GSE', None);
    Table = request.GET.get('table',None);
    datarows,columns = ftable.GetTargets(GSEValue, Table);
    if Table == 'Expression':
        columns.insert(0,'RandomBin')
        columns.insert(0,'Random')
        columns.insert(0,'Target')
        columns.insert(0,'geo_accession')
        df = pd.DataFrame(datarows)

    if Table == 'Targets':
        selectquery = 'Select * from ' + GSEValue + '_targets';
    elif Table == 'Probes':
        selectquery = 'Select * from ' + GSEValue + '_probes';
    else:
        maxcolumns= 54
        selectquery = 'Select '
        for i in range(maxcolumns):
            selectquery = selectquery + str(columns[i])
        df = df.iloc[:, : maxcolumns]
        datarows=df.values.tolist()
        selectquery = selectquery + ' from slice_001_fact';

    response = list()
    response.append(datarows)
    response.append(columns)
    response.append(selectquery)
    return JsonResponse(response,safe=False)