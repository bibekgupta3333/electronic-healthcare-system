from django.db import migrations
import os
from django.conf import settings
from medicalreport.models import NhsSensitiveConditions


def add_custom(*args):
    path = os.path.join(os.path.dirname(settings.BASE_DIR), 'initial_data/nhs_sensitive_conditions.txt')
    with open(path) as file:
        file_lines = file.readlines()
        for line in file_lines[1:]:
            NhsSensitiveConditions.objects.create(group=line.split()[0], snome_code=line.split()[1])


class Migration(migrations.Migration):

    dependencies = [
        ('medicalreport', '0007_auto_20181107_0837'),
    ]

    operations = [
        migrations.RunPython(add_custom)
    ]
