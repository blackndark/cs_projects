# Generated by Django 3.2 on 2021-05-10 20:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0018_alter_listings_sarting_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='sarting_bid',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
