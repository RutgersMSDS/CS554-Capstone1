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