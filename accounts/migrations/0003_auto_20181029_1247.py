# Generated by Django 2.1 on 2018-10-29 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20181022_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='patient_input_email',
            field=models.EmailField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='patient',
            name='emis_number',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='patient',
            name='microtest_number',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='patient',
            name='organisation_gp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organisations.OrganisationGeneralPractice'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='systmone_number',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='patient',
            name='vision_number',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]