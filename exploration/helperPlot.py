"""
TO DISCUSS:
    * Exception handling. (inlcuding custom) : Locally handling exceptions. 1) No data in DB, 2) Chart cannot be plotted. (data type conflict), 3) Stats analysis.
    * Query for stats of data. (Also not in sync with Actual query & app's query) : Need not to be the correct SQL.
    * How to calculate percentage in each column chart? (data coming from backend???) (No need to focus rn)
"""

import statistics
import numpy as np
import scipy.stats
from scipy.stats import chi2_contingency
from scipy.stats import chi2

from Bioada import DBHelper as db_con
cursor = db_con.DBConnection.Instance().cursor

"""
Get data for univariate analysis.

Accepts:
    attrType = ["categorical" or "numerical"]
    tableName = tableName
    columnName = selected column name
Returns:
    Statistics of the given column of given table.
"""
def get_univariate_data(attrType, columnName, tableName):
    dataSQL = ""
    data = {}
    
    if(attrType == "numerical"):
        dataSQL += "SELECT [" + columnName + "] from GSE13355.dbo." + tableName 
        
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        results = [x[0] for x in results]
        
        details = {}
        
        details["Count"] = len(results)
        details["Min"] = round(min(results), 4)
        
        Q3, Q1 = np.percentile(results, [75 ,25])
        
        details["Q1"] = round(Q1, 4)
        details["Median"] = round(statistics.median(results), 4)
        details["Q3"] = round(Q3, 4)
        details["Max"] = round(max(results), 4)
        details["Mean"] = round(np.mean(results), 4)
        details["StDev"] = round(statistics.stdev(results), 4)
        
        
        data["x_axis"] = columnName
        data["y_axis"] = "Value"
        data["data"] = [details]
    else:
        dataSQL += "SELECT [" + columnName + "], COUNT(*) AS freq FROM "
        dataSQL += "GSE13355.dbo." + tableName + " GROUP BY [" + columnName + "] ORDER BY 2 DESC"
        
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        
        curr = []
        
        for x in results:
            curr.append({
                "label" : x[0],
                "count" : x[1]
            })
        
        data["x_axis"] = "label"
        data["y_axis"] = "count"
        data["data"] = curr

    return data
	
def get_bivariate_data(attrType_x,attrType_y,columnName_x,columnName_y, tableName):
    dataSQL = ""
    
    data={}
    
    if((attrType_x == "numerical" and attrType_y == "categorical")  or (attrType_x == "categorical" and attrType_y == "numerical") ):
        
        if(attrType_x=="numerical"):
            attrType_y , attrType_x = attrType_x , attrType_y
            columnName_y ,columnName_x = columnName_x ,columnName_y
            
        dataSQL="Select "+columnName_x+", Sum(cast(["+columnName_y+"] As float)) As SumX, "
        dataSQL+="Sum(cast(["+columnName_y+"] As float)*cast(["+columnName_y+"] As float)) As SumX2,"
        dataSQL+="Count(*) As frq  FROM GSE13355.dbo."+tableName
        dataSQL+=" WHERE  1=1  And ["+ columnName_y +"] Is Not null GROUP BY ["+ columnName_x +"] ORDER BY 1 "
        
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        data_bar=[]
        data_pie=[]
        table=[]
        t_mean= 0
        
        for x in results:
            data_col_bar={}
            data_col_pie={}
            data_col_bar["name"]=x[0]
            data_col_bar["count"]=x[3]
            data_col_bar["value"]=x[1]/x[3]
            table.append(x)
            data_col_pie["name"]=x[0]
            data_col_pie["mean"]=x[1]/x[3]
            data_col_pie["error"]=0.3
            
            data_bar.append(data_col_bar)
            data_pie.append(data_col_pie)
            
        data["bar"]=data_bar
        data["pie"]=data_pie
        
        t_mean=0
        total_observations =0
        
        for e in table:
            total_observations +=e[3]
            t_mean +=e[1]
        
        t_mean=t_mean/total_observations
        
        data["B_SS"]=0
        data["B_DF"]=len(table)-1
        
        data["W_SS"]=0
        
        for e in table:
            data["B_SS"]+=e[2]-2*t_mean*e[1]+e[3]*t_mean*t_mean
            data["W_SS"]+=e[2]-2*(e[1]/e[3])*e[1]+e[3]*(e[1]/e[3])*(e[1]/e[3])
            
        data["B_MS"]=data["B_SS"]/data["B_DF"]
        data["W_DF"]=total_observations - len(table)
        data["W_MS"]=data["W_SS"]/data["W_DF"]
        data["B_F"]=data["B_MS"]/data["W_MS"]
        data["B_pvalue"]=1-scipy.stats.f.cdf(data["B_F"],data["B_DF"],data["W_DF"])
        data["B_trend"]=0
        data["T_SS"]=data["W_SS"]+data["B_SS"]
        data["T_DF"]=data["B_DF"]+data["W_DF"]
        
        return data
    
    elif(attrType_x == "numerical" and attrType_y == "numerical"):
        
        dataSQL="SELECT TOP 100  cast(["+columnName_x+"] as float) AS ["+columnName_x+"],"
        dataSQL+="cast(["+columnName_y+"] as float) AS ["+columnName_y+"]"
        dataSQL+=" FROM GSE13355.dbo."+tableName+" WHERE  1=1  AND ["+columnName_x+"] is not null AND ["+columnName_y+"] is not null"

        cursor.execute(dataSQL)
        results = cursor.fetchall()
        data_bar={}
        data_pie={}
    
        curr_bar= []
        result_list=[[],[]]
        
        for x in results:
            result_list[0].append(x[0])
            result_list[1].append(x[1])
            
            curr_bar.append({
                
                columnName_x : x[0],
                columnName_y : x[1]
            })
        
        data_bar["x_axis"] = columnName_x
        data_bar["y_axis"] = columnName_y
        data_bar["data"] = curr_bar
        data["data"]=[data_bar]
        data_pie["x_axis"] = "Name"
        data_pie["y_axis"] = "value"
        
        for x in range(2):
            details = {}
            details["Min"] = min(result_list[x])
            details["Max"] = max(result_list[x])
            details["Mean"] = np.mean(result_list[x])
            
            details["Count"] = len(result_list[x])
            details["Median"] = statistics.median(result_list[x])
            
            details["StDev"] = round(statistics.stdev(result_list[x]), 5)
        
            Q3, Q1 = np.percentile(result_list[x], [75 ,25])
        
            details["Q1"] = Q1
            details["Q3"] = Q3
            if(x==0):
                details["name"]=columnName_x
                data_pie["data"] = [details]
            else:
                details["name"]=columnName_y
                data_pie["data"].append(details)
        
        corr = scipy.stats.pearsonr(result_list[0], result_list[1])
        ttest = scipy.stats.ttest_ind(result_list[0], result_list[1])
        
        data["correlation"]=corr[0]
        data["ttest"]=ttest[0]
        data["pvalue"]=ttest[1]
        
        data["data"].append(data_pie)
        
        return data
    else:
        dataSQL="SELECT ["+columnName_x+"],["+columnName_y+"], Count(*) as Frq "
        dataSQL+="FROM GSE13355.dbo."+tableName+" WHERE  1=1  GROUP BY ["+columnName_x+"],["+columnName_y+"] ORDER BY ["+columnName_x+"],["+columnName_y+"]"
        
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        result_list=[[],[]]
        
        for x in results:
            result_list[0].append(x[0])
            result_list[1].append(x[1])
        
        data_bar=[]
        data_pie=[]
        
        col1_set=set()
        col2_set=set()
        col3_dict={}
        
        for x in results:
            col1_set.add(x[0])
            col2_set.add(x[1])
            col3_dict[(x[0],x[1])]=x[2]
            
        sum_dict={}
        
        for x in col1_set:
            data_col={}
            data_col_pie={}
            data_col["Name"]=x
            data_col_pie["Name"]=x
            
            count=0
            
            for y in col2_set:
                count+=col3_dict[(x,y)]
                data_col[y]=col3_dict[(x,y)]
            
            sum_dict[x]=count
            
            for y in col2_set:
                data_col[y]=col3_dict[(x,y)]
                data_col_pie[y]=round(col3_dict[(x,y)]*100/sum_dict[x],2)
            
            data_bar.append(data_col)
            data_pie.append(data_col_pie)
        
        data["bar"]=data_bar
        data["pie"]=data_pie
        
        x=set(result_list[0])
        y=set(result_list[1])
        
        table=[]
        
        for i in x:
            temp=[]
            for j in y:
                temp.append(col3_dict[(i,j)])
            table.append(temp)
        
        stat, p, dof, expected = chi2_contingency(table)
        
        data["chi"] = stat
        data["df"]=dof
        data["pvalue"]=p
        
        rh = scipy.stats.spearmanr(result_list[0],result_list[1])
        
        data["rho"] = rh[0] 
        data["count"] = len(result_list[0])
        
        return data
		
    return data