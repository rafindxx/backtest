from django.shortcuts import render
from decimal import Decimal
from calculation.models import PortfolioDescription, PortfolioComposition, TaxRate
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from calculation.utils import handle_uploaded_file, Validate_Read_CSV, remove_percent_symbole
from django.http import JsonResponse
from django.views import View
import csv
import pandas as pd
import dateutil.parser

# look template in 'root folder'
# The folder 'templates' is not checked inside the 'configuration folder'
# But it is checked inside the 'app' folder

class PortfolioView(View):
    """
    ** POST DATA **
    """
    def post(self, request):
        if request.method =='POST':
            file_name = handle_uploaded_file(request.FILES.get('protfolio_file'))
            identifier = request.POST.get('identifier')
            confirmbox = request.POST.get('confirmbox')
            tax_file = request.FILES.get('tax_rate')
            currency = request.FILES.get('currency')
            data = {'error':'', 'warning':'yes', 'yes':'yes'}#Validate_Read_CSV('./backtest-file/input/'+file_name, identifier)
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
                portfolio = create_portfolio(request, data)
                composition = portfolio_composition(data, currency, portfolio)
                if tax_file:
                    save_tax_rate = add_tax_rate(tax_file)
                if portfolio:
                    data = {
                        'status': True,
                        'success': 'Portfolio and composition is created successfully!'
                        }
                else:
                    data = {
                        'status': False,
                        'error': 'Portfolio and composition is not created please enter valid details!'
                        }

        return JsonResponse(data)



def create_portfolio(request, data):

    portfolio_obj = PortfolioDescription.objects.create(
        name = request.POST['name'],
        currency = request.POST['currency'],
        identifier = request.POST['identifier'],
        spin_off_treatment =request.POST['spin_off'],
        index_value_pr = Decimal(request.POST['index_vlaue']),
        market_value_pr = Decimal(request.POST['market_value']),
        file_name = file_name,
        period = 1,
        start_date = 0,
        end_date = 0
        )
    last_obj = PortfolioDescription.objects.last()
    return last_obj

def portfolio_composition(data, currency, portfolio):
    for d_data in data['D_Data'][last_Period]:
        composition_obj = PortfolioComposition.objects.create(
            portfolio_id= last_obj,
            isin = data['D_Data'][0],
            ric = data['D_Data'][1],
            weights = data['D_Data'][2],
            shares = data['D_Data'][3],
            currency = request.POST['currency'],
            country = data['D_Data'][4],
            quote_id =0,
            )
        last_composition = PortfolioDescription.objects.last()

def add_tax_rate(tax_file):
    data = pd.read_csv(tax_file)
    for i, j in data.iterrows():
        taxRate = remove_percent_symbole(j['WHT'])
        tax_rate = TaxRate.objects.create(
            country = j['COUNTRY'],
            index_value_ntr=Decimal(taxRate)
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
