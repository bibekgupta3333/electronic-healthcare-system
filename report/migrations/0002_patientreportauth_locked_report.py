# Generated by Django 2.1 on 2018-11-13 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientreportauth',
            name='locked_report',
            field=models.BooleanField(default=False),
        ),
    ]
