# Generated by Django 2.1.4 on 2019-02-20 12:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sensorapp', '0007_sensor_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sensor',
            name='state',
            field=models.CharField(blank=True, choices=[('0', 'Not Connected'), ('1', 'No Data'), ('2', 'Climate is good!'), ('3', 'Too cold!'), ('4', 'Too hot!'), ('5', 'Too moist!'), ('6', 'Too dry!'), ('7', 'Too dry and too hot!'), ('8', 'Too dry and too cold!'), ('9', 'Too moist and too hot!'), ('10', 'Too moist and too cold!'), ('11', 'Error')], default='0', max_length=512, null=True, verbose_name='State'),
        ),
    ]
