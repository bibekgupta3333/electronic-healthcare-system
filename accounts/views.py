from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from common.functions import multi_getattr
from payment.models import OrganisationFee


@login_required(login_url='/accounts/login')
def account_view(request):
    header_title = 'Account'
    user = request.user
    organisation = multi_getattr(user, 'userprofilebase.generalpracticeuser.organisation', default=None)
    organisation_fee = OrganisationFee.objects.filter(gp_practice=organisation).first()
    organisation_fee_data = list()

    if organisation_fee:
        organisation_fee_data.append('0-{max_day_level_1} days @ £{amount_rate_level_1}'.format(
            max_day_level_1=organisation_fee.max_day_lvl_1,
            amount_rate_level_1=organisation_fee.amount_rate_lvl_1)
        )
        organisation_fee_data.append('{min_day_level_2}-{max_day_level_2} days @ £{amount_rate_level_2}'.format(
            min_day_level_2=organisation_fee.max_day_lvl_1+1,
            max_day_level_2=organisation_fee.max_day_lvl_2,
            amount_rate_level_2=organisation_fee.amount_rate_lvl_2)
        )
        organisation_fee_data.append('{max_day_level_3} days or more @ £{amount_rate_level_3}'.format(
            max_day_level_3=organisation_fee.max_day_lvl_3,
            amount_rate_level_3=organisation_fee.amount_rate_lvl_3)
        )

    return render(request, 'accounts/accounts_view.html', {
        'header_title': header_title,
        'organisation_fee_data': organisation_fee_data,
    })