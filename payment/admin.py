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


class InstructionVolumeFeeClientAdmin(admin.ModelAdmin):
    form = InstructionVolumeFeeForm
    raw_id_fields = ('client_organisation', )
    fields = (
        'client_organisation', 'max_volume_band_lowest', 'max_volume_band_low', 'max_volume_band_medium', 'max_volume_band_top',
        'fee_rate_lowest', 'fee_rate_low', 'fee_rate_medium', 'fee_rate_top', 'vat'
    )


admin.site.register(OrganisationFee, OrganisationFeeAdmin)
admin.site.register(InstructionVolumeFee, InstructionVolumeFeeClientAdmin)

