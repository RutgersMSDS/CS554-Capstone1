from Bioada import DBHelper as db_con
from django.http import JsonResponse

conn= db_con.DBConnection.Instance()
cursor = conn.cursor

def get_datatype(databaseName, table_name):
    dataTypeSQL = "SELECT DATA_TYPE, COLUMN_NAME FROM [" + databaseName + "].[INFORMATION_SCHEMA].[COLUMNS] WHERE TABLE_NAME = '" + table_name + "'"
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
    
def get_all_probes(databaseName):
    probeSQL = "SELECT PID FROM " + databaseName + ".dbo." + databaseName + "_probes"
    cursor.execute(probeSQL)
    probes = cursor.fetchall()
    
    probes = [{"name":item[0], "type" : "numerical"} for item in probes]
    return probes

def get_all_tables(databaseName):
    tableSQL = "SELECT [name] FROM " + databaseName + ".dbo.sysobjects "
    tableSQL += " WHERE xtype='U' AND [name] LIKE '%fact' AND SUBSTRING([name],1,5)!='slice' ORDER BY 1"
    cursor.execute(tableSQL)

    allTables = cursor.fetchall()
    
    return allTables

def get_all_columns(databaseName, tableName):
    type_map = get_datatype(databaseName, tableName)
    columnSQL = "SELECT TOP(100) * FROM " + databaseName + ".dbo." + tableName + " WHERE 1=2"
    
    cursor.execute(columnSQL)
    
    curr = []
    
    for x in cursor.description:
        columnName = x[0]
            
        curr.append({
            "name" : columnName,
            "type" : type_map[columnName]
            })
        
    return curr

def gather_all_data(databaseName):
    res = {}

    probes = get_all_probes(databaseName)
    allTables = get_all_tables(databaseName)
    
    for eachTable in allTables:
        curr = get_all_columns(databaseName, eachTable[0])
        
        res[eachTable[0]] = {
            "X" : curr,
            "Y" : curr + probes
        }

    return res

def getdata(type):
    if(type == 'render'):
        tableSQL = "SELECT [GSE],[SubmissionYear],[Subject],[Organ],[Source],[Samples],[Assay],[Platform],[Title] FROM [GEO].[dbo].[DeepDive] where IsActive=1"
    else:
        tableSQL = "select DD.GSE,[SubmissionYear],[Subject],[Organ],[Source],[Samples],[Assay],[Platform],[Title] " +\
                  ",URL,DD.Notes as 'Public Notes',DDN.Notes as 'Private Notes' " +\
                  "from [GEO].[dbo].[DeepDive] DD left outer join [GEO].[dbo].[DeepDiveNotes] DDN on DD.GSE=DDN.GSE " +\
                  "where DD.GSE='" + type + "'"
    cursor.execute(tableSQL)
    data = cursor.fetchall()
    rows=[]
    for row in data:
        singlerow={}
        singlerow['GSE'] = row[0]
        singlerow['Year'] = row[1]
        singlerow['Subject'] = row[2]
        singlerow['Organ'] = row[3]
        singlerow['Source'] = row[4]
        singlerow['Samples'] = row[5]
        singlerow['Assay'] = row[6]
        singlerow['Platform'] = row[7]
        singlerow['Title'] = row[8]
        if(type != 'render'):
            singlerow['URL'] = row[9]
            singlerow['Public_Notes'] = row[10]
            singlerow['Private_Notes'] = row[11]
        rows.append(singlerow)
    return rows

def DeleteGSE(gsevalue):
    query2 = "drop database if exists {}".format(gsevalue);
    cursor.execute(query2)
    SQLquery = "Update [GEO].[dbo].[DeepDive] set IsActive =0 where GSE='" + str(gsevalue) + "';";
    cursor.execute(SQLquery)
    desc= cursor.description
    return desc


def SaveGSEData(dict):
    Querytxt = "Update [GEO].[dbo].[DeepDive] " + \
               "set GSE = '" + dict['GSE'] + "'," + \
                "SubmissionYear = '"+dict['Year']+"', " + \
                "Samples = '" + dict['Samples'] + "'," + \
                "Subject = '" + dict['Subject'] + "'," + \
                "Platform = '" + dict['Platform'] + "'," + \
                "Title = '" + dict['Title'] + "'," + \
                "URL = '" + dict['URL'] + "'," + \
                "Notes = '" + dict['Public'] + "'," + \
                "Source = '" + dict['Source'] + "'," + \
                "Organ = '" + dict['Organ'] + "'," + \
                "Assay = '" + dict['Assay'] + "'," +\
                "ProbeType='R'," +\
                "IsActive=1 " + \
    "where GSE='" + dict['GSE'] + "';"
    cursor.execute(Querytxt)
    privateQuery = "IF EXISTS (SELECT * FROM [GEO].[dbo].[DeepDiveNotes] WHERE GSE ='" + dict['GSE'] + "') " +\
                   "Update [GEO].[dbo].[DeepDiveNotes] set Notes='" + dict['Private'] + "' where GSE='" + dict['GSE'] + "'" +\
                   "ELSE " +\
                   "Insert into [GEO].[dbo].[DeepDiveNotes] values('web','"+dict['GSE']+"','"+ dict['Private'] +"')"

    cursor.execute(privateQuery)
    # conn.commit()
    desc = cursor.rowcount
    return desc

def GetTargets(GSEValue,tablename):
    if tablename == 'Targets':
        tablename = "[" + GSEValue + "].[dbo].[" + GSEValue + "_targets]";
        columnquery = "SELECT COLUMN_NAME FROM [" + GSEValue + "].[INFORMATION_SCHEMA].[COLUMNS] WHERE TABLE_NAME = '" + GSEValue + "_targets'";
    elif tablename == 'Probes':
        tablename = "[" + GSEValue + "].[dbo].[" + GSEValue + "_probes]";
        columnquery = "SELECT COLUMN_NAME FROM [" + GSEValue + "].[INFORMATION_SCHEMA].[COLUMNS] WHERE TABLE_NAME = '" + GSEValue + "_probes'";
    else:
        tablename = "[" + GSEValue + "].[dbo].[slice_001_fact]";
        columnquery = "SELECT TOP 50 COLUMN_NAME FROM [" + GSEValue + "].[INFORMATION_SCHEMA].[COLUMNS] WHERE TABLE_NAME = 'slice_001_fact'";

    SQLQuery = "select * from " + tablename;
    cursor.execute(SQLQuery)
    result = cursor.fetchall()
    cursor.execute(columnquery)
    columns= cursor.fetchall()
    return result,columns