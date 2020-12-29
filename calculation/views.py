from django.shortcuts import render
from decimal import Decimal
from calculation.models import PortfolioDescription, PortfolioComposition, TaxRate
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from calculation.utils import handle_uploaded_file, Validate_Read_CSV, remove_percent_symbole, Cal_Index
from django.http import JsonResponse
from django.views import View
import csv
import pandas as pd
import dateutil.parser

# look template in 'root folder'
# The folder 'templates' is not checked inside the 'configuration folder'
# But it is checked inside the 'app' folder
D_Index = {}
D_Index["Identifier"] = "ISIN"
D_Index["IV"] = 1000
D_Index["MV"] = 100000
D_Index["Currency"] = "EUR"
D_Index["Adjustment"] = "DA"#"SA"
D_Index["DCFO"] = "ND"#"CD","EDD"

class PortfolioView(View):
    """
    ** POST DATA **
    """
    def post(self, request):
        if request.method =='POST':
            file_name = handle_uploaded_file(request.FILES.get('protfolio_file'))
            identifier = request.POST.get('identifier')
            confirmbox = request.POST.get('confirmbox')
            tax_file = request.POST.get('tax_rate')
            currency = request.POST.get('currency')
            data = Validate_Read_CSV('./static/backtest-file/input/'+file_name, identifier)
            last_Period = data['last_Period']
            if data['error']:
                data = {
                    'status': True,
                    'error': data['error']
                    }
            elif data['warning'] and confirmbox =='':
                data = {
                    'status': True,
                    'warning': data['warning']
                    }
            else:
                portfolio = create_portfolio(request, file_name, data, last_Period)
                composition = portfolio_composition(data, currency, portfolio, last_Period)
                if tax_file:
                    save_tax_rate = add_tax_rate(tax_file)
                if portfolio:
                    save_file = Cal_Index(D_Index, data['D_Data'], data['D_ISIN'],data['D_Date'])
                    data = {
                        'status': True,
                        'success': 'Portfolio and composition is created successfully!',
                        'index_file': save_file['index_value_file'],
                        'constituents_file': save_file['constituents_file']
                        }
                else:
                    data = {
                        'status': False,
                        'error': 'Portfolio and composition is not created please enter valid details!'
                        }
        return JsonResponse(data)



def create_portfolio(request, file_name, data, last_Period):
    start_date = last_Period+'_START'
    end_date =last_Period+'_END'
    portfolio_obj = PortfolioDescription.objects.create(
        name = request.POST.get('name'),
        currency = request.POST.get('currency'),
        identifier = request.POST.get('identifier'),
        spin_off_treatment = request.POST.get('spin_off'),
        index_value_pr = Decimal(request.POST.get('index_vlaue')),
        market_value_pr = Decimal(request.POST.get('market_value')),
        file_name = file_name,
        period = data['last_Period'],
        start_date = data['D_Date'][start_date],
        end_date = data['D_Date'][end_date]
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

def add_tax_rate(tax_file):
    data = pd.read_csv(tax_file)
    for i, j in data.iterrows():
        taxRate = remove_percent_symbole(j['WHT'])
        tax_rate = TaxRate.objects.create(
            country = j['COUNTRY'],
            tax  = Decimal(taxRate)
            )

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
