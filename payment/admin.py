from django.contrib import admin
from .models import OrganisationFee
from .forms import OrganisationFeeForm


class OrganisationFeeAdmin(admin.ModelAdmin):
    form = OrganisationFeeForm
    fields = (
        'gp_practice',
        'max_day_lvl_1', 'max_day_lvl_2', 'max_day_lvl_3',
        'amount_rate_lvl_1', 'amount_rate_lvl_2', 'amount_rate_lvl_3'
    )

    class Media:
        js = ('js/custom_admin/payment_fee_admin.js', )


    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        obj.hard_delete()

admin.site.register(OrganisationFee, OrganisationFeeAdmin)
