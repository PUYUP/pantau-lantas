# Generated by Django 2.2 on 2019-04-16 14:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_auto_20190416_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policenumber',
            name='number',
            field=models.CharField(max_length=255, null=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.RegexValidator(message='Only alphanumeric characters are allowed.', regex='^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)+$')]),
        ),
    ]
