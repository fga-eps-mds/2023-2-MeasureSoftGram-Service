# Generated by Django 4.0.6 on 2023-11-11 18:28

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0004_alter_organization_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='gaugeRedLimit',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.33'), max_digits=3),
        ),
        migrations.AddField(
            model_name='product',
            name='gaugeYellowLimit',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.66'), max_digits=3),
        ),
    ]
