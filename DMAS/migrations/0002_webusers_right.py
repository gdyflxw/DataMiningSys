# Generated by Django 2.0.5 on 2018-05-27 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DMAS', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webusers',
            name='right',
            field=models.IntegerField(default=0),
        ),
    ]
