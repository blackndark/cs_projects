# Generated by Django 3.2 on 2021-05-10 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_alter_comment_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='maximum_bid',
            field=models.IntegerField(null=True),
        ),
    ]
