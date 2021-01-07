from django.db import models
from django.utils.translation import ugettext_lazy as _
from decimal import *

# Create your models here.
class PortfolioDescription(models.Model):
    """Model to store event type info
    """
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=55)
    identifier = models.CharField(max_length=55)
    constituents_file_download = models.CharField(max_length=55)
    file_name =  models.FileField(upload_to='documents/')
    spin_off_treatment = models.CharField(max_length=55)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    index_value_pr =  models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    market_value_pr =  models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    divisor_pr =   models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    index_value_tr =   models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    market_value_tr =  models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    divisor_tr =  models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    index_value_ntr = models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    market_value_ntr =  models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    divisor_ntr = models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    period =  models.IntegerField()

    class Meta:
        db_table = 'portfolio_description'
        verbose_name = _('Portfolio Description')
        verbose_name_plural = _('Portfolio Description')

    def __str__(self):
        """Return str for object."""
        return '{id} <{name}>'.format(
            id=self.pk,
            name=self.name
        )


class PortfolioComposition(models.Model):
    """Model to store event type info
    """
    portfolio = models.ForeignKey(PortfolioDescription, on_delete=models.CASCADE)
    isin = models.CharField(max_length=50)
    ric = models.CharField(max_length=50)
    weights = models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    shares = models.DecimalField(max_digits=30, decimal_places=15, blank=True, null=True)
    currency = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    quote_id = models.IntegerField()

    class Meta:
        db_table = 'portfolio_composition'
        verbose_name = _('Portfolio Composition')
        verbose_name_plural = _('Portfolio Composition')

    def __str__(self):
        """Return str for object."""
        return '{id}'.format(
            id=self.pk
        )


class TaxRate(models.Model):
    """Model to store event type info
    """
    country = models.CharField(max_length=50)
    tax = models.CharField(max_length=50)

    class Meta:
        db_table = 'tax_rate'
        verbose_name = _('Tax Rate')
        verbose_name_plural = _('Tax Rate')

    def __str__(self):
        """Return str for object."""
        return '{id}'.format(
            id=self.pk
        )


class CurrencyCode(models.Model):
    """Model to store event type info
    """
    country_name = models.CharField(blank=True, null=True, max_length=100)
    currency = models.CharField(blank=True, null=True, max_length=100)
    currency_code = models.CharField(blank=True, null=True, max_length=50)
    currency_number = models.CharField(blank=True, null=True,  max_length=50)



    class Meta:
        db_table = 'currency_code'
        verbose_name = _('Currency Code')
        verbose_name_plural = _('Currency Code')

    def __str__(self):
        return '{id} <{country_name}>'.format(
            id=self.pk,
            country_name=self.country_name,
        )
