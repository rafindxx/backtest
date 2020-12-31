import pyodbc
import csv
from itertools import chain
import random

def Print_Reports(Index_List,Constituents_List):
    random_name = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
    outFileName1="./static/backtest-file/output/"+random_name+"_index_value_file.csv"
    outFileName2="./static/backtest-file/output/"+random_name+"_constituents_file.csv"
    with open(outFileName1, 'w', newline='') as csvfile:
        writer1 = csv.writer(csvfile)
        writer1.writerow(["S.No","Date","Index Value PR","Index Value TR","Index Value NTR"])
        writer1.writerows(Index_List)
    with open(outFileName2, 'w', newline='') as csvfile:
        writer2 = csv.writer(csvfile)
        #writer2.writerow(["S.No","Date","Index Value PR","Index Value TR","Index Value NTR"])
        writer2.writerow(["S.No","Date","Index Value PR","Market CAP PR","Divisor PR","Index Value TR","Market CAP TR","Divisor TR","Index Value NTR","Market CAP NTR","Divisor NTR","ISIN","Currency","Country","TAX","Share PR","Share TR","Share NTR","Local Price","Index PRICE","MCAP PR","MCAP TR","MCAP NTR","Currency Price","Price Date","Weight PR","Weight TR","Weight NTR","Dividend","Special Dividend","Split","Spin"])
        writer2.writerows(Constituents_List)
    file_names = {'index_value_file':outFileName1,'constituents_file':outFileName2}
    return file_names

def Fill_Constituents_List(D_Index,Constituents_List,row,period,date,D_ISIN_Currency,Tax_Rate,Latest_Price,Latest_Ex_Rate):
    Constituents_Row = []
    Constituents_Row.append(period)
    Constituents_Row.append(date)
    Fill_Index_Value(D_Index,Constituents_Row)
    Constituents_Row.append(row[1])
    Constituents_Row.append(D_ISIN_Currency[row[1]])
    Constituents_Row.append(row[5])
    Constituents_Row.append(Tax_Rate[row[5]])
    Constituents_Row.append(row[7])
    Constituents_Row.append(row[8])
    Constituents_Row.append(row[9])
    Constituents_Row.append(Latest_Price[row[1]][0])
    Constituents_Row.append(Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])

    Constituents_Row.append(row[7]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])
    Constituents_Row.append(row[8]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])
    Constituents_Row.append(row[9]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])

    Constituents_Row.append(Latest_Ex_Rate[row[1]])
    Constituents_Row.append(Latest_Price[row[1]][1])

    Constituents_Row.append(row[10])
    Constituents_Row.append(row[11])
    Constituents_Row.append(row[12])
    Constituents_List.append(Constituents_Row)

def Cal_Index_Close(D_Index,Clist,Latest_Price,Latest_Ex_Rate,date,Constituents_List_Final,period,Tax_Rate,D_ISIN_Currency):
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
def Cal_Shares(D_Index,list,Latest_Price,Latest_Ex_Rate,date,Constituents_List,period,Tax_Rate,D_ISIN_Currency):
    #print("inside calshares"+ date)
    #ISIN,Currency,Country,TAX,Share PR,Share TR,Share NTR,Local Price,USD PRICE,MCAP PR,MCAP TR,MCAP NTR,Currency Price,Price Date,Weight PR,Weight TR,Weight NTR,Dividend,Special Dividend,Split,Spin

    # print(Latest_Price)
    # print(Latest_Ex_Rate)
    #print(D_Price)
    M_Cap = D_Index["MV"]
    ISIN_Shares = {}
    for row in list:
        weight = float(row[2][0:-1])
        shares = (weight*M_Cap)/(100*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])
        row.append(shares)
        row.append(shares)
        row.append(shares)
        row.append(weight)
        row.append(weight)
        row.append(weight)
        Fill_Constituents_List(D_Index,Constituents_List,row,period,date,D_ISIN_Currency,Tax_Rate,Latest_Price,Latest_Ex_Rate)


def Adjust_CA(D_Index,list,Latest_Price,Latest_Ex_Rate,date,D_ISIN_Currency,D_CA):
    print("inside CA")

def Fill_Index_Value(D_Index,Constituents_Row):
    #Index Value PR,Market CAP PR,Divisor PR,Index Value TR,Market CAP TR,Divisor TR,Index Value NTR,Market CAP NTR,Divisor NTR,
    Constituents_Row.append(D_Index["Index_Value_PR"])
    Constituents_Row.append(D_Index["M_Cap_PR"])
    Constituents_Row.append(D_Index["Divisor_PR"])
    Constituents_Row.append(D_Index["Index_Value_TR"])
    Constituents_Row.append(D_Index["M_Cap_TR"])
    Constituents_Row.append(D_Index["Divisor_TR"])
    Constituents_Row.append(D_Index["Index_Value_NTR"])
    Constituents_Row.append(D_Index["M_Cap_NTR"])
    Constituents_Row.append(D_Index["Divisor_NTR"])

def Fill_Index_Report_Data(D_Index,Index_List,period,S_Date):
   row = []
   row.append(period)
   row.append(str(S_Date))
   row.append(D_Index["Index_Value_PR"])
   row.append(D_Index["Index_Value_TR"])
   row.append(D_Index["Index_Value_NTR"])
   Index_List.append(row)

def Set_Latest_Price(list,D_Price,Latest_Price,date):
    # print("inside Latest Price" + date)
    for row in list:
        var1 = row[1]+'_'+date

        if var1 in D_Price:
            price = D_Price[var1]
            Row = []
            Row.append(price)
            Row.append(date)
            Latest_Price[row[1]] = Row
def Get_Price(ISIN,D_Price,date,Latest_Price):
    # print("inside Get_Price" + date)
    var1 = ISIN+'_'+date

    if var1 in D_Price:
        price = D_Price[var1]
        return price
    else:
        return Latest_Price[ISIN][0]

def Get_Ex_Rate(fromCurrency,toCurrency,Ex_Rate,date):
    # print("inside Get_Ex_Rate" + date)
    var1 = fromCurrency +'_'+date
    if var1 in Ex_Rate:
        fromRate = (Ex_Rate[var1])
        toRate = (Ex_Rate[toCurrency+'_'+date])
        ex_Rate = toRate/fromRate
    else:
        return 1

def Set_Latest_Ex_Rate(Index_Currency,list,Ex_Rate,Latest_Ex_Rate,date,D_ISIN_Currency):
    # print("inside Set_Latest_Ex_Rate" + date)
    #print(Ex_Rate)
    for row in list:

        fromCurrency = D_ISIN_Currency[row[1]]
        var2 = fromCurrency +'_'+date
        # print(var2)

        if var2 in Ex_Rate:
            fromRate = (Ex_Rate[fromCurrency+'_'+date])
            toRate = (Ex_Rate[Index_Currency+'_'+date])
            ex_Rate = toRate/fromRate
            Latest_Ex_Rate[row[1]] = ex_Rate


