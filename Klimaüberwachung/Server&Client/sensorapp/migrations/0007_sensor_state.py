# Generated by Django 2.1.4 on 2019-02-06 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensorapp', '0006_user_accepted_agbs'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='state',
            field=models.CharField(blank=True, choices=[('0', 'Not Connected'), ('1', 'No Data'), ('2', 'Good Climate'), ('3', 'Too dry'), ('4', 'Too hot'), ('5', 'Too moist'), ('6', 'Too cold'), ('7', 'Error')], default='0', max_length=512, null=True, verbose_name='State'),
        ),
    ]
