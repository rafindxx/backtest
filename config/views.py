# bookstore/views.py

from django.shortcuts import render
from calculation.models import PortfolioDescription, CurrencyCode
from django.http import JsonResponse

# look template in 'root folder'
# The folder 'templates' is not checked inside the 'configuration folder'
# But it is checked inside the 'app' folder
def index(request):
    portfolio_list = PortfolioDescription.objects.all()
    currency_list = CurrencyCode.objects.all().order_by('currency_code')
    return render(request, 'index.html', {'all_objects': portfolio_list, 'currency_list': currency_list})




