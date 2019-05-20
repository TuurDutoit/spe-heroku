# Generated by Django 2.2.1 on 2019-05-20 12:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20190520_0900'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)])),
                ('longitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)])),
                ('related_to', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.IntegerField()),
                ('end', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='routes_to', to='web.Location')),
                ('start', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='routes_from', to='web.Location')),
            ],
        ),
        migrations.AddIndex(
            model_name='route',
            index=models.Index(fields=['start'], name='web_route_start_i_bf40bd_idx'),
        ),
        migrations.AddIndex(
            model_name='route',
            index=models.Index(fields=['end'], name='web_route_end_id_5a0c95_idx'),
        ),
    ]
