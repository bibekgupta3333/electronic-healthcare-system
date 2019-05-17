# Generated by Django 2.1 on 2019-04-18 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instructions', '0045_instruction_invoice_pdf_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instruction',
            name='rejected_reason',
            field=models.IntegerField(blank=True, choices=[(0, 'No suitable patient can be found'), (1, 'The patient is no longer registered at this practice'), (2, 'The consent form is invalid'), (3, 'Inappropriate instruction for Subject Access Request'), (4, 'The instruction has generated fail'), (5, 'Instruction not process until dute date'), (6, 'Inappropriate consent / consent not properly obtained')], null=True),
        ),
    ]