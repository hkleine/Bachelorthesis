# Generated by Django 2.1.4 on 2019-02-05 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensorapp', '0005_auto_20190202_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='accepted_agbs',
            field=models.BooleanField(default=True),
        ),
    ]
