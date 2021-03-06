# Generated by Django 2.1 on 2019-01-22 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_thirdpartyauthorisation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patientreportauth',
            old_name='count',
            new_name='patient_count',
        ),
        migrations.RenameField(
            model_name='patientreportauth',
            old_name='locked_report',
            new_name='patient_locked_report',
        ),
        migrations.RenameField(
            model_name='patientreportauth',
            old_name='mobi_request_id',
            new_name='patient_mobi_request_id',
        ),
        migrations.AddField(
            model_name='patientreportauth',
            name='third_party_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='patientreportauth',
            name='third_party_locked_report',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='patientreportauth',
            name='third_party_mobi_request_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='patientreportauth',
            name='third_party_mobi_request_voice_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='patientreportauth',
            name='third_party_verify_sms_pin',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='patientreportauth',
            name='third_party_verify_voice_pin',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='thirdpartyauthorisation',
            name='family_phone_number_code',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='thirdpartyauthorisation',
            name='office_phone_number_code',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='thirdpartyauthorisation',
            name='unique',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
