# Generated by Django 3.2 on 2021-04-28 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_auto_20210428_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='books_amount',
            field=models.IntegerField(default=0, editable=False, verbose_name='Количество книг автора'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='books_amount',
            field=models.IntegerField(default=0, editable=False, verbose_name='Количество книг жанра'),
        ),
    ]