# Generated by Django 2.1 on 2018-10-08 04:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('snomedct', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('completed_signed_off_timestamp', models.DateTimeField(blank=True, null=True)),
                ('rejected_timestamp', models.DateTimeField(blank=True, null=True)),
                ('rejected_note', models.TextField(blank=True)),
                ('rejected_reason', models.IntegerField(blank=True, choices=[(0, 'No suitable patient can be found'), (1, 'The patient is no longer registered at this practice'), (2, 'The consent form is invalid'), (3, 'Inappropriate purpose for Subject Access Request')], null=True)),
                ('type', models.CharField(choices=[('AMRA', 'AMRA'), ('SARS', 'SARS')], max_length=4)),
                ('final_report_date', models.TextField(blank=True)),
                ('initial_monetary_value', models.FloatField(blank=True, null=True, verbose_name='Value £')),
                ('status', models.IntegerField(choices=[(0, 'New'), (1, 'In Progress'), (2, 'Overdue'), (3, 'Complete'), (4, 'Reject')], default=0)),
                ('consent_form', models.FileField(blank=True, null=True, upload_to='consent_forms')),
                ('gp_practice_id', models.CharField(max_length=255)),
                ('client_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.ClientUser', verbose_name='Client')),
                ('gp_practice_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('gp_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.GeneralPracticeUser', verbose_name='GP Allocated')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Patient', verbose_name='Patient')),
            ],
            options={
                'verbose_name': 'Instruction',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='InstructionAdditionQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=255)),
                ('response_mandatory', models.BooleanField(default=False)),
                ('instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instructions.Instruction')),
            ],
            options={
                'verbose_name': 'Instruction Addition Question',
            },
        ),
        migrations.CreateModel(
            name='InstructionConditionsOfInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instructions.Instruction')),
                ('snomedct', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='snomedct.SnomedConcept')),
            ],
            options={
                'verbose_name': 'Instruction Conditions Of Interest',
            },
        ),
    ]
