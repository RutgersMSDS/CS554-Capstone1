from django.shortcuts import render
import json
from django.http import JsonResponse

# Data libraries
import math
import numpy as np
import pandas as pd

# Visualization libraries
import matplotlib as plt
import scikitplot as skplt

def getClassificationEvaluationMetrics(report, matthews_c):
    result = pd.DataFrame(columns=["Statisics", "Value", "Same As"])

    result.loc[0] = ["Count",
                     str(report['weighted avg']['support']),
                     ""]
    result.loc[1] = ["Accuracy",
                     str(round(report['accuracy'], 2)) + "%",
                     ""]

    result.loc[2] = ["Sensitivity",
                     str(round(report['1']['recall'], 2)) + "%",
                     "True Positive Rate, Power, Recall"]
    result.loc[3] = ["Specificity",
                     str(round(report['0']['recall'], 2)) + "%",
                     "True Negative Rate"]

    result.loc[4] = ["Positive Predictive Value",
                     str(round(report['1']['precision'], 2)) + "%",
                     "Precision"]
    result.loc[5] = ["Negative Predictive Value",
                     str(round(report['0']['precision'], 2)) + "%",
                     ""]

    result.loc[6] = ["False Positive Rate",
                     str(round(1 - float(result.loc[3]['Value'].split("%")[0]), 2)) + "%",
                     "Fall Out, 1 - Specificity"]
    result.loc[7] = ["False Negative Rate",
                     str(round(1 - float(result.loc[2]['Value'].split("%")[0]), 2)) + "%",
                     ""]

    result.loc[8] = ["False Discovery Rate",
                     str(round(1 - float(result.loc[4]['Value'].split("%")[0]), 2)) + "%",
                     "1 - PPV"]
    result.loc[9] = ["Matthew's Correlation Coef.",
                     str(round(matthews_c, 2)),
                     ""]

    result.loc[10] = ["Informedness",
                      str(round(
                          float(result.loc[2]["Value"].split("%")[0])
                          +
                          float(result.loc[3]["Value"].split("%")[0])
                          - 1,
                          2)),
                      "Sensitivity + Specificity - 1"]
    result.loc[11] = ["F score",
                      str(round(report['1']['f1-score'], 2)),
                      "TP / (2TP + FP + FN)"]

    return result

def getClassificationBinMetrics(prediction_probs, label, y_test, y_pred):
    collen = len(prediction_probs[0])

    last_column_name = label + str(collen - 1)
    colnames = []

    for i in range(collen):
        colnames.append(label + str(i))

    pred_probs_df = pd.DataFrame(prediction_probs, columns=colnames)
    list_1 = y_test.values.tolist()
    list_2 = y_pred.tolist()

    pred_probs_df['target'] = list_1
    pred_probs_df['p_target'] = list_2

    # sort by p score
    pred_probs_df = pred_probs_df.sort_values(by=last_column_name, ascending=True).reset_index(drop=True)

    # paritition the p_target into 10 bins
    n = y_pred.shape[0]
    if(n > 10):
        bin_size = n // 10

        # Compute average score, target count and target percentage
        average_score = (round(pred_probs_df[last_column_name].groupby(pred_probs_df.index // bin_size).mean(), 5))
        target_count = (round(pred_probs_df['p_target'].groupby(pred_probs_df.index // bin_size).sum(), 2))
        total_predicted = pred_probs_df['p_target'].sum()
        target_percentage = str(round((target_count * 100) / total_predicted, 1)) + "%"

        bins_data = pd.DataFrame()
        bins_data["Bucket"] = range(1, 11)
        bins_data["Average Score"] = average_score
        bins_data["Target Count"] = target_count
        bins_data["Target Percentage"] = target_percentage

        return bins_data
    else:
        return None

def getRegressionEvaluationMetrics(stats):
    result = pd.DataFrame(columns=["Mean Absolute Error", "Mean Squared Error", "Mean Squared Log Error"])

    result.loc[0] = stats
    return result

def getRegressionHistogramMetrics(y_test, y_pred):
    err_histogram = pd.DataFrame()

    err_histogram['actual'] = y_test
    err_histogram['predict'] = y_pred

    err_histogram['Error(actual-predicted)'] = abs(err_histogram['actual'] - err_histogram['predict'])

    min_v = err_histogram['Error(actual-predicted)'].min()
    max_v = err_histogram['Error(actual-predicted)'].max()

    denominator = max_v - min_v

    err_histogram['Error(actual-predicted)'] = (err_histogram['Error(actual-predicted)'] - min_v) / denominator
    err_histogram = err_histogram.sort_values(by=['Error(actual-predicted)'], ascending=True).reset_index(drop=True)

    #err_histogram = err_histogram['Error(actual-predicted)'].apply(np.ceil)

    return err_histogram







