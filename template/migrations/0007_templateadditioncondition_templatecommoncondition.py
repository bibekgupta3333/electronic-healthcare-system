# Generated by Django 2.1 on 2018-12-21 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snomedct', '0002_auto_20181206_0819'),
        ('template', '0006_auto_20181201_1057'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateAdditionCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snomedct', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='snomedct.SnomedConcept')),
                ('template_instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='template.TemplateInstruction')),
            ],
            options={
                'verbose_name': 'Template Additional Conditions',
            },
        ),
        migrations.CreateModel(
            name='TemplateCommonCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('common_condition', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='snomedct.CommonSnomedConcepts')),
                ('template_instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='template.TemplateInstruction')),
            ],
            options={
                'verbose_name': 'Template Common Conditions',
            },
        ),
    ]
