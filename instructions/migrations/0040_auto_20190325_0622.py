# Generated by Django 2.1 on 2019-03-25 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instructions', '0039_auto_20190319_0318'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruction',
            name='ins_amount_rate_lvl_1',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='instruction',
            name='ins_amount_rate_lvl_2',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='instruction',
            name='ins_amount_rate_lvl_3',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='instruction',
            name='ins_amount_rate_lvl_4',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='instruction',
            name='ins_max_day_lvl_1',
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='instruction',
            name='ins_max_day_lvl_2',
            field=models.PositiveSmallIntegerField(default=7),
        ),
        migrations.AddField(
            model_name='instruction',
            name='ins_max_day_lvl_3',
            field=models.PositiveSmallIntegerField(default=11),
        ),
        migrations.AddField(
            model_name='instruction',
            name='ins_max_day_lvl_4',
            field=models.PositiveSmallIntegerField(default=12),
        ),
        migrations.AlterField(
            model_name='instruction',
            name='rejected_reason',
            field=models.IntegerField(blank=True, choices=[(0, 'No suitable patient can be found'), (1, 'The patient is no longer registered at this practice'), (2, 'The consent form is invalid'), (3, 'Inappropriate instruction for Subject Access Request'), (4, 'The instruction has generated fail'), (5, 'Instruction not process until dute date')], null=True),
        ),
    ]
