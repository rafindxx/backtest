from django.shortcuts import render
from decimal import Decimal
from calculation.models import PortfolioDescription, PortfolioComposition, TaxRate
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from calculation.utils import handle_uploaded_file, Validate_Read_CSV, remove_percent_symbole, Cal_Index, Rerun_Dbdata, DateTime
from django.http import JsonResponse
from django.views import View
import csv
import pandas as pd
import dateutil.parser
from django.db.models import Q

# look template in 'root folder'
# The folder 'templates' is not checked inside the 'configuration folder'
# But it is checked inside the 'app' folder


class PortfolioView(View):
    """
    ** POST DATA **
    """
    def post(self, request):
        D_Index = {}
        if request.method =='POST':
            file_name = handle_uploaded_file(request.FILES.get('protfolio_file'))
            identifier = request.POST.get('identifier')
            confirmbox = request.POST.get('confirmbox')
            tax_file = request.FILES.get('tax_rate')
            currency = request.POST.get('currency')
            save_data = request.POST.get('save_data')
            csv_data = Validate_Read_CSV('./static/backtest-file/input/'+file_name, identifier)
            if csv_data['error']:
                data = {
                    'status': False,
                    'error': csv_data['error']
                    }
            elif csv_data['warning'] and confirmbox =='':
                data = {
                    'status': True,
                    'warning': csv_data['warning']
                    }
            else:
                last_Period = csv_data['last_Period']
                D_RIC_ISIN = csv_data['D_RIC_ISIN']
                index_vlaue = request.POST.get('index_vlaue')
                market_value = request.POST.get('market_value')
                if market_value==0 or index_vlaue==0:
                    index_vlaue= 1000
                    market_value=100000
                if save_data:
                    portfolio = create_portfolio(request, file_name, csv_data, last_Period)
                    composition = portfolio_composition(csv_data, currency, portfolio, last_Period)
                if tax_file:
                    save_tax_rate = add_tax_rate(tax_file)
                if market_value < index_vlaue:
                    data = {
                    'status': False,
                    'error_msg': 'Market Value should be greater then Index Value.'
                    }
                else:
                    D_Index["Identifier"] = identifier
                    D_Index["IV"] = int(request.POST.get('index_vlaue'))
                    D_Index["MV"] = int(request.POST.get('market_value'))
                    D_Index["Currency"] = currency
                    D_Index["Adjustment"] = request.POST.get('spin_off')
                    D_Index["DCFO"] = request.POST.get('download')
                    save_file = Cal_Index(D_Index, csv_data['D_Data'], csv_data['D_ISIN'], csv_data['D_Date'], D_RIC_ISIN, last_Period)
                    data = {
                        'status': True,
                        'success': 'Index file and Constituents file is created successfully!',
                        'index_file': save_file['index_value_file'],
                        'constituents_file': save_file['constituents_file']
                        }
            return JsonResponse(data)



def create_portfolio(request, file_name, data, last_Period):
    print(request.POST.get('download'))
    start_date = last_Period+'_START'
    end_date = last_Period+'_END'
    date_start = DateTime(data['D_Date'][start_date])
    date_end = DateTime(data['D_Date'][end_date])
    portfolio_obj = PortfolioDescription.objects.create(
        name = request.POST.get('name'),
        currency = request.POST.get('currency'),
        identifier = request.POST.get('identifier'),
        spin_off_treatment = request.POST.get('spin_off'),
        index_value_pr = Decimal(request.POST.get('index_vlaue')),
        market_value_pr = Decimal(request.POST.get('market_value')),
        constituents_file_download = request.POST.get('download'),
        file_name = file_name,
        period = data['last_Period'],
        start_date = date_start,
        end_date = date_end
        )
    last_obj = PortfolioDescription.objects.last()
    return last_obj

def portfolio_composition(data, currency, portfolio, last_Period):
    for comp_data in data['D_Data'][last_Period]:
        weights = remove_percent_symbole(comp_data[2])
        composition_obj = PortfolioComposition.objects.create(
            portfolio= portfolio,
            isin = comp_data[1],
            ric = comp_data[6],
            weights = weights,
            shares = 0,
            currency = currency,
            country = comp_data[5],
            quote_id =0,
            )
        last_composition = PortfolioDescription.objects.last()
    return last_composition

def add_tax_rate(tax_file):
    data = pd.read_csv(tax_file)
    obj =TaxRate.objects.all()
    for i, j in data.iterrows():
        if j['COUNTRY'] not in obj:
            TaxRate.objects.create(
                country=j['COUNTRY'],
                tax=j['WHT']
                )
        else:
            TaxRate.objects.filter(country=j['COUNTRY']).update(tax=j['WHT'])

    return True

class GetPortfolioView(View):
    """docstring for GetPortfolioView"""
    def post(self, request):
        if request.method =='POST':
            portfolio_id = request.POST.get('id')
            portfolio_list = PortfolioDescription.objects.filter(id=portfolio_id)
            for portfolio in portfolio_list:
                start_date = dateutil.parser.parse(str(portfolio.start_date)).date()
                end_date = dateutil.parser.parse(str(portfolio.end_date)).date()
                data = {
                    'status': True,
                    'start_date':start_date,
                    'end_date': end_date
                    }
            return JsonResponse(data)


class RerunPortfolio(View):
    """docstring for ClassName"""
    def post(self, request):
        if request.method == 'POST':
            D_Index ={}
            portfolio_id = request.POST.get('portfolio_id')
            portfolio = PortfolioDescription.objects.filter(id=portfolio_id)
            get_composition = PortfolioComposition.objects.filter(portfolio_id=portfolio_id)
            for portfolio_data in portfolio:
                D_Index["Identifier"] = portfolio_data.identifier
                D_Index["IV"] = int(portfolio_data.index_value_pr)
                D_Index["MV"] = int(portfolio_data.market_value_pr)
                D_Index["Currency"] = portfolio_data.currency
                D_Index["Adjustment"] = portfolio_data.spin_off_treatment
                D_Index["DCFO"] = portfolio_data.constituents_file_download
                start_date = dateutil.parser.parse(str(portfolio_data.start_date)).date()
                end_date = dateutil.parser.parse(str(portfolio_data.end_date)).date()
                period = portfolio_data.period
            rerun_date = Rerun_Dbdata(D_Index, start_date, end_date, period, get_composition)
            data = {
                    'status': True,
                    'success': 'Index file and Constituents file is created please download.',
                    'index_file': rerun_date['index_value_file'],
                    'constituents_file': rerun_date['constituents_file']
                }
        else:
            data = {
                'status': False,
                'error': 'Portfolio and composition is not created please enter valid details!'
                }
        return JsonResponse(data)

class getTax(View):
    """docstring for ClassName"""
    def get(self, request):
        tax_data = TaxRate.objects.all()
        return render(request, 'tax_file.html', {'tax_object': tax_data})


        
class AddNewTax(View):
    """docstring for ClassName"""
    def post(self, request):
        if request.method=='POST':
            country = request.POST.get('country')
            tax = request.POST.get('tax')
            tax_obj = TaxRate.objects.create(
                country=country,
                tax=tax
                )
            response ={'status': True, 'message':'Tax Rate successfully added.'}        
        return JsonResponse(response)



