# Generated by Django 2.1 on 2018-12-17 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instructions', '0010_instructioninternalnote'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='InstructionClientNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(max_length=255)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_notes', to='instructions.Instruction')),
            ],
            options={
                'verbose_name': 'Instruction Client Note',
            },
        ),
        migrations.RenameField(
            model_name='instructioninternalnote',
            old_name='notes',
            new_name='note',
        ),
    ]
