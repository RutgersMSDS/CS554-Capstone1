from django.shortcuts import render
import json
from django.http import JsonResponse
from django.template import RequestContext

from . import load_fact_table_helper_SQL as ftable
from . import helperPlot as hp
from . import binningHelper as bh

response = ftable.gather_all_data()

# Create your views here.
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
        
        if(incoming_data["columns"][0]["isBinningRequired"]):
            binSize = int(incoming_data["columns"][0]["binningSize"])
            res = bh.get_univariate_binned_data(attrType, columnName, tableName, binSize)
        else:
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
