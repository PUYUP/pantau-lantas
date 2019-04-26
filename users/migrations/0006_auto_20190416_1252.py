# Generated by Django 2.2 on 2019-04-16 12:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20190416_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpolicenumberclaim',
            name='police_number',
            field=models.CharField(max_length=255, null=True, validators=[django.core.validators.MinLengthValidator(4)]),
        ),
    ]
