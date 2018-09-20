from django.contrib import admin
from .models import OrganisationFee
from .forms import OrganisationFeeForm


class OrganisationFeeAdmin(admin.ModelAdmin):
    form = OrganisationFeeForm


admin.site.register(OrganisationFee, OrganisationFeeAdmin)
