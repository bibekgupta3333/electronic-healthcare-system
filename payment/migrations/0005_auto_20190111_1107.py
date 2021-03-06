# Generated by Django 2.1 on 2019-01-11 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20181226_0427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisationfee',
            name='max_day_lvl_1',
            field=models.PositiveSmallIntegerField(default=5, verbose_name='Top payment band until day'),
        ),
        migrations.AlterField(
            model_name='organisationfee',
            name='max_day_lvl_2',
            field=models.PositiveSmallIntegerField(default=10, verbose_name='Medium payment band until day'),
        ),
        migrations.AlterField(
            model_name='organisationfee',
            name='max_day_lvl_3',
            field=models.PositiveSmallIntegerField(default=15, verbose_name='Low payment band until day'),
        ),
        migrations.AlterField(
            model_name='organisationfee',
            name='max_day_lvl_4',
            field=models.PositiveSmallIntegerField(default=16, verbose_name='Lowest payment band after day'),
        ),
    ]
