from django.urls import path
from django.conf.urls import url
from django.conf import settings
from calculation import views
from django.conf.urls.static import static

urlpatterns = [
    url(r'get_portfolio/$', views.GetPortfolioView.as_view(), name='get_portfolio'),
    url(r'rerun_portfolio/$', views.RerunPortfolio.as_view(), name='rerun_portfolio'),
    url(r'portfolio/$', views.PortfolioView.as_view(), name='portfolio'),

]
