# Generated by Django 2.1.15 on 2020-12-29 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0002_portfolio'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=50)),
                ('tax', models.DecimalField(blank=True, decimal_places=15, max_digits=30, null=True)),
            ],
            options={
                'verbose_name': 'Tax Rate',
                'verbose_name_plural': 'Tax Rate',
                'db_table': 'tax_rate',
            },
        ),
    ]
