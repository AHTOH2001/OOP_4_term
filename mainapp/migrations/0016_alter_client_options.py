# Generated by Django 3.2 on 2021-04-09 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0015_alter_client_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
    ]