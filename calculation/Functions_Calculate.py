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

def Adjust_Dividend(divList,isinRow,Tax_Rate,D_ISIN_Currency,Ex_Rate,date,Latest_Price):
    isin = isinRow[1]
    country = isinRow[5]
    countryTax = Tax_Rate[country]/100
    toCurrency = D_ISIN_Currency[isin];
    aFactor_PR,aFactor_TR,aFactor_NTR = 1,1,1
    Dividend,sDividend,Spin = 0,0,0
    for row in divList:
        fromCurrency = row[3]
        div_code = row[4]
        spin_off_flag = row[2]
        if spin_off_flag ==1:
            Spin = div_code

        exRate = Get_Ex_Rate(fromCurrency,toCurrency,Ex_Rate,date)
        amount = row[1]
        amount_Tax = amount*(1-countryTax)
        if div_code in (11,134):
            sDividend = div_code
            amount_PR  = amount*exRate
        else:
            amount_PR=0
            Dividend = div_code

        amount_TR  = amount*exRate
        amount_NTR  = amount_Tax*exRate

        aFactor_PR =  aFactor_PR*(1 - (amount_PR/Latest_Price[isin][0]))
        aFactor_TR =  aFactor_TR*(1 - (amount_TR/Latest_Price[isin][0]))
        aFactor_NTR =  aFactor_NTR*(1 - (amount_NTR/Latest_Price[isin][0]))
    return aFactor_PR,aFactor_TR,aFactor_NTR,Dividend,sDividend,Spin

def Adjust_Split(splitList):
    sFactor_PR,sFactor_TR,sFactor_NTR = 1,1,1
    for row in splitList:
        sFactor_PR =  1/row[2]
        sFactor_TR =  1/row[2]
        sFactor_NTR =  1/row[2]
    return sFactor_PR,sFactor_TR,sFactor_NTR,row[2]

def Adjust_CA(D_Index,D_CA,isin_Data_Row,date,Tax_Rate,D_ISIN_Currency,Ex_Rate,Latest_Price):
    #adjustmentFactor_PR,adjustmentFactor_TR,adjustmentFactor_NTR = 1,1,1
    dFactorPR,dFactorTR,dFactorNTR =1,1,1
    sFactorPR,sFactorTR,sFactorNTR = 1,1,1
    Dividend,sDividend,Spin,Split = 0,0,0,0
    var = isin_Data_Row[1]+'_'+date
    dFactorPR,dFactorTR,dFactorNTR = 1,1,1
    sFactorPR,sFactorTR,sFactorNTR = 1,1,1
    if var in D_CA["Dividend"]:
        div_list = D_CA["Dividend"][var]
        dFactorPR,dFactorTR,dFactorNTR,Dividend,sDividend,Spin = Adjust_Dividend(div_list,isin_Data_Row,Tax_Rate,D_ISIN_Currency,Ex_Rate,date,Latest_Price)
    if var in D_CA["Split"]:
        split_list = D_CA["Split"][var]
        sFactorPR,sFactorTR,sFactorNTR,Split = Adjust_Split(split_list)

    return dFactorPR*sFactorPR,dFactorTR*sFactorTR,dFactorNTR*sFactorNTR,10,sDividend,Spin,Split

def Delist(Clist,date,D_LastDate):
    for row in Clist:
        if D_LastDate[row[1]] == date:
            Clist.remove(row)

def Cal_Index_Open(D_Index,Clist,Latest_Price,Latest_Ex_Rate,date,Tax_Rate,D_ISIN_Currency,Ex_Rate,D_CA):
    Constituents_List = list()
    M_CAP_PR,M_CAP_TR,M_CAP_NTR = 0,0,0
    Dividend,sDividend,Spin,Split = 0,0,0,0
    Index_Value_PR,Index_Value_TR,Index_Value_NTR = D_Index["Index_Value_PR"],D_Index["Index_Value_TR"],D_Index["Index_Value_NTR"]
    for row in Clist:
        adjustmentFactor_PR,adjustmentFactor_TR,adjustmentFactor_NTR,Dividend,sDividend,Spin,Split =Adjust_CA(D_Index,D_CA,row,date,Tax_Rate,D_ISIN_Currency,Ex_Rate,Latest_Price)

        Adjusted_Price_PR = Latest_Price[row[1]][0]*adjustmentFactor_PR
        Adjusted_Price_TR = Latest_Price[row[1]][0]*adjustmentFactor_TR
        Adjusted_Price_NTR = Latest_Price[row[1]][0]*adjustmentFactor_NTR
        if D_Index["Adjustment"] =="SA":
            shares_PR = row[7]/adjustmentFactor_PR
            shares_TR = row[8]/adjustmentFactor_TR
            shares_NTR = row[9]/adjustmentFactor_NTR
            row[7] = shares_PR
            row[8] = shares_TR
            row[9] = shares_NTR

        M_CAP_PR += row[7]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]
        M_CAP_TR += row[8]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]
        M_CAP_NTR += row[9]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]

        row[13] = row[7]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]
        row[14] = row[8]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]
        row[15] = row[9]*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]]
        #print("------------------------------------------------")
        #print(row)
        row[16] = Dividend
        row[17] = sDividend
        row[18] = Spin
        row[19] = Split


    D_Index["M_Cap_PR"]=M_CAP_PR
    D_Index["M_Cap_TR"]=M_CAP_TR
    D_Index["M_Cap_NTR"]=M_CAP_NTR

    D_Index["Divisor_PR"]=M_CAP_PR/D_Index["Index_Value_PR"]
    D_Index["Divisor_TR"]=M_CAP_TR/D_Index["Index_Value_TR"]
    D_Index["Divisor_NTR"]=M_CAP_NTR/D_Index["Index_Value_NTR"]

    for row in Clist:
        row[10] = (row[13]*100)/D_Index["M_Cap_PR"]
        row[11] = (row[14]*100)/D_Index["M_Cap_PR"]
        row[12] = (row[15]*100)/D_Index["M_Cap_PR"]

def Cal_Index_Close(D_Index,Clist,Latest_Price,Latest_Ex_Rate,date,Constituents_List_Final,period,Tax_Rate,D_ISIN_Currency,print_flag):
    Constituents_List = list()
    M_CAP_PR,M_CAP_TR,M_CAP_NTR = 0,0,0
    Index_Value_PR,Index_Value_TR,Index_Value_NTR = 0,0,0
    Divisor_PR = D_Index["M_Cap_PR"]/D_Index["Index_Value_PR"]
    Divisor_TR = D_Index["M_Cap_TR"]/D_Index["Index_Value_TR"]
    Divisor_NTR = D_Index["M_Cap_NTR"]/D_Index["Index_Value_NTR"]
    #print(list)
    for row in Clist:
        if print_flag==1:
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
        row.append(shares*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])
        row.append(shares*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])
        row.append(shares*Latest_Price[row[1]][0]*Latest_Ex_Rate[row[1]])

        row.append('')
        row.append('')
        row.append('')
        row.append('')

        Fill_Constituents_List(D_Index,Constituents_List,row,period,date,D_ISIN_Currency,Tax_Rate,Latest_Price,Latest_Ex_Rate)

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

    Constituents_Row.append(row[16])
    Constituents_Row.append(row[17])
    Constituents_Row.append(row[18])
    Constituents_Row.append(row[19])

    Constituents_List.append(Constituents_Row)

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
    for row in list:
        var1 = row[1]+'_'+date

        if var1 in D_Price:
            price = D_Price[var1]
            Row = []
            Row.append(price)
            Row.append(date)
            Latest_Price[row[1]] = Row
def Get_Price(ISIN,D_Price,date,Latest_Price):
    var1 = ISIN+'_'+date

    if var1 in D_Price:
        price = D_Price[var1]
        return price
    else:
        return Latest_Price[ISIN][0]

def Get_Ex_Rate(fromCurrency,toCurrency,Ex_Rate,date):
    var1 = fromCurrency +'_'+date
    if var1 in Ex_Rate:
        fromRate = (Ex_Rate[var1])
        if toCurrency =="USD":
            toRate = 1
        else:
            toRate = (Ex_Rate[toCurrency+'_'+date])
        ex_Rate = toRate/fromRate
        return ex_Rate
    else:
        return 1

def Set_Latest_Ex_Rate(Index_Currency,list,Ex_Rate,Latest_Ex_Rate,date,D_ISIN_Currency):
    #print(Ex_Rate)
    for row in list:

        fromCurrency = D_ISIN_Currency[row[1]]
        var2 = fromCurrency +'_'+date
        #print(var2)

        if var2 in Ex_Rate:
            fromRate = (Ex_Rate[fromCurrency+'_'+date])
            if Index_Currency =="USD":
                toRate = 1
            else:
                toRate = (Ex_Rate[Index_Currency+'_'+date])
            ex_Rate = toRate/fromRate
            Latest_Ex_Rate[row[1]] = ex_Rate
