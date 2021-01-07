from django.contrib import admin

# Register your models here.
from calculation.models import PortfolioDescription, PortfolioComposition, TaxRate, CurrencyCode

admin.site.register(PortfolioDescription)
admin.site.register(PortfolioComposition)
admin.site.register(TaxRate)
admin.site.register(CurrencyCode)
