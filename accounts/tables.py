import django_tables2 as tables
from .models import User
from django.utils.html import format_html


class UserTable(tables.Table):
    checkbox = tables.CheckBoxColumn(attrs={'id': 'check_all'})

    class Meta:
        attrs = {
            'class': 'table table-striped table-bordered table-hover',
            'id': 'usersTable'
        }
        model = User
        fields = ('checkbox', 'username', 'email', 'userprofilebase.generalpracticeuser.role')
        template_name = 'django_tables2/semantic.html'
