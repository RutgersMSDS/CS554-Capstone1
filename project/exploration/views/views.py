from django.shortcuts import render
import json
from django.http import JsonResponse
from django.template import RequestContext

from exploration import load_fact_table_helper_SQL as ftable
from exploration import helperPlot as hp
import pandas as pd
#Modelling imports
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve
import xgboost
from sklearn.metrics import mean_absolute_error,\
 mean_squared_log_error,\
mean_squared_error
import math

# response = ftable.gather_all_data()
# Modelling Code
train_set = pd.DataFrame()
test_set = pd.DataFrame()

train_path =''

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
    # json_string = json.dumps(response)
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
    type = request.GET.get('type', 1)
    dataresponse = ftable.getdata(type)
    return JsonResponse(dataresponse, safe=False)

def DeleteGSE(request):
    gsevalue= request.GET.get('GSE',1)
    # gsevalue=json.load(request)['GSE']
    dbresponse=ftable.DeleteGSE(gsevalue)
    return JsonResponse('success', safe=False)

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

# MODELLING

# def render_modelling(request):
#     if request.method != 'POST':
#         columns=[]
#         values=[]
#         return render(request, 'exploration/Modelling.html')
#     else:
#         train_path = request.FILES['fileupload']
#         test_path = request.FILES['fileupload1']
#         trainfile = train_path.read().splitlines()
#         testfile = test_path.read().splitlines()
#         trainlist = [str(i).split(',') for i in trainfile]
#         testlist = [str(i).split(',') for i in testfile]
#         train_set = pd.DataFrame(data=trainlist[1:len(trainlist)], columns=trainlist[0])
#         test_set = pd.DataFrame(data=testlist[1:len(testlist)], columns=testlist[0])
#         columns = list(train_set.columns)
#         values=[]
#         for col in columns:
#             values.append(train_set[col].unique().astype(str))
#
#         return render(request, 'exploration/Modelling.html', {'columns' : columns, 'values' : values})

def render_modelling(request):
    global train_set
    global test_set
    global train_path

    if request.method != 'POST':
        columns=[]
        values=[]
        return render(request, 'exploration/Modelling.html')
    else:
        train_path = request.FILES['fileupload']
        test_path = request.FILES['fileupload1']


        trainfile = train_path.read()
        trainfile = trainfile.decode("utf-8")
        trainfile = trainfile.splitlines()

        testfile = test_path.read()
        testfile = testfile.decode('utf8')
        testfile = testfile.splitlines()

        trainlist = [str(i).split(',') for i in trainfile]
        testlist = [str(i).split(',') for i in testfile]

        train_set = pd.DataFrame(data=trainlist[1:len(trainlist)], columns=trainlist[0])
        test_set = pd.DataFrame(data=testlist[1:len(testlist)], columns=testlist[0])
        columns = list(train_set.columns)
        values=[]
        for col in columns:
            values.append(train_set[col].unique().astype(str))

        return render(request, 'exploration/Modelling.html', {'columns' : columns, 'values' : values, 'train_path': train_path, 'test_path':test_path})

def dynamic_dropdown(request):
    colname = request.GET.get('col',None);
    values = list(train_set[colname].unique().astype(str))
    return JsonResponse(values, safe=False)

def get_model_params(request):

    label = request.GET.get('y', None);
    omit_params = request.GET.getlist('x[]',None)

    y_train = pd.to_numeric(train_set[label])
    train_set.drop(omit_params, axis=1, inplace = True)
    for col in train_set.columns:
        train_set[col] = pd.to_numeric(train_set[col])
    X_train = train_set

    y_test = pd.to_numeric(test_set[label])
    test_set.drop(omit_params, axis=1, inplace = True)
    for col in test_set.columns:
        test_set[col] = pd.to_numeric(test_set[col])
    X_test = test_set

    model = XGBClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    #for charts
    class_pred_probs = model.predict_proba(X_test)
    res = pd.DataFrame()
    res['actual']=y_test
    res['predict']=y_pred

    collen = len(class_pred_probs[0])
    colnames = []
    for i in range(collen):
        colnames.append('target_factor_' + str(i))

    pred_probs_df = pd.DataFrame(class_pred_probs , columns =colnames)
    list_1 = res['actual'].values.tolist()
    list_2 = res['predict'].values.tolist()

    pred_probs_df['target'] = list_1
    pred_probs_df['p_target'] = list_2

    pred_probs_df.to_csv('Class_XGB_SCORES.csv')

    return JsonResponse(acc, safe=False)


def reg_model_params(request):
    label = request.GET.get('y', None);
    omit_params = request.GET.getlist('x[]', None)

    y_train = pd.to_numeric(train_set[label])
    train_set.drop(omit_params, axis=1, inplace=True)
    for col in train_set.columns:
        train_set[col] = pd.to_numeric(train_set[col])
    X_train = train_set

    y_test = pd.to_numeric(test_set[label])
    test_set.drop(omit_params, axis=1, inplace=True)
    for col in test_set.columns:
        test_set[col] = pd.to_numeric(test_set[col])
    X_test = test_set

    model = xgboost.XGBRegressor()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    results =[]
    results.append(mean_absolute_error(y_test, y_pred))
    results.append(math.sqrt(mean_squared_error(y_test, y_pred)))
    results.append(math.sqrt(mean_squared_log_error(y_test, y_pred)))

     # saving results to local
    Reg_eval_scores = {}
    Reg_eval_scores['MAE'] = results[0]
    Reg_eval_scores['MSE'] = results[1]
    Reg_eval_scores['MSLE'] = results[2]

    (pd.DataFrame.from_dict(data=Reg_eval_scores, orient='index')
     .to_csv('REG_output.csv', header=False))

    #  # for charts
    # reg_pred_probs = model.predict_proba(X_test)
    # res = pd.DataFrame()
    # res['actual'] = y_test
    # res['predict'] = y_pred
    #
    # collen = len(reg_pred_probs[0])
    # colnames = []
    # for i in range(collen):
    #     colnames.append('target_factor_' + str(i))
    #
    # pred_probs_df = pd.DataFrame(reg_pred_probs, columns=colnames)
    # list_1 = res['actual'].values.tolist()
    # list_2 = res['predict'].values.tolist()
    #
    # pred_probs_df['target'] = list_1
    # pred_probs_df['p_target'] = list_2
    #
    # pred_probs_df.to_csv('REG_XGB_SCORES.csv')

    return JsonResponse(results, safe=False)
