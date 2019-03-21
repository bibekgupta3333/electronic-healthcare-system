from django.contrib import admin
from .models import OrganisationFeeRate, InstructionVolumeFee, GpOrganisationFee
from .forms import OrganisationFeeForm, InstructionVolumeFeeForm
from common.import_export import CustomExportMixin


class OrganisationFeeAdmin(CustomExportMixin, admin.ModelAdmin):
    form = OrganisationFeeForm

    class Media:
        js = ('js/custom_admin/payment_fee_admin.js', )

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        obj.hard_delete()


class GpOrganisationFeeAdmin(admin.ModelAdmin):
    raw_id_fields = ['gp_practice', ]
    list_filter = (
        ('gp_practice', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'gp_practice', 'organisation_fee__amount_rate_lvl_1', 'organisation_fee__amount_rate_lvl_2'
    )
    list_display = (
        'gp_practice', 'get_amount_rate_lvl_1', 'get_amount_rate_lvl_2'
    )

    def get_amount_rate_lvl_1(self, obj):
        return obj.organisation_fee.amount_rate_lvl_1

    get_amount_rate_lvl_1.admin_order_field = 'organisation_fee'
    get_amount_rate_lvl_1.short_description = 'Earnings for top payment band'

    def get_amount_rate_lvl_2(self, obj):
        return obj.organisation_fee.amount_rate_lvl_2

    get_amount_rate_lvl_2.admin_order_field = 'organisation_fee'
    get_amount_rate_lvl_2.short_description = 'Earnings for lowest payment band'


class InstructionVolumeFeeClientAdmin(admin.ModelAdmin):
    form = InstructionVolumeFeeForm
    raw_id_fields = ('client_organisation', )
    fields = (
        'client_organisation', 'max_volume_band_lowest', 'max_volume_band_low', 'max_volume_band_medium', 'max_volume_band_top',
        'fee_rate_lowest', 'fee_rate_low', 'fee_rate_medium', 'fee_rate_top', 'vat'
    )


admin.site.register(OrganisationFeeRate, OrganisationFeeAdmin)
admin.site.register(InstructionVolumeFee, InstructionVolumeFeeClientAdmin)
admin.site.register(GpOrganisationFee, GpOrganisationFeeAdmin)

