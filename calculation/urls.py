from django.urls import path
from django.conf.urls import url
from django.conf import settings
from calculation import views
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static

urlpatterns = [
    url(r'get_portfolio/$', csrf_exempt(views.GetPortfolioView.as_view()), name='get_portfolio'),
    url(r'tax_rate/$', csrf_exempt(views.getTax.as_view()), name='taxrate'),
    url(r'add_tax/$', csrf_exempt(views.AddNewTax.as_view()), name='add_tax'),
    url(r'update_tax/$', csrf_exempt(views.updateTax.as_view()), name='update_tax'),
    url(r'rerun_portfolio/$', csrf_exempt(views.RerunPortfolio.as_view()), name='rerun_portfolio'),
    url(r'portfolio/$', csrf_exempt(views.PortfolioView.as_view()), name='portfolio'),

]
