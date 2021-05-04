import math
import bisect

from Bioada import DBHelper as db_con
cursor = db_con.DBConnection.Instance().cursor

def get_tuples_and_nums(pos, neg, step):
    all_pairs = []            
    nums = set()
    
    for i in range(pos):
        all_pairs.append((i * step, (i+1) * step))
        nums.add(i * step)
    
    for i in range(neg):
        all_pairs.append((-((i+1) * step), -(i * step)))
        nums.add(-((i+1) * step))
        
    nums.add(pos * step)
    
    return all_pairs, sorted(list(nums))

def get_matching_tuple(ls, target):
    x = bisect.bisect(ls, target)
    
    if(x == 0):
        return (0, 1)
    
    if(x == len(ls)):
        return (ls[x-2], ls[x-1])
    
    return (ls[x-1], ls[x])

def get_univariate_binned_data(attrType, columnName, tableName, databaseName, binSize):
    dataSQL = "SELECT [" + columnName + "] from " + databaseName + ".dbo." + tableName 
    cursor.execute(dataSQL)
    
    results = cursor.fetchall()
    results = [x[0] for x in results]
    
    minVal = min(results)
    maxVal = max(results)
    
    modified_min = math.floor(minVal)
    modified_max = math.ceil(maxVal)
    
    totalPos = abs(math.ceil(modified_max / binSize))
    totalNeg = abs(math.floor(modified_min / binSize))
    
    all_pairs, nums = get_tuples_and_nums(totalPos, totalNeg, binSize)
    count_dic = {}
    
    for a in all_pairs:
        count_dic[a] = 0
    
    for r in results:
        x = get_matching_tuple(nums, r)
        
        if(x in count_dic):
            count_dic[x] += 1
            
    res = {}
    
    res["x_axis"] = "label"
    res["y_axis"] = "count"
    
    curr = []
    
    count_dic = dict(sorted(count_dic.items()))
    
    for x in count_dic:
        temp = {}
        temp["label"] = str(x[0]) + " to " + str(x[1])
        temp["count"] = count_dic[x]
        curr.append(temp)
    
    res["data"] = curr
    return res
def get_bivariate_binned_data(column_data,tableName,databaseName):
    
    columnName_x = column_data[0]["columnName"]
    attrType_x = column_data[0]["columnType"]
    binSize_x = int(column_data[0]["binningSize"])
    
    columnName_y = column_data[1]["columnName"]
    attrType_y = column_data[1]["columnType"]
    binSize_y = int(column_data[1]["binningSize"])
    
    
    if(binSize_x != 0):
        attrType_x = "binning"
    if(binSize_y != 0):
        attrType_y = "binning"
    
    
        
    if(attrType_x == "binning" and attrType_y == "numerical" ):
        
        dataSQL = "SELECT [" + columnName_x + "],["+ columnName_y +  "] from " + databaseName + ".dbo." + tableName 
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        data={}
        result_x = []
        data_bar=[]
        data_pie=[]
        
        ans_cols={}
        
        for x in results:
            result_x.append(x[0])
            
            
        minVal = min(result_x)
        maxVal = max(result_x)
        print(minVal)
        print(maxVal)
        
        modified_min = math.floor(minVal)
        modified_max = math.ceil(maxVal)
        
        totalPos = math.ceil(modified_max / binSize_x)
        totalNeg = math.floor(modified_min / binSize_x)
        
        key_set=set()
        for i in range(totalNeg,totalPos,1):
            key_set.add((i*binSize_x,(i+1)*binSize_x))
        print(key_set)
        
        for x in results:
            key_r = math.ceil(x[0] / binSize_x)*binSize_x
            key_l = math.floor(x[0] / binSize_x)*binSize_x
            key = ((key_l,key_r))
            if(key in ans_cols):
                ans_cols[key][0]+=1
                ans_cols[key][1]+=x[1]             
            else:
                ans_cols[key]=[1,x[1]]
                
                
        print(ans_cols)
        for k,v in ans_cols.items():
            print(k,v)
            data_col_bar={}
            data_col_pie={}
            data_col_bar["name"]=str(k)
            data_col_bar["count"]=v[0]
            data_col_bar["value"]=v[1]/v[0]

            data_col_pie["name"]=str(k)
            data_col_pie["mean"]=v[1]/v[0]
            data_col_pie["error"]=0.3
            
            data_bar.append(data_col_bar)
            data_pie.append(data_col_pie)
            
        data["bar"]=data_bar
        data["pie"]=data_pie
        
        return data
        
        
    elif(attrType_x == "binning" and attrType_y == "categorical" ):
        dataSQL = "SELECT [" + columnName_x + "],["+ columnName_y +  "] from " + databaseName + ".dbo." + tableName 
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        print(attrType_x,attrType_y)    
        result_x = []
        
        ans_cols={}
        
        for x in results:
            result_x.append(x[0])
            
            
        minVal = min(result_x)
        maxVal = max(result_x)
        print(minVal)
        print(maxVal)
        
        modified_min = math.floor(minVal)
        modified_max = math.ceil(maxVal)
        
        totalPos = math.ceil(modified_max / binSize_x)
        totalNeg = math.floor(modified_min / binSize_x)
        
        key_dict=set()
        for i in range(totalNeg,totalPos,1):
            key_dict.add((i*binSize_x,(i+1)*binSize_x))
        print(key_dict)
        
        for x in results:
            key_r = math.ceil(x[0] / binSize_x)*binSize_x
            key_l = math.floor(x[0] / binSize_x)*binSize_x
            key = ((key_l,key_r),x[1])
            if(key in ans_cols):
                ans_cols[key]+=1
            else:
                ans_cols[key]=1
        
        
        print(ans_cols)
        data={}
        data_bar=[]
        data_pie=[]    
        col_2=set()
        
        
        for x in results:
            col_2.add(x[1])
        
        sum_dict={}
        for x in key_dict:
            data_col={}
            data_col_pie={}
            data_col["Name"]=str(x)
            data_col_pie["Name"]=str(x)
            count=0
            for y in col_2:
                if((x,y) in ans_cols):
                    count+=ans_cols[(x,y)]
                    data_col[y]=ans_cols[(x,y)]
                else:
                    count+=0
                    data_col[y]=0
                     
            sum_dict[x]=count
            for y in col_2:
                if((x,y) in ans_cols ):       
                    data_col[y]=ans_cols[(x,y)]
                    data_col_pie[y]=round(ans_cols[(x,y)]*100/sum_dict[x],2)
                else:
                    data_col[y]=0
                    data_col_pie[y]=0
                    
            data_bar.append(data_col)
            data_pie.append(data_col_pie)
        data["bar"]=data_bar
        data["pie"]=data_pie
            
            
        return data
    
    elif(attrType_x == "categorical" and attrType_y == "binning" ):
        
        
        dataSQL = "SELECT [" + columnName_x + "],["+ columnName_y +  "] from " + databaseName + ".dbo." + tableName 
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        print(attrType_x,attrType_y)    
        result_y = []
        
        ans_cols={}
        
        for y in results:
            result_y.append(y[1])
            
            
        minVal = min(result_y)
        maxVal = max(result_y)
        print(minVal)
        print(maxVal)
        
        modified_min = math.floor(minVal)
        modified_max = math.ceil(maxVal)
        
        totalPos = math.ceil(modified_max / binSize_y)
        totalNeg = math.floor(modified_min / binSize_y)
        
        key_dict=set()
        for i in range(totalNeg,totalPos,1):
            key_dict.add((i*binSize_y,(i+1)*binSize_y))
        print(key_dict)
        
        for x in results:
            key_r = math.ceil(x[1] / binSize_y)*binSize_y
            key_l = math.floor(x[1] / binSize_y)*binSize_y
            key = (x[0],(key_l,key_r))
            if(key in ans_cols):
                ans_cols[key]+=1
            else:
                ans_cols[key]=1
        
        print(ans_cols)
        data={}
        data_bar=[]
        data_pie=[]    
        col_2=set()
        
        
        for x in results:
            col_2.add(x[0])
        
        sum_dict={}
        for x in col_2:
            data_col={}
            data_col_pie={}
            data_col["Name"]=x
            data_col_pie["Name"]=x
            count=0
            for y in key_dict:
                if((x,y) in ans_cols):
                    count+=ans_cols[(x,y)]
                    data_col[str(y)] = ans_cols[(x,y)]
                else:
                    count+=0
                    data_col[str(y)]=0
                     
            sum_dict[x]=count
            for y in key_dict:
                if((x,y) in ans_cols ):       
                    data_col[str(y)]=ans_cols[(x,y)]
                    data_col_pie[str(y)]=round(ans_cols[(x,y)]*100/sum_dict[x],2)
                else:
                    data_col[str(y)]=0
                    data_col_pie[str(y)]=0
                    
            data_bar.append(data_col)
            data_pie.append(data_col_pie)
        data["bar"]=data_bar
        data["pie"]=data_pie
            
            
        return data
    elif(attrType_x == "numerical" and attrType_y == "binning" ):
        
        attrType_x,attrType_y = attrType_y,attrType_x
        columnName_x,columnName_y = columnName_y,columnName_x
        binSize_x,binSize_y = binSize_y,binSize_x
        
        dataSQL = "SELECT [" + columnName_x + "],["+ columnName_y +  "] from " + databaseName + ".dbo." + tableName 
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        data={}
        result_x = []
        data_bar=[]
        data_pie=[]
        
        ans_cols={}
        
        for x in results:
            result_x.append(x[0])
            
            
        minVal = min(result_x)
        maxVal = max(result_x)
        print(minVal)
        print(maxVal)
        
        modified_min = math.floor(minVal)
        modified_max = math.ceil(maxVal)
        
        totalPos = math.ceil(modified_max / binSize_x)
        totalNeg = math.floor(modified_min / binSize_x)
        
        key_set=set()
        for i in range(totalNeg,totalPos,1):
            key_set.add((i*binSize_x,(i+1)*binSize_x))
        print(key_set)
        
        for x in results:
            key_r = math.ceil(x[0] / binSize_x)*binSize_x
            key_l = math.floor(x[0] / binSize_x)*binSize_x
            key = ((key_l,key_r))
            if(key in ans_cols):
                ans_cols[key][0]+=1
                ans_cols[key][1]+=x[1]             
            else:
                ans_cols[key]=[1,x[1]]
                
                
        print(ans_cols)
        for k,v in ans_cols.items():
            print(k,v)
            data_col_bar={}
            data_col_pie={}
            data_col_bar["name"]=str(k)
            data_col_bar["count"]=v[0]
            data_col_bar["value"]=v[1]/v[0]

            data_col_pie["name"]=str(k)
            data_col_pie["mean"]=v[1]/v[0]
            data_col_pie["error"]=0.3
            
            data_bar.append(data_col_bar)
            data_pie.append(data_col_pie)
            
        data["bar"]=data_bar
        data["pie"]=data_pie
        
        return data
        
    else:
        dataSQL = "SELECT [" + columnName_x + "],["+ columnName_y +  "] from " + databaseName + ".dbo." + tableName 
        cursor.execute(dataSQL)
        results = cursor.fetchall()
        print(attrType_x,attrType_y)    
        result_x = []
        result_y = []
        
        ans_cols={}
        
        for x in results:
            result_x.append(x[0])
        for y in results:
            result_y.append(y[1])
            
            
            
        minVal_x = min(result_x)
        maxVal_x = max(result_x)
        
        minVal_y = min(result_y)
        maxVal_y = max(result_y)
        
        modified_min_x = math.floor(minVal_x)
        modified_max_x = math.ceil(maxVal_x)
        
        modified_min_y = math.floor(minVal_y)
        modified_max_y = math.ceil(maxVal_y)
        
        totalPos_x = math.ceil(modified_max_x / binSize_x)
        totalNeg_x = math.floor(modified_min_x / binSize_x)
        
        totalPos_y = math.ceil(modified_max_y / binSize_y)
        totalNeg_y = math.floor(modified_min_y / binSize_y)
        
        key_set_x=set()
        key_set_y=set()
        
        for i in range(totalNeg_x,totalPos_x,1):
            key_set_x.add((i*binSize_x,(i+1)*binSize_x))
        print(key_set_x)
        
        for i in range(totalNeg_y,totalPos_y,1):
            key_set_y.add((i*binSize_y,(i+1)*binSize_y))
        print(key_set_y)
        
        
        
        for x in results:
            key_r_x = math.ceil(x[0] / binSize_x)*binSize_x
            key_l_x = math.floor(x[0] / binSize_x)*binSize_x
            key_r_y = math.ceil(x[1] / binSize_y)*binSize_y
            key_l_y = math.floor(x[1] / binSize_y)*binSize_y
            
            key = ((key_l_x,key_r_x),(key_l_y,key_r_y))
            if(key in ans_cols):
                ans_cols[key]+=1
            else:
                ans_cols[key]=1
        
        
        print(ans_cols)
        data={}
        data_bar=[]
        data_pie=[]    
        
        
        sum_dict={}
        
        for x in key_set_x:
            data_col={}
            data_col_pie={}
            data_col["Name"]=str(x)
            data_col_pie["Name"]=str(x)
            count=0
            for y in key_set_y:
                if((x,y) in ans_cols):
                    count+=ans_cols[(x,y)]
                    data_col[str(y)]=ans_cols[(x,y)]
                else:
                    count+=0
                    data_col[str(y)]=0
                     
            sum_dict[x]=count
            for y in key_set_y:
                if((x,y) in ans_cols ):       
                    data_col[str(y)]=ans_cols[(x,y)]
                    data_col_pie[str(y)]=round(ans_cols[(x,y)]*100/sum_dict[x],2)
                else:
                    data_col[str(y)]=0
                    data_col_pie[str(y)]=0
                    
            data_bar.append(data_col)
            data_pie.append(data_col_pie)
        data["bar"]=data_bar
        data["pie"]=data_pie
            
            
        return data
        
   
    
    
    
    
    return data