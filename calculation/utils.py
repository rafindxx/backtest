import csv
from django.db import connection
import datetime
import pyodbc
import calculation.Query as Q
import random
import calculation.Functions_Calculate as f_c
from itertools import chain
import pandas as pd

#======Database Connections===========================#
conn1 = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER=65.0.33.214;DATABASE=FDS_Datafeeds;UID=sa;PWD=Indxx@1234')
cur = conn1.cursor()

def Validate_Read_CSV(file_Name, IDentifier):
    d1 = {}
    d2 = {}
    D_Data= {}
    D_Date = {}
    D_ISIN = {}
    D_RIC_ISIN = {}
    last_Period = 1
    errorMessage = ""
    warningMessage = ""
    df = pd.read_csv(file_Name)
    csv_check = column_validation_check(df)
    if csv_check == False:
        errorMessage = {'error':"Please add valid data in csv file."}
        return errorMessage
    store_period = df['Period'].iloc[0]
    store_start_date =  df['Start date'].iloc[0]
    store_end_date =  df['End date'].iloc[0]
    with open(file_Name,'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)
        for line in csvreader:
            if line[0] == store_period and store_start_date != line[3] or store_end_date != line[4]:
                errorMessage = "Please check your portfolio start date and end date should be same for one period."
            elif line[0] != store_period:
                store_period = line[0]
                store_start_date = line[3]
                store_end_date = line[4]
            '''Check for Mandatory Fields'''
            if line[0] in (None, "") or line[1] in (None, "") or line[2] in (None, "") or line[3] in (None, "") or line[4] in (None, "") or line[5] in (None, ""):
                return "Please check your portfolio.Few Securities does not have proper period, proper ISIN, proper weight , proper Start Date and End Date or proper country.","",D_Data,D_Date,D_ISIN,last_Period,D_RIC_ISIN
            else:                
                startDate= line[3]
                endDate  = line[4]
                period = line[0]
                last_Period = period
                if '-' in startDate:
                    startDate = check_date_formate(startDate)
                    line[3] = startDate
                if '-' in endDate:
                    endDate = check_date_formate(endDate)
                    line[4] = endDate
                if (period+'_START' in D_Date and D_Date[period+'_START']!= startDate) or (period+'_END' in D_Date and D_Date[period+'_END']!= endDate) :
                    errorMessage = "Please check your portfolio.Start date and End date for same perioed should be same.","",D_Data,D_Date,D_ISIN,last_Period,D_RIC_ISIN
                else:                    
                    Load_Data(line,d1,d2,D_Data,D_Date,D_ISIN)

        '''Check for Total sum of weights'''                        
        for key in d1:
            if d1[key]>100.44 or d1[key]<99.50:
                errorMessage = "Total weight of period " + key +" is " + str(d1[key])+"."
        '''Check for Delisted Securities'''                        
        for key in D_ISIN:
            isins=D_ISIN[key]
            startDate = D_Date[key+'_'+'START']
            delistedISINs = Delisting_Check(isins,startDate,IDentifier)
            if delistedISINs not in (None, ""):
                errorMessage = "Securities " + delistedISINs +" of period - "+key+" is not trading start at the start of the period . "
        '''Check for Warning '''
        for key in d2:
             if d2[key]>45:
                 warningMessage ="Sum of weights of securities for period " + key +" with greater than 5% weight is  " + str(d2[key])+"."
        yesterday = datetime.datetime.now()- datetime.timedelta(days=1)
        yesterday_date = yesterday.strftime("%x")
        if '-' in D_Date[last_Period+'_END']:
            d_date_last_period = check_date_formate(D_Date[last_Period+'_END'])
        else:
            d_date_last_period = D_Date[last_Period+'_END']
        format_str = '%m/%d/%Y'
        S_Date = datetime.datetime.strptime(d_date_last_period, format_str).date()
        if yesterday_date == S_Date.strftime("%x"):
            for line in D_Data[last_Period]:
                if line[6] in (None, "") :
                    errorMessage =  "Please check your portfolio.Few Securities in last period does not have proper RIC.","",D_Data,D_Date,D_ISIN,last_Period
                else:
                     D_RIC_ISIN[line[6]]=line[1]
                    
        if errorMessage not in (None, ""):
            errorMessage = "Please check your portfolio."+errorMessage
        if D_RIC_ISIN:
            ric_error = check_ric(getList(D_RIC_ISIN))
            errorMessage = ric_error
        
    final_data = {'error':errorMessage, 'warning': warningMessage, 'D_Data':D_Data, 'D_Date': D_Date, 'D_ISIN':D_ISIN, 'last_Period':last_Period, 'D_RIC_ISIN':D_RIC_ISIN }
    return final_data

def Set_TR_Price(D_Date,D_RIC_ISIN,last_Period,D_Price):
    print(D_Date)
    yesterday = datetime.datetime.now()- datetime.timedelta(days=1)
    yesterday_date = yesterday.strftime("%x")
    format_str = '%m/%d/%Y'
    if str(last_Period)+'_START' in D_Date and str(last_Period)+'_END' in D_Date:
        E_Date = D_Date[str(last_Period)+'_END']
    else:
        E_Date = datetime.datetime.strptime(D_Date[last_Period+'_END'], format_str).date()
        E_Date = E_Date.strftime("%x")
    if yesterday_date == E_Date:
        TR_Price = Get_TR_PRICE(getList(D_RIC_ISIN),E_Date)
        for ric in D_RIC_ISIN:
            var1 = ric+'_'+date
            var2 = D_RIC_ISIN[ric]+'_'+date        
            if var1 in TR_Price:            
                trPrice = TR_Price[var1]
                if var2 not in D_Price:
                    D_Price[var2] = trPrice
        
def  Load_Data(line,d1,d2,D_Data,D_Date,D_ISIN):   
    period = str(line[0])
    weight = float(line[2][0:-1])
    if period+'_START' not in D_Date:
        D_Date[period+'_START'] = line[3]
    if period+'_END' not in D_Date:
        D_Date[period+'_END'] = line[4]
    if period not in D_Data:
        D_Data[period] = list()
    if len(line) == 6:
        line.append('')
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
    if '-' in E_DATE:
        E_DATE = check_date_formate(E_DATE)
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

def Get_TAX():   
    cur.execute('SELECT * from FDS_DataFeeds.dbo.tax_rate')
    dir = {}
    for row in cur:
        dir[row[1]] = float(row[2].strip()[0:-1])# row[2].strip()
    return dir

def Get_CA(ISIN_LIST,S_DATE,E_DATE,IDentifier):
    isins = str(ISIN_LIST)[1:-1]
    D_CA ={}
    D_CA_Dividend = {}
    D_CA_Split ={}
    Query= Q.Query_Divident(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        var = row[0]+'_'+row[5].strftime("%x")
        if var not in D_CA_Dividend:
            D_CA_Dividend[var] = list()
        D_CA_Dividend[var].append(row)
    D_CA["Dividend"] = D_CA_Dividend
    
    Query= Q.Query_Split(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        var = row[0]+'_'+row[1].strftime("%x")
        if var not in D_CA_Split:
            D_CA_Split[var] = list()
        D_CA_Split[var].append(row)
    D_CA["Split"] = D_CA_Split
    
    return D_CA
        
def Get_PRICE(ISIN_LIST,S_DATE,E_DATE,IDentifier):
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

def Get_TR_PRICE(RIC_LIST,DATE):
    connection = ms.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER=65.0.33.214;DATABASE=FDS_Datafeeds;UID=sa;PWD=Indxx@1234')
    cursor = connection.cursor()
    rics = str(RIC_LIST)[1:-1]
    Query= Q.Query_TR_Price(RIC_LIST,DATE)
    cursor.execute(Query)
    D_TR_Price = {}
    for row in cursor:
        D_TR_Price[row[0]+'_'+row[1].strftime("%x")] = row[2]
    cursor.close()
    connection.close()
    return D_TR_Price

def Get_Currency(C_list,S_DATE,E_DATE):
    clist = str(C_list)[1:-1]
    Query="SELECT RTS.iso_currency, RTS.date, RTS.exch_rate_usd, RTS.exch_rate_per_usd FROM FDS_DataFeeds.ref_v2.fx_rates_usd AS RTS WHERE RTS.date between '"+S_DATE+"' and '"+E_DATE+"' and RTS.iso_currency in ("+clist +") ORDER BY RTS.date"
    cur.execute(Query)
    dir = {}
    for row in cur:
        dir[row[0]+'_'+row[1].strftime("%x")] = (row[3])
        dir['USD_'+row[1].strftime("%x")] = 1
    return dir


def Cal_Index(D_Index,D_Data,D_ISIN,D_Date,D_RIC_ISIN,last_Period):
    Index_List = list()
    Constituents_List = list()
    for period in D_Data:
        Index_Currency = D_Index["Currency"]
        format_str = '%m/%d/%Y'
        S_Date = datetime.datetime.strptime(D_Date[period+"_START"], format_str).date()- datetime.timedelta(days=0)
        if S_Date.weekday()==5:
            S_Date = S_Date - datetime.timedelta(days=1)
        S_Date_Minus_Five = datetime.datetime.strptime(D_Date[period+"_START"], format_str).date()- datetime.timedelta(days=5)
        E_Date = datetime.datetime.strptime(D_Date[period+"_END"], format_str).date()- datetime.timedelta(days=0)
       
        i=0

        D_Index["M_Cap_PR"],D_Index["M_Cap_TR"],D_Index["M_Cap_NTR"]=D_Index["MV"],D_Index["MV"],D_Index["MV"]
        D_Index["Index_Value_PR"], D_Index["Index_Value_TR"],D_Index["Index_Value_NTR"]= D_Index["IV"],D_Index["IV"],D_Index["IV"]
        Divisor = D_Index["MV"]/D_Index["IV"]
        D_Index["Divisor_PR"], D_Index["Divisor_TR"],D_Index["Divisor_NTR"]=Divisor,Divisor,Divisor
       
        D_Price,D_LastDate,currency_list,D_ISIN_Currency = Get_PRICE(D_ISIN[period],S_Date_Minus_Five.strftime("%x"),E_Date.strftime("%x"),D_Index["Identifier"])
        Set_TR_Price(D_Date,D_RIC_ISIN,last_Period,D_Price)
        currency_list.append(Index_Currency)
        Ex_Rate = Get_Currency(currency_list,S_Date_Minus_Five.strftime("%x"),E_Date.strftime("%x"))
        Tax_Rate = Get_TAX()
        D_CA = Get_CA(D_ISIN[period],S_Date.strftime("%x"),E_Date.strftime("%x"),D_Index["Identifier"])
        
        Latest_Price={}
        Latest_Ex_Rate={}

        while S_Date_Minus_Five <= E_Date:
            f_c.Set_Latest_Ex_Rate(Index_Currency,D_Data[period],Ex_Rate,Latest_Ex_Rate,S_Date_Minus_Five.strftime("%x"),D_ISIN_Currency)
            f_c.Set_Latest_Price(D_Data[period],D_Price,Latest_Price,S_Date_Minus_Five.strftime("%x"))
            if S_Date_Minus_Five>=S_Date:
                if i==0:
                    f_c.Cal_Shares(D_Index,D_Data[period],Latest_Price,Latest_Ex_Rate,S_Date_Minus_Five.strftime("%x"),Constituents_List,period,Tax_Rate,D_ISIN_Currency)
                else:
                    print_flag = GetFlag(D_Index["DCFO"],S_Date_Minus_Five.strftime("%x"),D_Date[period+'_END'])
                    M_Cap = f_c.Cal_Index_Close(D_Index,D_Data[period],Latest_Price,Latest_Ex_Rate,S_Date_Minus_Five.strftime("%x"),Constituents_List,period,Tax_Rate,D_ISIN_Currency,print_flag)
                f_c.Fill_Index_Report_Data(D_Index,Index_List,period,S_Date_Minus_Five)
                i += 1
                
            if S_Date_Minus_Five.weekday()==4:
                S_Date_Minus_Five = S_Date_Minus_Five + datetime.timedelta(days=3)
            else:
                S_Date_Minus_Five = S_Date_Minus_Five + datetime.timedelta(days=1)
            if S_Date_Minus_Five>S_Date and i!=0:
                f_c.Delist(D_Data[period],S_Date_Minus_Five.strftime("%x"),D_LastDate,E_Date.strftime("%x"))
                f_c.Cal_Index_Open(D_Index,D_Data[period],Latest_Price,Latest_Ex_Rate,S_Date_Minus_Five.strftime("%x"),Tax_Rate,D_ISIN_Currency,Ex_Rate,D_CA)
    files = f_c.Print_Reports(Index_List,Constituents_List)
    return files


def GetFlag(option,date,date_end):
    if option =="ND":
        return 0
    elif option =="CD":
        return 1
    elif option =="EDD":
        format_str = '%m/%d/%Y'
        endDate = datetime.datetime.strptime(date_end, format_str).date()

        if endDate.strftime("%x") ==date:
            return 1
        else :
            return 0


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


def Rerun_Dbdata(D_Index, start_date, end_date, period, get_composition):
    D_Data ={}
    D_ISIN ={}
    D_Date ={}
    data = []
    start_date = start_date.strftime('%m/%d/%Y')
    end_date = end_date.strftime('%m/%d/%Y')
    st_date = str(period)+"_START"
    en_date = str(period)+"_END"
    D_Date[st_date] =start_date
    D_Date[en_date] =end_date
    for data_composition in get_composition:
        weights = data_composition.weights
        weights = str(weights)+'%'
        comp_data = []
        comp_isin =[]
        comp_data.append(period)
        comp_data.append(data_composition.isin)
        comp_data.append(weights)
        comp_data.append(start_date)
        comp_data.append(end_date)
        comp_data.append(data_composition.country)
        comp_data.append(data_composition.ric)
        comp_isin.append(data_composition.isin)
    data.append(comp_data)
    D_Data[str(period)] = data
    D_ISIN [str(period)] = comp_isin
    D_RIC_ISIN ={}
    save_file = Cal_Index(D_Index, D_Data, D_ISIN, D_Date, D_RIC_ISIN, period)
    return save_file

def DateTime(current_time):
    date_time = datetime.datetime.strptime(current_time, "%m/%d/%Y")
    cr_date = date_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    return cr_date

def check_ric(ric_data):
    ric_active_data= {}
    connection = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER=3.7.99.191;DATABASE=TR_Datafeeds;UID=sa;PWD=Indxx@1234')
    cursor = connection.cursor()
    Query= Q.Query_TR_Equity(ric_data)
    cursor.execute(Query)
    for row in cursor:
        if row[1]:
            ric_active_data[row[0]] = row[1]
        else:
            msg = "Please check input file and add an active RIC value."
            return msg

def getList(dict):
    list_keys = []
    for key in dict.keys():
        list_keys.append(key)
    str1 = "', '".join(list_keys)
    str1 = "'"+str1+"'"
    return str1

def check_date_formate(date):
    date = date.split('-')
    date = date[0] +'/'+date[1]+'/'+date[2]
    return date

def column_validation_check(df):
    column_list = ['Period', 'ISIN', 'Weights', 'Start date', 'End date', 'Country', 'RIC']
    for col in column_list:
        if col not in df.columns:
            return False
    return True