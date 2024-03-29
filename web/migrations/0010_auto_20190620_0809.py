# Generated by Django 2.2.1 on 2019-06-20 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_recommendation_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recommendation',
            name='title',
        ),
        migrations.AddField(
            model_name='location',
            name='is_office',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recommendation',
            name='loc_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='web.Location'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recommendation',
            name='service_type',
            field=models.CharField(choices=[('meeting', 'Meeting'), ('call', 'Call'), ('email', 'Email')], default='meeting', max_length=10),
            preserve_default=False,
        ),
    ]
