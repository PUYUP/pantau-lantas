# Generated by Django 2.2 on 2019-04-15 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userpolicenumberclaim'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpolicenumberclaim',
            name='is_accept',
            field=models.NullBooleanField(),
        ),
    ]
