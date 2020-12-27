# bookstore/views.py

from django.shortcuts import render
from calculation.models import PortfolioDescription
from django.http import JsonResponse

# look template in 'root folder'
# The folder 'templates' is not checked inside the 'configuration folder'
# But it is checked inside the 'app' folder
def index(request):
    portfolio_list = PortfolioDescription.objects.all()
    return render(request, 'index.html', {'all_objects': portfolio_list})




