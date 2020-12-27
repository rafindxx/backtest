import pyodbc
import csv
import datetime
import calculation.Query as Q
import random

def Validate_Read_CSV(file_Name,IDentifier):
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
            delistedISINs = Delisting_Check(cur,isins,startDate,IDentifier)
            if delistedISINs not in (None, ""):
                errorMessage += "Securities " + delistedISINs +" of period - "+key+" is not trading start at the start of the period . "
        '''Check for Warning '''
        for key in d2:
             if d2[key]>45:
                 warningMessage +="Sum of weights of securities for period " + key +" with greater than 5% weight is  " + str(d2[key])+"."
        if errorMessage not in (None, ""):
            errorMessage = "Please check your portfolio."+errorMessage
    #print(last_Period)
    final_data = {'error':errorMessage, 'warning':warningMessage, 'D_Data':D_Data, 'D_Date':D_Date, 'D_ISIN':D_ISIN, 'last_Period': last_Period}
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
    #date_str = '29/12/2017' # The date - 29 Dec 2017
    isins = str(ISIN_LIST)[1:-1]
    delistedISINs=""
    format_str = '%m/%d/%Y' # The format
    datetime_obj = datetime.datetime.strptime(E_DATE, format_str)
    #print(datetime_obj.date())#- datetime.timedelta(days=5)
    S_DATE = str(datetime_obj.date()- datetime.timedelta(days=5))
    #print(S_DATE)
    #Query= "select  b.isin,a.p_date as date,a.p_price,a.currency from fp_v2.fp_basic_prices a inner join sym_v1.sym_coverage c on a.fsym_id=c.fsym_regional_id inner join sym_v1.sym_isin b on c.fsym_id=b.fsym_id WHERE b.isin in  ("+isins +")AND  a.p_date between '"+S_DATE+"' and '"+E_DATE+"'    ORDER BY b.isin, a.p_date"
    Query= Q.Query_Price(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    dir1 = {}
    delistedISINs
    for row in cur:
        #print(row)
        dir1[row[0]] = row[2]
    for ISIN in ISIN_LIST:
        if ISIN not in dir1:
            delistedISINs += ISIN +","
    return delistedISINs

def handle_uploaded_file(file):
    if file:
        random_id = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
        file_name = random_id+'-'+file.name
        with open('./backtest-file/input/'+file_name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return file_name

def remove_percent_symbole(weight):
    weight = list(weight)
    weight =  weight[:-1]
    weight = ''.join([str(elem) for elem in weight])
    return weight

