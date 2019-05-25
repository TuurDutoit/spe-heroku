# Generated by Django 2.2.1 on 2019-05-25 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20190524_0946'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='location',
            name='longitude',
        ),
        migrations.AddField(
            model_name='location',
            name='address',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='is_valid',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]