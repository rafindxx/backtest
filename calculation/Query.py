def Query_Price(IDentifier,LIST,S_DATE,E_DATE):
    Query=""
    if IDentifier=='ISIN':
        Query= "select  b.isin,a.p_date as date,a.p_price,a.currency from fp_v2.fp_basic_prices a inner join sym_v1.sym_coverage c on a.fsym_id=c.fsym_regional_id inner join sym_v1.sym_isin b on c.fsym_id=b.fsym_id WHERE b.isin in ("+LIST +") AND  a.p_date between '"+S_DATE+"' and '"+E_DATE+"' ORDER BY b.isin, a.p_date asc"
    else:
        Query= "select a.fsym_id,a.p_date as date,a.p_price,a.currency from fp_v2.fp_basic_prices a WHERE a.fsym_id in  ("+LIST +")  AND  a.p_date between '"+S_DATE+"' and '"+E_DATE+"'  ORDER BY a.fsym_id, a.p_date asc"
    return Query

def Query_Divident(IDentifier,LIST,S_DATE,E_DATE):
    Query=""
    if IDentifier=='ISIN':
        Query= "SELECT ISN.isin ,DIV.p_divs_pd,DIV.p_divs_s_spinoff,DIV.currency,DIV.p_divs_pd_type_code,DIV.p_divs_exdate as date FROM FDS_DataFeeds.fp_v2.fp_basic_dividends  AS DIV inner join [sym_v1].[sym_coverage] c on DIV.fsym_id = c.fsym_regional_id inner join [sym_v1].[sym_isin] ISN  on c.fsym_id=ISN.fsym_id WHERE ISN.isin in ("+LIST +") AND  DIV.p_divs_exdate between '"+S_DATE+"' and '"+E_DATE+"' ORDER BY ISN.isin, DIV.p_divs_exdate"
    else:
        Query= "div.fsym_id,DIV.p_divs_pd,DIV.p_divs_s_spinoff,DIV.currency,DIV.p_divs_pd_type_code,DIV.p_divs_exdate as date FROM FDS_DataFeeds.fp_v2.fp_basic_dividends  AS DIV WHERE DIV.fsym_id in ("+LIST +") AND  DIV.p_divs_exdate between '"+S_DATE+"' and '"+E_DATE+"' ORDER BY DIV.fsym_id, DIV.p_divs_exdate"
    return Query

def Query_Split(IDentifier,LIST,S_DATE,E_DATE):
    Query=""
    if IDentifier=='ISIN':
        Query= "SELECT b.isin,a.p_split_date,p_split_factor FROM [fp_v2].[fp_basic_splits] a inner join [sym_v1].[sym_coverage] c on a.fsym_id=c.fsym_regional_id inner join [sym_v1].[sym_isin] b on c.fsym_id=b.fsym_id WHERE b.isin in ("+LIST +") AND  a.p_split_date between '"+S_DATE+"' and '"+E_DATE+"' ORDER BY b.isin, a.p_split_date"
    else:
        Query= "SELECT a.* FROM [fp_v2].[fp_basic_splits] a WHERE a.fsym_id in ("+LIST +") AND  a.p_split_date between '"+S_DATE+"' and '"+E_DATE+"' ORDER by a.fsym_id, a.p_split_date "
    return Query

def Query_TR_Price(LIST,Date):
#with cte  AS ( select distinct File_code,columnname, colvalue,Quote_ID,RIC,Trade_date from (select * from EQU_Price ) src unpivot (colvalue for columnname in ( offi_close_price,last_trade_price,p_close_price,bid_price,ask_price,alt_close_price,open_price,high_price,low_price,mid_price)) AS pvt WHERE Quote_ID IN( SELECT quote_id FROM TR_Equity WHERE ric in ('600085.SS','600556.SS','4113.TWO') AND valid_flag=1) AND Trade_Date ='2021-01-06' and Valid_flag=1) select c.Quote_ID,c.RIC,c.Trade_Date,c.colvalue AS price from tabl t join cte c on t.Code=c.File_code AND t.Column_ref=c.columnname
    Query="with cte  AS ( select distinct File_code,columnname, colvalue,Quote_ID,RIC,Trade_date from (select * from EQU_Price ) src unpivot (colvalue for columnname in ( offi_close_price,last_trade_price,p_close_price,bid_price,ask_price,alt_close_price,open_price,high_price,low_price,mid_price)) AS pvt WHERE Quote_ID IN( SELECT quote_id FROM TR_Equity WHERE ric in ("+LIST +") AND valid_flag=1) AND Trade_Date ='"+Date+"' and Valid_flag=1) select c.Quote_ID,c.RIC,c.Trade_Date,c.colvalue AS price from tabl t join cte c on t.Code=c.File_code AND t.Column_ref=c.columnname"
    return Query;

def Query_TR_Equity(LIST):
    Query ="SELECT ric,quote_id FROM TR_Equity WHERE ric in ("+LIST +") AND valid_flag=1"
    print(Query)
    return Query;
