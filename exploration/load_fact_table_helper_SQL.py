import pymssql

conn = pymssql.connect(server='13.92.0.168', user='saedsayad', password='mordab1339235$', database='GSE13355')
cursor = conn.cursor()

def get_datatype(table_name):
    dataTypeSQL = "SELECT DATA_TYPE, COLUMN_NAME FROM [GSE13355].[INFORMATION_SCHEMA].[COLUMNS] WHERE TABLE_NAME = '" + table_name + "'"
    cursor.execute(dataTypeSQL)
    data = cursor.fetchall()
    
    dic = {}
    
    categorical_type = ["char", "varchar", "nchar", "nvarchar", "text", "ntext"]

    for x in data:
        if(x[0] in categorical_type):
            dic[x[1]] = "categorical"
        else:
            dic[x[1]] = "numerical"
    
    return dic
    
def get_all_probes():
    probeSQL = "SELECT PID FROM GSE13355.dbo.GSE13355_probes"
    cursor.execute(probeSQL)
    probes = cursor.fetchall()
    
    probes = [{"name":item[0], "type" : "numerical"} for item in probes]
    return probes

def get_all_tables():
    tableSQL = "SELECT [name] FROM GSE13355.dbo.sysobjects "
    tableSQL += " WHERE xtype='U' AND [name] LIKE '%fact' AND SUBSTRING([name],1,5)!='slice' ORDER BY 1"
    cursor.execute(tableSQL)

    allTables = cursor.fetchall()
    
    return allTables

def get_all_columns(tableName):
    type_map = get_datatype(tableName)
    columnSQL = "SELECT TOP(100) * FROM " + tableName + " WHERE 1=2"
    cursor.execute(columnSQL)
    
    curr = []
    
    for x in cursor.description:
        columnName = x[0]
            
        curr.append({
            "name" : columnName,
            "type" : type_map[columnName]
            })
        
    return curr

def gather_all_data():
    res = {}

    probes = get_all_probes()
    allTables = get_all_tables()
    
    for eachTable in allTables:
        curr = get_all_columns(eachTable[0])
        
        res[eachTable[0]] = {
            "X" : curr,
            "Y" : curr + probes
        }

    return res