
import Functions as f
import pyodbc as ms
import Functions_Cal as f_c
from itertools import chain
import datetime

# csv fileused id Geeks.csv
filename="C://Backtest//BacktestInput.csv"

#filename="C://Backtest//BacktestInputFYSMID.csv"
#print(filename)
conn1 = ms.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER=204.80.90.133;DATABASE=FDS_Datafeeds;UID=sa;PWD=f0r3z@786')
cursor1 = conn1.cursor()

Error,Warning,D_Data,D_Date,D_ISIN,last_Period = f.Validate_Read_CSV(filename,cursor1,"ISIN")

def Adjust_Dividend(D_Index,divLits,cRow,Tax_Rate,D_ISIN_Currency,Ex_Rate,date,Latest_Price):
    isin = cRow[1]
    country = cRow[5]
    countryTax = Tax_Rate[country]/100
    toCurrency = D_ISIN_Currency[isin];
    adjustmentFactor_PR,adjustmentFactor_TR,adjustmentFactor_NTR = 1
    for row in divLits:
        fromCurrency = row[3]
        exRate = Get_Ex_Rate(fromCurrency,toCurrency,Ex_Rate,date)
        amount = row[1]
        amount_Tax = amount*(1-countryTax)
        amount_PR  = amount*exRate
        amount_TR  = amount*exRate
        amount_NTR  = amount_Tax*exRate

        adjustmentFactor_PR =  adjustmentFactor_PR(1 - (amount_PR/Latest_Price[isin]))
        adjustmentFactor_TR =  adjustmentFactor_TR(1 - (amount_TR/Latest_Price[isin]))
        adjustmentFactor_NTR =  adjustmentFactor_NTR(1 - (amount_NTR/Latest_Price[isin]))

        #if D_Index["Adjustment"] ==


def Adjust_CA(D_Index,Clist,Latest_Price,Latest_Ex_Rate,date,Constituents_List_Final,period,Tax_Rate,D_ISIN_Currency,Ex_Rate):
    Constituents_List = list()
    M_CAP_PR,M_CAP_TR,M_CAP_NTR = 0,0,0
    Index_Value_PR,Index_Value_TR,Index_Value_NTR = 0,0,0
    Divisor_PR = D_Index["M_Cap_PR"]/D_Index["Index_Value_PR"]
    Divisor_TR = D_Index["M_Cap_TR"]/D_Index["Index_Value_TR"]
    Divisor_NTR = D_Index["M_Cap_NTR"]/D_Index["Index_Value_NTR"]
    #print(list)
    for row in Clist:
        Fill_Constituents_List(D_Index,Constituents_List,row,period,date,D_ISIN_Currency,Tax_Rate,Latest_Price,Latest_Ex_Rate)
        M_CAP_PR += row[7]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]
        M_CAP_TR += row[8]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]
        M_CAP_NTR += row[9]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]

    Index_Value_PR = M_CAP_PR/Divisor_PR
    Index_Value_TR = M_CAP_PR/Divisor_TR
    Index_Value_NTR = M_CAP_PR/Divisor_NTR
    D_Index["M_Cap_PR"]=M_CAP_PR
    D_Index["M_Cap_TR"]=M_CAP_TR
    D_Index["M_Cap_NTR"]=M_CAP_NTR
    D_Index["Index_Value_PR"] = Index_Value_PR
    D_Index["Index_Value_TR"] = Index_Value_TR
    D_Index["Index_Value_NTR"] = Index_Value_NTR
    #D_Index["Divisor_PR"]=M_CAP_PR/Index_Value_PR
    #D_Index["Divisor_TR"]=M_CAP_TR/Index_Value_TR
    #D_Index["Divisor_NTR"]=M_CAP_NTR/Index_Value_NTR

    for row in Constituents_List:
        row[2] = D_Index["Index_Value_PR"]
        row[3] = D_Index["M_Cap_PR"]
        row[4] = D_Index["Divisor_PR"]
        row[5] = D_Index["Index_Value_TR"]
        row[6] = D_Index["M_Cap_TR"]
        row[7] = D_Index["Divisor_TR"]
        row[8] = D_Index["Index_Value_NTR"]
        row[9] = D_Index["M_Cap_NTR"]
        row[10] = D_Index["Divisor_NTR"]
    Constituents_List_Final.extend(Constituents_List)

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

        D_Price,D_LastDate,currency_list,D_ISIN_Currency = f.Get_PRICE(cursor1,D_ISIN[period],S_Date_Minus_Five.strftime("%x"),E_Date.strftime("%x"),D_Index["Identifier"])
        currency_list.append(Index_Currency)
        Ex_Rate = f.Get_Currency(cursor1,currency_list,S_Date_Minus_Five.strftime("%x"),E_Date.strftime("%x"))
        Tax_Rate = f.Get_TAX(cursor1)
        #D_CA = f.Get_CA(cursor1,D_ISIN[period],S_Date.strftime("%x"),E_Date.strftime("%x"),D_Index["Identifier"])
        #print(D_CA)

        Latest_Price={}
        Latest_Ex_Rate={}

        while S_Date_Minus_Five <= E_Date:
            # print(D_Price)
            # print(Ex_Rate)
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
            #    f_c.Adjust_CA(D_Index,D_Data[period],Latest_Price,Latest_Ex_Rate,S_Date.strftime("%x"),D_ISIN_Currency,D_CA,Ex_Rate)
    f_c.Print_Reports(Index_List,Constituents_List)

D_Index = {}
D_Index["Identifier"] = "ISIN"
D_Index["IV"] = 1000
D_Index["MV"] = 100000
D_Index["Currency"] = "EUR"
D_Index["Adjustment"] = "DA"#"SA"
D_Index["DCFO"] = "ND"#"CD","EDD"

Cal_Index(D_Index,D_Data,D_ISIN,D_Date)

cursor1.close()
conn1.close()

