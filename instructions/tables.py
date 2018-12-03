import django_tables2 as tables
from accounts import models
from .models import Instruction
from django.utils.html import format_html
from django.urls import reverse
from permissions.templatetags.get_permissions import view_complete_report


class InstructionTable(tables.Table):
    checkbox = tables.CheckBoxColumn(attrs={'id': 'check_all'})
    patient_information = tables.Column()
    status = tables.Column()
    user = None

    class Meta:
        attrs = {
            'class': 'table table-striped table-bordered table-hover',
            'id': 'instructionsTable'
        }
        model = Instruction
        fields = ('checkbox', 'client_user', 'gp_practice', 'type', 'patient_information', 'gp_user', 'initial_monetary_value', 'created', 'status')
        template_name = 'django_tables2/semantic.html'
        row_attrs = {
            'data-id': lambda record: record.pk
        }

    def before_render(self, request):
        if request.user.type == models.CLIENT_USER:
            self.columns.hide('client_user')
        elif request.user.type == models.GENERAL_PRACTICE_USER:
            self.columns.hide('gp_practice')
        self.user = request.user

    def render_client_user(self, value):
        user = value.user
        trading_name = ""
        if hasattr(user, 'userprofilebase') and hasattr(user.userprofilebase, 'clientuser') and\
            user.userprofilebase.organisation:
            trading_name = user.userprofilebase.clientuser.organisation.trading_name
        return format_html(trading_name)

    def render_patient_information(self, value):
        return format_html(
            '{} {} {} <br><b>NHS: </b>{}', value.get_patient_title_display(), value.patient_first_name, value.patient_last_name, value.patient_nhs_number
        )

    def render_status(self, value, record):
        STATUS_DICT = {
            'New': 'badge-primary',
            'In Progress': 'badge-warning',
            'Overdue': 'badge-info',
            'Completed': 'badge-success',
            'Rejected': 'badge-danger'
        }
        url = 'instructions:review_instruction'
        view_report = view_complete_report(self.user.id, record.pk)
        if value == 'Completed':
            if self.user.type != models.GENERAL_PRACTICE_USER:
                url = 'medicalreport:final_report'
            elif view_report:
                url = 'medicalreport:final_report'
            else:
                return format_html('<a><h5><span class="status badge {}">{}</span></h5></a>', STATUS_DICT[value], value)
        elif value == 'Rejected':
            url = 'instructions:view_reject'
        elif value == 'In Progress' and self.user.type == models.GENERAL_PRACTICE_USER and not record.saved:
            url = 'medicalreport:edit_report'
        elif value == 'In Progress' and self.user.type == models.GENERAL_PRACTICE_USER and record.saved:
            url = 'instructions:consent_contact'
            return format_html('<a href='+reverse(url, args=[record.pk, record.patient_information.patient_emis_number])+'><h5><span class="status badge {}">{}</span></h5></a>', STATUS_DICT[value], value)
        return format_html('<a href='+reverse(url, args=[record.pk])+'><h5><span class="status badge {}">{}</span></h5></a>', STATUS_DICT[value], value)


