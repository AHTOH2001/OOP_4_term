# Generated by Django 3.2 on 2021-04-09 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0009_alter_client_register_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='username',
            field=models.CharField(default='Клиент <built-in function id>', max_length=150),
        ),
    ]