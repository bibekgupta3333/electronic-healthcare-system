from django.contrib import admin
from .models import OrganisationFee, InstructionVolumeFee
from .forms import OrganisationFeeForm, InstructionVolumeFeeForm


class OrganisationFeeAdmin(admin.ModelAdmin):
    form = OrganisationFeeForm
    raw_id_fields = ('gp_practice', )

    class Media:
        js = ('js/custom_admin/payment_fee_admin.js', )

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        obj.hard_delete()


class InstructionVolumeFeeAdmin(admin.ModelAdmin):
    form = InstructionVolumeFeeForm
    raw_id_fields = ('client_organisation', )


admin.site.register(OrganisationFee, OrganisationFeeAdmin)
admin.site.register(InstructionVolumeFee, InstructionVolumeFeeAdmin)
