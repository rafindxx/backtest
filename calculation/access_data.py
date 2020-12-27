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
        Query= "SELECT DIV.*,DIV.p_divs_exdate as date ,ISN.isin FROM FDS_DataFeeds.fp_v2.fp_basic_dividends  AS DIV inner join [sym_v1].[sym_coverage] c on DIV.fsym_id = c.fsym_regional_id inner join [sym_v1].[sym_isin] ISN  on c.fsym_id=ISN.fsym_id WHERE ISN.isin in ("+LIST +") AND  DIV.p_divs_exdate between '"+S_DATE+"' and '"+E_DATE+"' ORDER BY ISN.isin, DIV.p_divs_exdate"
    else:
        Query= "SELECT DIV.*,DIV.p_divs_exdate as date FROM FDS_DataFeeds.fp_v2.fp_basic_dividends  AS DIV WHERE DIV.fsym_id in ("+LIST +") AND  DIV.p_divs_exdate between '"+S_DATE+"' and '"+E_DATE+"' ORDER BY DIV.fsym_id, DIV.p_divs_exdate"
    return Query

def Query_Split(IDentifier,LIST,S_DATE,E_DATE):
    Query=""
    if IDentifier=='ISIN':
        Query= "SELECT a.*,a.p_split_date as date, b.isin FROM [fp_v2].[fp_basic_splits] a inner join [sym_v1].[sym_coverage] c on a.fsym_id=c.fsym_regional_id inner join [sym_v1].[sym_isin] b on c.fsym_id=b.fsym_id WHERE b.isin in ("+LIST +") AND  a.p_split_date between '"+S_DATE+"' and '"+E_DATE+"' ORDER BY b.isin, a.p_split_date"
    else:
        Query= "SELECT a.*,a.p_split_date as date FROM [fp_v2].[fp_basic_splits] a WHERE a.fsym_id in ("+LIST +") AND  a.p_split_date between '"+S_DATE+"' and '"+E_DATE+"' ORDER by a.fsym_id, a.p_split_date "
    return Query
