# Generated by Django 3.2 on 2021-04-30 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_auto_20210430_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='amount',
            field=models.IntegerField(blank=True, default=0, verbose_name='Количество'),
        ),
    ]
