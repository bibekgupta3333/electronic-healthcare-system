import django_tables2 as tables
from .models import User


class UserTable(tables.Table):
    chkbox = tables.CheckBoxColumn(attrs={'id': 'check_all', "th__input": {"onclick": "toggleUserTableHeadChk(this)"}}, accessor="email")
    role = tables.Column(verbose_name='Role', accessor="userprofilebase")
    organisation = tables.Column(verbose_name='Organisation', accessor="userprofilebase")
    email = tables.Column(verbose_name='Email', accessor='email')
    name = tables.Column(verbose_name='Name', accessor='userprofilebase')

    class Meta:
        attrs = {
            'class': 'table table-striped table-bordered table-hover',
            'id': 'usersTable'
        }
        model = User
        fields = ('chkbox', 'email', 'name', 'organisation', 'role')
        template_name = 'django_tables2/semantic.html'

    def render_name(self, value):
        return "%s %s"%(value.get_title_display(), value.user.get_full_name())

    def render_role(self, value):
        return value.user.get_short_my_role()

    def render_organisation(self, value):
        if hasattr(value, 'generalpracticeuser'):
            return value.generalpracticeuser.organisation.__str__()
        elif hasattr(value, 'medidatauser'):
            return value.medidatauser.organisation.__str__()
        else:
            return value.clientuser.organisation.__str__()
