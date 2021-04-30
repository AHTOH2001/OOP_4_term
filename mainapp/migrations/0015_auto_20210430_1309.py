# Generated by Django 3.2 on 2021-04-30 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_alter_book_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basket',
            name='client',
        ),
        migrations.AddField(
            model_name='client',
            name='baskets',
            field=models.ManyToManyField(to='mainapp.Basket', verbose_name='Корзины клиента'),
        ),
        migrations.AlterField(
            model_name='basket',
            name='date_of_taking',
            field=models.DateTimeField(null=True, verbose_name='Дата и время взятия'),
        ),
        migrations.AlterField(
            model_name='basket',
            name='return_date',
            field=models.DateTimeField(null=True, verbose_name='Дата и время возврата'),
        ),
    ]
