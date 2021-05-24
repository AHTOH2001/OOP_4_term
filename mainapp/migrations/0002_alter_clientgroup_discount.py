# Generated by Django 3.2 on 2021-05-08 13:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientgroup',
            name='discount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(-10)], verbose_name='Скидка в процентах'),
        ),
    ]
