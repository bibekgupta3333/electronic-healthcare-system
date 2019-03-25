import django_tables2 as tables
from .models import User
import django_tables2 as tables
from accounts import models
from instructions.models import Instruction
from django.utils.html import format_html
from django.urls import reverse
from permissions.templatetags.get_permissions import view_complete_report
from django.template.defaultfilters import date


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


class AccountTable(tables.Table):
    patient_information = tables.Column()
    client_ref = tables.Column(empty_values=(), default='-')
    instruction_information = tables.Column(empty_values=(), default='-')
    PDF_copy_of_invoice = tables.Column(empty_values=(), default='-')
    # created = tables.DateTimeColumn(format='D j M Y')
    user = None

    class Meta:
        attrs = {
            'class': 'table table-striped table-bordered table-hover',
            'id': 'instructionsTable'
        }
        model = Instruction
        fields = (
            'client_ref', 'medi_ref', 'patient_information', 'cost', 'type',
            'instruction_information', 'PDF_copy_of_invoice'
        )
        template_name = 'django_tables2/semantic.html'
        row_attrs = {
            'data-id': lambda record: record.pk
        }

    def before_render(self, request):
        self.user = request.user

    def render_type(self, record):
        type = record.type
        type_catagory = record.type_catagory
        if type_catagory:
            return format_html(
                '<strong>{}</strong><br> <font size="-1">( {} )</font>', type, type_catagory
            )
        else:
            return format_html(
                '<strong>{}</strong>', type
            )

    def render_client_ref(self, record):
        client_ref = record.your_ref
        if not client_ref:
            client_ref = "—"
        return format_html(client_ref)

    def render_patient_information(self, value):
        return format_html(
            '{} {} {} <br><b>NHS: </b>{}', value.get_patient_title_display(), value.patient_first_name, value.patient_last_name, value.patient_nhs_number
        )

    def render_cost(self, record):
        if self.user.type == models.CLIENT_USER:
            return record.gp_earns + record.medi_earns

    def render_instruction_information(self, record):
        gp_practice = record.gp_practice
        client_user = record.client_user
        patient = record.patient_information
        snomed_detail = ''
        for snomed in record.get_inner_selected_snomed_concepts():
            if snomed_detail == '':
                snomed_detail = snomed
            else:
                snomed_detail = snomed_detail + ', ' + snomed
        
        if record.fee_calculation_start_date and record.completed_signed_off_timestamp:
            calculate_date = record.completed_signed_off_timestamp - record.fee_calculation_start_date
            result_date = '\nresult: ' + str(calculate_date.days) + ' days.'
            date_detail = str(date(record.fee_calculation_start_date, "d/m/Y")) + " - " + str(date(record.completed_signed_off_timestamp, "d/m/Y"))
            show_date = " ".join([str(date_detail), str(result_date)])
        else:
            show_date = 'None'

        return format_html(
            "<a href='#infoModal'>"
            "<span class='btn btn-primary btn-block btn-sm infoDetailButton'"
            "data-ins_number='{}'"
            "data-patient_name='{}'"
            "data-patient_dob='{}'"
            "data-patient_address='{}'"
            "data-patient_nhs='{}'"
            "data-detail_request='{}'"
            "data-detail_date='{}'"
            ">View</span>"
            "</a>",
            record.id,
            patient.get_full_name(),
            patient.patient_dob,
            ' '.join([
                    patient.patient_address_number,
                    patient.patient_address_line1,
                    patient.patient_address_line2,
                    patient.patient_address_line3,
                    patient.patient_city,
                    patient.patient_county
                ]),
            patient.patient_nhs_number if patient.patient_nhs_number else '-',
            snomed_detail if not snomed_detail == '' else 'None',
            show_date
        )

    def render_PDF_copy_of_invoice(self, record):
        return format_html(
            "<a href='#invoiceModal' class='btn btn-success btn-block btn-sm invoiceDetailButton' role='button'>"
            "View</a>"
        )