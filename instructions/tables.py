import django_tables2 as tables
from accounts import models
from .models import Instruction
from django.utils.html import format_html
from django.urls import reverse


class InstructionTable(tables.Table):
    checkbox = tables.CheckBoxColumn(attrs={'id': 'check_all'})
    patient = tables.Column()
    status = tables.Column()

    class Meta:
        attrs = {
            'class': 'table table-striped table-bordered table-hover',
            'id': 'instructionsTable'
        }
        model = Instruction
        fields = ('checkbox', 'client_user', 'gp_practice', 'type', 'patient', 'gp_user', 'initial_monetary_value', 'created', 'status')
        template_name = 'django_tables2/semantic.html'
        row_attrs = {
            'data-id': lambda record: record.pk
        }

    def before_render(self, request):
        if request.user.type == models.CLIENT_USER:
            self.columns.hide('client_user')
        elif request.user.type == models.GENERAL_PRACTICE_USER:
            self.columns.hide('gp_practice')

    def render_patient(self, value):
        return format_html('{} {} <br><b>NHS: </b>{}', value.user.first_name, value.user.last_name, value.nhs_number)

    def render_status(self, value, record):
        STATUS_DICT = {
            'New':'badge-primary',
            'In Progress': 'badge-warning',
            'Overdue': 'badge-info',
            'Complete': 'badge-success',
            'Reject': 'badge-danger'
        }
        if value == 'Complete':
            return format_html('<a href='+reverse('medicalreport:final_report', args=[record.pk])+'><h5><span class="status badge {}">{}</span></h5></a>', STATUS_DICT[value], value)
        else:
            return format_html('<a href='+reverse('medicalreport:edit_report', args=[record.pk])+'><h5><span class="status badge {}">{}</span></h5></a>', STATUS_DICT[value], value)


