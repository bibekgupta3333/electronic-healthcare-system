import django_tables2 as tables
from .models import User


class UserTable(tables.Table):
    chkbox = tables.CheckBoxColumn(attrs={'id': 'check_all'}, accessor="email")
    role = tables.Column(verbose_name='Role', accessor="userprofilebase")
    organisation = tables.Column(verbose_name='Organisation', accessor="userprofilebase")

    class Meta:
        attrs = {
            'class': 'table table-striped table-bordered table-hover',
            'id': 'usersTable'
        }
        model = User
        fields = ('chkbox', 'username', 'email', 'organisation', 'role')
        template_name = 'django_tables2/semantic.html'

    def render_role(self, value):
        return value.user.get_short_my_role()

    def render_organisation(self, value):
        if hasattr(value, 'generalpracticeuser'):
            return value.generalpracticeuser.organisation.__str__()
        elif hasattr(value, 'medidatauser'):
            return value.medidatauser.organisation.__str__()
        else:
            return value.clientuser.organisation.__str__()
