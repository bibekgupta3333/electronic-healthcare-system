from django.contrib import admin
from .models import PatientReportAuth, ThirdPartyAuthorisation, UnsupportedAttachment
from django.core.mail import send_mail


class ThirdPartyAuthorisationAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):

        if obj.expired:
            send_mail(
                'Medical Report Authorisation',
                'Your access on SAR report from {patient_name} has been expired. Please contact {patient_name}'.format(
                    patient_name=obj.patient_report_auth.patient.user.first_name,
                ),
                'Medidata',
                [obj.email],
                fail_silently=True
            )
            super().save_model(request, obj, form, change)


class UnsupportedAttachmentAdmin(admin.ModelAdmin):

    list_display = ('instruction', 'file_name', 'file_type')

admin.site.register(PatientReportAuth)
admin.site.register(ThirdPartyAuthorisation, ThirdPartyAuthorisationAdmin)
admin.site.register(UnsupportedAttachment, UnsupportedAttachmentAdmin)
