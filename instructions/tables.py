import django_tables2 as tables
from .models import Instruction
from django.utils.html import format_html


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
        fields = ('checkbox', 'client_user', 'type', 'patient', 'gp_user', 'initial_monetary_value', 'created', 'status')
        template_name = 'django_tables2/semantic.html'
        row_attrs = {
            'data-id': lambda record: record.pk
        }

    def render_patient(self, value):
        return format_html('{} {} <br><b>NHS: </b>{}', value.user.first_name, value.user.last_name, value.nhs_number)

    def render_status(self, value):
        STATUS_DICT = {
            'New':'badge-primary',
            'In Progress': 'badge-warning',
            'Overdue': 'badge-info',
            'Complete': 'badge-success',
            'Reject': 'badge-danger'
        }
        return format_html('<h5><span class="status badge {}">{}</span></h5>', STATUS_DICT[value], value)

