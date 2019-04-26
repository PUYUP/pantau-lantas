# Generated by Django 2.2 on 2019-04-16 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190415_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpolicenumberclaim',
            name='file_certificate_ownership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='mains.FileManagement'),
        ),
        migrations.AlterField(
            model_name='userpolicenumberclaim',
            name='file_certificate_vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='police_number_claim', to='mains.FileManagement'),
        ),
        migrations.AlterField(
            model_name='userpolicenumberclaim',
            name='file_identity_card',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='mains.FileManagement'),
        ),
    ]
