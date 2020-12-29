import csv
from django.db import connection
import datetime
import pyodbc
import calculation.Query as Q
import random
import calculation.Functions_Calculate as f_c
from itertools import chain

#======Database Connections===========================#
#conn1 = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER=65.0.33.214;DATABASE=FDS_Datafeeds;UID=sa;PWD=Indxx@1234')
cur = connection.cursor()
#==== Temporary dict data====//
D_Index = {}
D_Index["Identifier"] = "ISIN"
D_Index["IV"] = 1000
D_Index["MV"] = 100000
D_Index["Currency"] = "EUR"
D_Index["Adjustment"] = "DA"#"SA"
D_Index["DCFO"] = "ND"#"CD","EDD"

def Validate_Read_CSV(file_Name, IDentifier):
    d1 = {}
    d2 = {}
    D_Data= {}
    D_Date = {}
    D_ISIN = {}
    last_Period = 1
    errorMessage = ""
    warningMessage = ""
    with open(file_Name,'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)
        for line in csvreader:
            #print(line)
            '''Check for Mandatory Fields'''
            if line[0] in (None, "") or line[1] in (None, "") or line[2] in (None, "") or line[3] in (None, "") or line[4] in (None, ""):
                return "Please check your portfolio.Few Securities does not have proper period, proper ISIN, proper weight or proper Start Date and End Date.","",D_Data,D_Date,D_ISIN,last_Period
            else:
                period = line[0]
                last_Period = period
                Load_Data(line,d1,d2,D_Data,D_Date,D_ISIN)
        '''Check for Total sum of weights'''
        for key in d1:
            #print(d1[key])
            if d1[key]>100.44 or d1[key]<99.50:
                errorMessage += "Total weight of period " + key +" is " + str(d1[key])+"."
        '''Check for Delisted Securities'''
        for key in D_ISIN:
            isins=D_ISIN[key]
            #print(str(isins)[1:-1])
            startDate = D_Date[key+'_'+'START']
            #print(startDate)
            delistedISINs = Delisting_Check(isins,startDate,IDentifier)
            if delistedISINs not in (None, ""):
                errorMessage += "Securities " + delistedISINs +" of period - "+key+" is not trading start at the start of the period . "
        '''Check for Warning '''
        for key in d2:
             if d2[key]>45:
                 warningMessage +="Sum of weights of securities for period " + key +" with greater than 5% weight is  " + str(d2[key])+"."
        if errorMessage not in (None, ""):
            errorMessage = "Please check your portfolio."+errorMessage
    #print(last_Period)last_Period
    final_data = {'error':errorMessage, 'warning': warningMessage, 'D_Data':D_Data, 'D_Date': D_Date, 'D_ISIN':D_ISIN, 'last_Period':last_Period}
    return final_data

def  Load_Data(line,d1,d2,D_Data,D_Date,D_ISIN):
    period = line[0]
    weight = float(line[2][0:-1])
    if period+'_'+'START' not in D_Date:
        D_Date[period+'_'+'START'] = line[3]
    D_Date[period+'_'+'END'] = line[4]
    if period not in D_Data:
        D_Data[period] = list()
    D_Data[period].append(line)
    if period not in D_ISIN:
        D_ISIN[period] = list()
    D_ISIN[period].append(line[1])
    if period in d1:
        d1[period] += weight
    else:
        d1[period] = weight
    if weight > 5:
        if period in d2:
            d2[period] += weight
        else:
            d2[period] = weight

def Delisting_Check(ISIN_LIST,E_DATE,IDentifier):
    isins = str(ISIN_LIST)[1:-1]
    delistedISINs=""
    format_str = '%m/%d/%Y' # The format
    datetime_obj = datetime.datetime.strptime(E_DATE, format_str)
    S_DATE = str(datetime_obj.date()- datetime.timedelta(days=5))
    Query= Q.Query_Price(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    dir1 = {}
    delistedISINs
    for row in cur:
        dir1[row[0]] = row[2]
    for ISIN in ISIN_LIST:
        if ISIN not in dir1:
            delistedISINs += ISIN +","
    return delistedISINs

def Get_TAX(cur):
    cur.execute('SELECT * from FDS_DataFeeds.dbo.tax_rate ')
    dir = {}
    for row in cur:
        dir[row[1]] = row[2].strip()
    return dir

def Get_CA(cur,ISIN_LIST,S_DATE,E_DATE,IDentifier):
    isins = str(ISIN_LIST)[1:-1]
    D_CA ={}
    D_CA_Dividend = {}
    D_CA_Spin ={}
    Query= Q.Query_Divident(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        var = row[0]+'_'+row[1].strftime("%x")
        if var not in D_CA_Dividend:
            D_CA_Dividend[var] = list()
        D_CA_Dividend[var].append(row)
    D_CA["Dividend"] = D_CA_Dividend

    Query= Q.Query_Split(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        var = row[0]+'_'+row[1].strftime("%x")
        if var not in D_CA_Spin:
            D_CA_Spin[var] = list()
        D_CA_Spin[var].append(row)
    D_CA["Spin"] = D_CA_Spin

    return D_CA

def Get_PRICE(cur,ISIN_LIST,S_DATE,E_DATE,IDentifier):
    print("inside get price")
    isins = str(ISIN_LIST)[1:-1]
    Query= Q.Query_Price(IDentifier,isins,S_DATE,E_DATE)
    currency_list = []
    cur.execute(Query)
    D_Price = {}
    D_ISIN_Currency ={}
    D_LastDate = {}
    for row in cur:
        D_Price[row[0]+'_'+row[1].strftime("%x")] = row[2]
        D_ISIN_Currency[row[0]] = row[3]
        D_LastDate[row[0]] = row[1].strftime("%x")
        if row[3] not in currency_list:
            currency_list.append(row[3])
    return D_Price,D_LastDate,currency_list,D_ISIN_Currency

def Get_Currency(cur,C_list,S_DATE,E_DATE):
    clist = str(C_list)[1:-1]
    Query="SELECT RTS.iso_currency, RTS.date, RTS.exch_rate_usd, RTS.exch_rate_per_usd FROM FDS_DataFeeds.ref_v2.fx_rates_usd AS RTS WHERE RTS.date between '"+S_DATE+"' and '"+E_DATE+"' and RTS.iso_currency in ("+clist +") ORDER BY RTS.date"
    print("Currency Query : "+Query)
    cur.execute(Query)
    dir = {}
    for row in cur:
        dir[row[0]+'_'+row[1].strftime("%x")] = (row[3])
    return dir

def Cal_Index(D_Index,D_Data,D_ISIN,D_Date):
    Index_List = list()
    print("inside cal_Index")
    Constituents_List = list()
    for period in D_Data:
        print("inside cal_Index")
        Index_Currency = D_Index["Currency"]
        format_str = '%m/%d/%Y'
        S_Date = datetime.datetime.strptime(D_Date[period+"_START"], format_str).date()- datetime.timedelta(days=0)
        S_Date_Minus_Five = datetime.datetime.strptime(D_Date[period+"_START"], format_str).date()- datetime.timedelta(days=5)
        E_Date = datetime.datetime.strptime(D_Date[period+"_END"], format_str).date()- datetime.timedelta(days=0)

        i=0

        D_Index["M_Cap_PR"],D_Index["M_Cap_TR"],D_Index["M_Cap_NTR"]=D_Index["MV"],D_Index["MV"],D_Index["MV"]
        D_Index["Index_Value_PR"], D_Index["Index_Value_TR"],D_Index["Index_Value_NTR"]= D_Index["IV"],D_Index["IV"],D_Index["IV"]
        Divisor = D_Index["MV"]/D_Index["IV"]
        D_Index["Divisor_PR"], D_Index["Divisor_TR"],D_Index["Divisor_NTR"]=Divisor,Divisor,Divisor

        D_Price,D_LastDate,currency_list,D_ISIN_Currency = Get_PRICE(cur,D_ISIN[period],S_Date_Minus_Five.strftime("%x"),E_Date.strftime("%x"),D_Index["Identifier"])
        currency_list.append(Index_Currency)
        Ex_Rate = Get_Currency(cur,currency_list,S_Date_Minus_Five.strftime("%x"),E_Date.strftime("%x"))
        Tax_Rate = Get_TAX(cur)
        #D_CA = f.Get_CA(cur,D_ISIN[period],S_Date.strftime("%x"),E_Date.strftime("%x"),D_Index["Identifier"])
        #print(D_CA)

        Latest_Price={}
        Latest_Ex_Rate={}

        while S_Date_Minus_Five <= E_Date:
            print(D_Price)
            print(Ex_Rate)
            f_c.Set_Latest_Ex_Rate(Index_Currency,D_Data[period],Ex_Rate,Latest_Ex_Rate,S_Date_Minus_Five.strftime("%x"),D_ISIN_Currency)
            f_c.Set_Latest_Price(D_Data[period],D_Price,Latest_Price,S_Date_Minus_Five.strftime("%x"))
            if S_Date_Minus_Five>=S_Date:
                if i==0:
                    f_c.Cal_Shares(D_Index,D_Data[period],Latest_Price,Latest_Ex_Rate,S_Date_Minus_Five.strftime("%x"),Constituents_List,period,Tax_Rate,D_ISIN_Currency)
                else:
                    M_Cap = f_c.Cal_Index_Close(D_Index,D_Data[period],Latest_Price,Latest_Ex_Rate,S_Date_Minus_Five.strftime("%x"),Constituents_List,period,Tax_Rate,D_ISIN_Currency)
                f_c.Fill_Index_Report_Data(D_Index,Index_List,period,S_Date_Minus_Five)
                i += 1

            if S_Date_Minus_Five.weekday()==4:
                S_Date_Minus_Five = S_Date_Minus_Five + datetime.timedelta(days=3)
            else:
                S_Date_Minus_Five = S_Date_Minus_Five + datetime.timedelta(days=1)

            #if S_Date_Minus_Five>=S_Date:
            #  f_c.Adjust_CA(D_Index,D_Data[period],Latest_Price,Latest_Ex_Rate,S_Date.strftime("%x"),D_ISIN_Currency,D_CA,Ex_Rate)
    files = f_c.Print_Reports(Index_List,Constituents_List)
    return files


def handle_uploaded_file(file):
    if file:
        random_id = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
        file_name = random_id+'-'+file.name
        with open('./static/backtest-file/input/'+file_name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return file_name

def remove_percent_symbole(weight):
    weight = list(weight)
    weight =  weight[:-1]
    weight = ''.join([str(elem) for elem in weight])
    return weight

