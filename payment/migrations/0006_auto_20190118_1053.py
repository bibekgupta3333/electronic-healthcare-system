# Generated by Django 2.1.4 on 2019-01-18 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20190111_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructionvolumefee',
            name='vat',
            field=models.DecimalField(decimal_places=2, default=20, max_digits=5, verbose_name='VAT(%)'),
        ),
    ]
