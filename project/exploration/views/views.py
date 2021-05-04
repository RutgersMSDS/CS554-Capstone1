from django.shortcuts import render
from django.template import loader
import json
from django.http import JsonResponse
from django.template import RequestContext

from exploration import load_fact_table_helper_SQL as ftable
from exploration import helperPlot as hp
from exploration import binningHelper as bh
#Modeling imports
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve

import xgboost
from sklearn.metrics import mean_absolute_error, mean_squared_log_error, mean_squared_error, classification_report, \
    matthews_corrcoef

import math
from exploration import FileUtils

# Evaluation libraries
from exploration import evaluationHelper
from django.views.decorators.csrf import csrf_exempt

# response = ftable.gather_all_data()
# modeling Code
train_set = pd.DataFrame()
test_set = pd.DataFrame()

train_path = ''


# Create your views here.
def render_Home(request):
    # clear output folder and start
    FileUtils.clearOutputFolder()
    return render(request, 'exploration/Home.html')


def get_GSEview(request):
    return render(request, 'exploration/UI.html')


def render_Data(request):
    # dataresponse = ftable.getdata()
    # json_string = json.dumps(response)
    return render(request, 'exploration/Data.html')


def render_exploration(request):
    databaseName = request.GET.get('gse_value')

    response = ftable.gather_all_data(databaseName)
    response["databaseName"] = databaseName
    json_string = json.dumps(response)

    return render(request, 'exploration/Exploration.html', {"res" : json_string})


def get_plot_data(request):
    a = request.body
    incoming_data = json.loads(a.decode('utf-8'))
    databaseName = incoming_data["databaseName"]
    if(incoming_data["analysis"] == "univariate"):

        tableName = incoming_data["tableName"]
        attrType = incoming_data["columns"][0]["columnType"]
        columnName = incoming_data["columns"][0]["columnName"]
        chartType = incoming_data["chartType"]

        if(incoming_data["columns"][0]["isBinningRequired"]):
            binSize = int(incoming_data["columns"][0]["binningSize"])
            res = bh.get_univariate_binned_data(attrType, columnName, tableName, databaseName, binSize)
        else:
            res = hp.get_univariate_data(attrType, columnName, tableName, databaseName, chartType)

        #" + databaseName + "
        #databaseName
        return JsonResponse(res)

    else:
        tableName = incoming_data["tableName"]
        attrType_x = incoming_data["columns"][0]["columnType"]
        columnName_x = incoming_data["columns"][0]["columnName"]
        attrType_y = incoming_data["columns"][1]["columnType"]
        columnName_y = incoming_data["columns"][1]["columnName"]

        if(incoming_data["columns"][0]["isBinningRequired"] or incoming_data["columns"][1]["isBinningRequired"] ):
            res = bh.get_bivariate_binned_data(incoming_data["columns"],incoming_data["tableName"],databaseName)
        else:
            res = hp.get_bivariate_data(attrType_x, attrType_y, columnName_x,columnName_y,databaseName, tableName)
        return JsonResponse(res)

    return JsonResponse("")


def GetGSEData(request):
    type = request.GET.get('type', 1)
    dataresponse = ftable.getdata(type)
    return JsonResponse(dataresponse, safe=False)


def DeleteGSE(request):
    gsevalue = request.GET.get('GSE', 1)
    # gsevalue=json.load(request)['GSE']
    dbresponse = ftable.DeleteGSE(gsevalue)
    return JsonResponse('success', safe=False)


def SaveGSEData(request):
    dict = {}
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

    dbresp = ftable.SaveGSEData(dict)
    return JsonResponse("success", safe=False)


def GetDatafromDB(request):
    GSEValue = request.GET.get('GSE', None);
    Table = request.GET.get('table', None);
    datarows, columns = ftable.GetTargets(GSEValue, Table);
    if Table == 'Expression':
        columns.insert(0, 'RandomBin')
        columns.insert(0, 'Random')
        columns.insert(0, 'Target')
        columns.insert(0, 'geo_accession')
        df = pd.DataFrame(datarows)

    if Table == 'Targets':
        selectquery = 'Select * from ' + GSEValue + '_targets';
    elif Table == 'Probes':
        selectquery = 'Select * from ' + GSEValue + '_probes';
    else:
        maxcolumns = 54
        selectquery = 'Select '
        for i in range(maxcolumns):
            selectquery = selectquery + str(columns[i])
        df = df.iloc[:, : maxcolumns]
        datarows = df.values.tolist()
        selectquery = selectquery + ' from slice_001_fact';

    response = list()
    response.append(datarows)
    response.append(columns)
    response.append(selectquery)
    return JsonResponse(response, safe=False)


# modeling

# def render_modeling(request):
#     if request.method != 'POST':
#         columns=[]
#         values=[]
#         return render(request, 'exploration/modeling.html')
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
#         return render(request, 'exploration/modeling.html', {'columns' : columns, 'values' : values})

def render_modeling(request):
    global train_set
    global test_set
    global train_path

    if request.method != 'POST':
        columns = []
        values = []
        return render(request, 'exploration/modeling.html')
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
        values = []
        for col in columns:
            values.append(train_set[col].unique().astype(str))

        return render(request, 'exploration/modeling.html',
                      {'columns': columns, 'values': values, 'train_path': train_path, 'test_path': test_path})


def dynamic_dropdown(request):
    colname = request.GET.get('col', None);
    values = list(train_set[colname].unique().astype(str))
    return JsonResponse(values, safe=False)


def get_model_params(request):
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

    model = XGBClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    matthews_c = matthews_corrcoef(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    # generate confusion matrix data
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    conf_m = pd.DataFrame(columns=[" ", "1", "0", "Predicted"])
    conf_m.loc[0] = ["1", tp, fn, tp + fn]
    conf_m.loc[1] = ["0", fp, tn, fp + tn]
    conf_m.loc[2] = ["Actual", tp + fp, fn + tn, tp + fp + fn + tn]
    conf_m.to_csv(FileUtils.getXGBClassificationConfusionMatrix(), index=False)

    # generate data for stats table
    result = evaluationHelper.getClassificationEvaluationMetrics(report, matthews_c)
    result.to_csv(FileUtils.getXGBClassificationOutputFileName(), index=False)

    # generate data for deci chart bins
    class_pred_probs = model.predict_proba(X_test)
    bins_data = evaluationHelper.getClassificationBinMetrics(class_pred_probs, label, y_test, y_pred)
    if (bins_data is not None):
        bins_data.to_csv(FileUtils.getXGBClassificationBinScoreFileName(), index=False)

    # save y_pred and y_test for other classification charts
    scores = pd.DataFrame()
    scores[label] = y_test
    scores["p_" + label] = y_pred
    scores.to_csv(FileUtils.getXGBClassificationScoreFileName())

    return JsonResponse(report['accuracy'], safe=False)


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

    results = []
    results.append(mean_absolute_error(y_test, y_pred))
    results.append(math.sqrt(mean_squared_error(y_test, y_pred)))
    results.append(math.sqrt(mean_squared_log_error(y_test, y_pred)))

    # generate results to local
    reg_eval_scores = evaluationHelper.getRegressionEvaluationMetrics(results)
    reg_eval_scores.to_csv(FileUtils.getXGBRegressionOutputFileName(), header=False)

    # generate histogram results
    reg_hist_scores = evaluationHelper.getRegressionHistogramMetrics(y_test, y_pred)
    reg_hist_scores.to_csv(FileUtils.getXGBRegressionHistogramFileName(), header=False)

    return JsonResponse(results, safe=False)


#################
# Evaluation
#################

@csrf_exempt
def render_evaluation(request):
    mode = request.GET.get("mode")
    result = {}
    result["Evaluation"] = loader.render_to_string('exploration/Evaluation.html', request=request)

    if (mode == "classification"):

        print("Evaluating classification model...")
        # generate confusion matrix Html
        conf_matrix_data = pd.read_csv(FileUtils.getXGBClassificationConfusionMatrix())
        result["ConfusionMatrix"] = conf_matrix_data.style.set_table_styles(
            [{'selector': '.row_heading',
              'props': [('display', 'none')]},
             {'selector': '.blank.level0',
              'props': [('display', 'none')]}]).render()

        # generate stats table
        stats = pd.read_csv(FileUtils.getXGBClassificationOutputFileName())
        result["StatisticsTable"] = stats.style.set_table_styles(
            [{'selector': '.row_heading',
              'props': [('display', 'none')]},
             {'selector': '.blank.level0',
              'props': [('display', 'none')]}]).render()

        # generate decile chart
        if (int(stats.loc[0]["Value"]) > 10):
            deciles = pd.read_csv(FileUtils.getXGBClassificationBinScoreFileName())
            result["DecileTable"] = deciles.style.set_table_styles(
                [{'selector': '.row_heading',
                  'props': [('display', 'none')]},
                 {'selector': '.blank.level0',
                  'props': [('display', 'none')]}]).render()

        # generate Gain chart

        # generate Lift chart

        # generate K-S chart

        # generate ROC chart

        # save all images

    else:
        print("Evaluation regression model...")

        # read classification output file

        # generate the histogram

        # save image

    print("Evaluation complete.\nSending Response to frontend...")

    # return the array of images to frontend
    return JsonResponse(result, safe=False)
