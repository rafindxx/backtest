import pyodbc
import csv 
import datetime
import Query as Q
import pyodbc as ms

def Validate_Columns_Order(line):
    csvColStr = line[0]+'_'+line[1]+'_'+line[2]+'_'+line[3].replace(' ','')+'_'+line[4].replace(' ','')+'_'+line[5]+'_'+line[6]
    print(csvColStr)
    validColStr="Period_ISIN_Weights_Startdate_Enddate_Country_RIC"

    if csvColStr!=validColStr:
        return 1
    else:
        return 0

def Validate_Data(line,D_Date,last_Period):
    errorMessage = ""
    
    if line[0] in (None, "") or line[1] in (None, "") or line[2] in (None, "") or line[3] in (None, "") or line[4] in (None, "") or line[5] in (None, ""):
        errorMessage =  "Please check your portfolio.Few Securities does not have proper period, proper ISIN, proper weight , proper Start Date and End Date or proper country."
    else:                
        startDate= line[3]
        endDate  = line[4]
        period = line[0]        
        if (period+'_START' in D_Date and D_Date[period+'_START']!= startDate) or (period+'_END' in D_Date and D_Date[period+'_END']!= endDate) :
            errorMessage =  "Please check your portfolio.Start date and End date for all the securities of same perioed should be same."
        if last_Period != period and (str(last_Period)+'_END' in D_Date and D_Date[str(last_Period)+'_END']!= startDate):
            errorMessage =  "Please check your portfolio.Start date of a period should be equal to end date of previous period."
    return errorMessage

    
def Validate_Read_CSV(file_Name,cur,IDentifier):
    d1 = {}
    d2 = {}
    D_Data= {}
    D_Date = {}
    D_ISIN = {}
    D_RIC_ISIN = {}
    last_Period = 1
    errorMessage = ""
    warningMessage = ""
    i = 0
    with open(file_Name,'r') as csvfile:
        csvreader = csv.reader(csvfile)
        #next(csvreader, None)
       
        for line in csvreader:
            line[3] = line[3].replace('-','/')
            line[4] = line[4].replace('-','/')
            if i==0 :
                if bool(Validate_Columns_Order(line)):
                    return "Please check your portfolio.Columns should be in order (Period, ISIN, Weights, Start date, End date, Country, RIC).","",D_Data,D_Date,D_ISIN,last_Period,D_RIC_ISIN
            #print(line)
            else:
                strMessage = Validate_Data(line,D_Date,last_Period)
                if strMessage not in (None, ""):
                    return strMessage,"",D_Data,D_Date,D_ISIN,last_Period,D_RIC_ISIN
                else:
                    last_Period = line[0]
                    Load_Data(line,d1,d2,D_Data,D_Date,D_ISIN)
            i += 1
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
        #yesterday = datetime.datetime.now()+ datetime.timedelta(days=17)
        yesterday = datetime.datetime.now()- datetime.timedelta(days=1)
        yesterday_date = yesterday.strftime("%x")
        #print(yesterday_date)

        format_str = '%m/%d/%Y'
        Last_Period_End_Date = datetime.datetime.strptime(D_Date[last_Period+'_END'], format_str).date()
        
        #print(S_Date.strftime("%x"))
        if yesterday_date == Last_Period_End_Date.strftime("%x"):
            #print("RIC CHECKING")
            #print(last_Period)
            for line in D_Data[last_Period]:
                if line[6] in (None, "") :
                    return "Please check your portfolio.Few Securities in last period does not have proper RIC.","",D_Data,D_Date,D_ISIN,last_Period
                else:
                     D_RIC_ISIN[line[6]]=line[1]
                    
        if errorMessage not in (None, ""):
            errorMessage = "Please check your portfolio."+errorMessage
        
    #print(last_Period)                
    return errorMessage,warningMessage,D_Data,D_Date,D_ISIN,last_Period,D_RIC_ISIN

def Set_TR_Price(D_Date,D_RIC_ISIN,last_Period,D_Price):
    yesterday = datetime.datetime.now()- datetime.timedelta(days=1)
    yesterday_date = yesterday.strftime("%x")
    #print(yesterday_date)

    format_str = '%m/%d/%Y'
    E_Date = datetime.datetime.strptime(D_Date[last_Period+'_END'], format_str).date()
    E_Date = E_Date.strftime("%x")
    if yesterday_date == E_Date:
        #print("TR Price Update")
        TR_Price = Get_TR_PRICE(getList(D_RIC_ISIN),E_Date)
        for ric in D_RIC_ISIN:
            var1 = ric+'_'+date
            var2 = D_RIC_ISIN[ric]+'_'+date        
            if var1 in TR_Price:            
                trPrice = TR_Price[var1]
                if var2 not in D_Price:
                    D_Price[var2] = trPrice
        
def  Load_Data(line,d1,d2,D_Data,D_Date,D_ISIN):
    #.replace(' ','')
    
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
    
def Delisting_Check(cur,ISIN_LIST,E_DATE,IDentifier):
    #print("inside Delisting_Check")
    #date_str = '29/12/2017' # The date - 29 Dec 2017
    isins = str(ISIN_LIST)[1:-1]
    delistedISINs=""
    format_str = '%m/%d/%Y' # The format
    datetime_obj = datetime.datetime.strptime(E_DATE, format_str)
    #print(datetime_obj.date())#- datetime.timedelta(days=5)
    S_DATE = str(datetime_obj.date()- datetime.timedelta(days=5))
    #print("Delisting")
    #print(S_DATE)
    #Query= "select  b.isin,a.p_date as date,a.p_price,a.currency from fp_v2.fp_basic_prices a inner join sym_v1.sym_coverage c on a.fsym_id=c.fsym_regional_id inner join sym_v1.sym_isin b on c.fsym_id=b.fsym_id WHERE b.isin in  ("+isins +")AND  a.p_date between '"+S_DATE+"' and '"+E_DATE+"'	ORDER BY b.isin, a.p_date"
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

def Get_TAX(cur):	
    cur.execute('SELECT * from FDS_DataFeeds.dbo.tax_rate ')
    dir = {}
    for row in cur:
        dir[row[1]] = float(row[2].strip()[0:-1])# row[2].strip()
    return dir

def Get_CA(cur,ISIN_LIST,S_DATE,E_DATE,IDentifier):
    #print("inside Get_CA")
    isins = str(ISIN_LIST)[1:-1]
    D_CA ={}
    D_CA_Dividend = {}
    D_CA_S_Dividend = {}
    D_CA_Spin = {}
    D_CA_Split ={}
    Query= Q.Query_Divident(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        #print(row)#
        var = row[0]+'_'+row[5].strftime("%x")
        if var not in D_CA_Dividend:
            D_CA_Dividend[var] = list()
        D_CA_Dividend[var].append(row)
    D_CA["Dividend"] = D_CA_Dividend

    Query= Q.Query_Special_Divident(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        #print(row)#
        var = row[0]+'_'+row[5].strftime("%x")
        if var not in D_CA_S_Dividend:
            D_CA_S_Dividend[var] = list()
        D_CA_S_Dividend[var].append(row)
    D_CA["SDividend"] = D_CA_S_Dividend

    Query= Q.Query_Spin(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        #print(row)#
        var = row[0]+'_'+row[5].strftime("%x")
        if var not in D_CA_Spin:
            D_CA_Spin[var] = list()
        D_CA_Spin[var].append(row)
    D_CA["Spin"] = D_CA_Spin
    
    Query= Q.Query_Split(IDentifier,isins,S_DATE,E_DATE)
    cur.execute(Query)
    for row in cur:
        #print(row)
        var = row[0]+'_'+row[1].strftime("%x")
        if var not in D_CA_Split:
            D_CA_Split[var] = list()
        D_CA_Split[var].append(row)
    D_CA["Split"] = D_CA_Split
    
    return D_CA

def getList(dict): 
    list1 = [] 
    for key in dict.keys(): 
        list1.append(key)      
    return list1 
def Get_PRICE(cur,ISIN_LIST,S_DATE,E_DATE,IDentifier):
    #print("inside get price")
    isins = str(ISIN_LIST)[1:-1]
    
    '''format_str = '%m/%d/%Y'
    datetime_obj = datetime.datetime.strptime(S_DATE, format_str)
    START_DATE = str(datetime_obj.date()- datetime.timedelta(days=5))'''
    #Query= "select  b.isin,a.p_date as date,a.p_price,a.currency from fp_v2.fp_basic_prices a inner join sym_v1.sym_coverage c on a.fsym_id=c.fsym_regional_id inner join sym_v1.sym_isin b on c.fsym_id=b.fsym_id WHERE b.isin in  ("+isins +")AND  a.p_date between '"+START_DATE+"' and '"+E_DATE+"' ORDER BY b.isin, a.p_date asc"
    Query= Q.Query_Price(IDentifier,isins,S_DATE,E_DATE)
    currency_list = []
    cur.execute(Query)
    D_Price = {}
    D_ISIN_Currency ={}
    D_LastDate = {}
    for row in cur:
        #print(row)
        D_Price[row[0]+'_'+row[1].strftime("%x")] = row[2]
        D_ISIN_Currency[row[0]] = row[3]
        D_LastDate[row[0]] = row[1].strftime("%x")
        if row[3] not in currency_list: 
            currency_list.append(row[3])
        #print(currency_list)
    #currency_list.append(Index_Currency)
    #ex_Rate = Get_Currency(cursor1,currency_list,S_DATE,E_Date)
    return D_Price,D_LastDate,currency_list,D_ISIN_Currency

def Get_TR_PRICE(RIC_LIST,DATE):
    connection = ms.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER=65.0.33.214;DATABASE=FDS_Datafeeds;UID=sa;PWD=Indxx@1234')
    cursor = connection.cursor()
    #print("inside get price")
    rics = str(RIC_LIST)[1:-1]
    
    '''format_str = '%m/%d/%Y'
    datetime_obj = datetime.datetime.strptime(S_DATE, format_str)
    START_DATE = str(datetime_obj.date()- datetime.timedelta(days=5))'''
    #Query= "select  b.isin,a.p_date as date,a.p_price,a.currency from fp_v2.fp_basic_prices a inner join sym_v1.sym_coverage c on a.fsym_id=c.fsym_regional_id inner join sym_v1.sym_isin b on c.fsym_id=b.fsym_id WHERE b.isin in  ("+isins +")AND  a.p_date between '"+START_DATE+"' and '"+E_DATE+"' ORDER BY b.isin, a.p_date asc"
    Query= Q.Query_TR_Price(RIC_LIST,DATE)
    cursor.execute(Query)
    D_TR_Price = {}
    for row in cursor:
        #print(row)
        D_TR_Price[row[0]+'_'+row[1].strftime("%x")] = row[2]
    cursor.close()
    connection.close()
    return D_TR_Price

def Get_Currency(cur,C_list,S_DATE,E_DATE):
    clist = str(C_list)[1:-1]
    #format_str = '%m/%d/%Y'
    #datetime_obj = datetime.datetime.strptime(S_DATE, format_str)
    #START_DATE = str(datetime_obj.date()- datetime.timedelta(days=5))
    Query="SELECT RTS.iso_currency, RTS.date, RTS.exch_rate_usd, RTS.exch_rate_per_usd FROM FDS_DataFeeds.ref_v2.fx_rates_usd AS RTS WHERE RTS.date between '"+S_DATE+"' and '"+E_DATE+"' and RTS.iso_currency in ("+clist +") ORDER BY RTS.date"
    #print("Currency Query : "+Query)
    cur.execute(Query)
    dir = {}
    for row in cur:
        dir[row[0]+'_'+row[1].strftime("%x")] = (row[3])
        dir['USD_'+row[1].strftime("%x")] = 1
    return dir


