# Generated by Django 2.1.15 on 2020-12-28 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfoliocomposition',
            old_name='portfolio_id',
            new_name='portfolio',
        ),
    ]
