# Generated by Django 4.0.4 on 2022-06-06 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userinfo', '0004_product_trans_fat'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ingredient',
            field=models.CharField(default='Nothing', max_length=800),
        ),
    ]
