# Generated by Django 2.1 on 2018-12-25 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snomedct', '0002_auto_20181206_0819'),
        ('template', '0007_templateadditioncondition_templatecommoncondition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='templateadditioncondition',
            name='snomedct',
        ),
        migrations.RemoveField(
            model_name='templateadditioncondition',
            name='template_instruction',
        ),
        migrations.RemoveField(
            model_name='templatecommoncondition',
            name='common_condition',
        ),
        migrations.RemoveField(
            model_name='templatecommoncondition',
            name='template_instruction',
        ),
        migrations.RemoveField(
            model_name='templateconditionsofinterest',
            name='snomedct',
        ),
        migrations.RemoveField(
            model_name='templateconditionsofinterest',
            name='template_instruction',
        ),
        migrations.RemoveField(
            model_name='templateadditionalquestion',
            name='response_mandatory',
        ),
        migrations.RemoveField(
            model_name='templateinstruction',
            name='type',
        ),
        migrations.AddField(
            model_name='templateinstruction',
            name='common_snomed_concepts',
            field=models.ManyToManyField(to='snomedct.CommonSnomedConcepts'),
        ),
        migrations.AlterField(
            model_name='templateadditionalquestion',
            name='template_instruction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='template.TemplateInstruction'),
        ),
        migrations.DeleteModel(
            name='TemplateAdditionCondition',
        ),
        migrations.DeleteModel(
            name='TemplateCommonCondition',
        ),
        migrations.DeleteModel(
            name='TemplateConditionsOfInterest',
        ),
    ]