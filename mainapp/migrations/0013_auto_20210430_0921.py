# Generated by Django 3.2 on 2021-04-30 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_auto_20210429_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='amount',
            field=models.IntegerField(default=0, verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='book',
            name='collateral_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, verbose_name='Залоговая стоимость'),
        ),
    ]
