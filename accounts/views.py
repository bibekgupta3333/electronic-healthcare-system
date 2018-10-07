from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect
from django.http import JsonResponse

from common.functions import multi_getattr
from payment.models import OrganisationFee
from django_tables2 import RequestConfig

from .models import User, UserProfileBase, GeneralPracticeUser
from .models import GENERAL_PRACTICE_USER, CLIENT_USER
from .forms import NewGPForm, NewClientForm
from .tables import GPUserTable, ClientUserTable
from medi.settings.common import DEFAULT_FROM_EMAIL
from medi.settings.common import ACCOUNT_LINK, get_env_variable


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


@login_required(login_url='/accounts/login')
def reset_password(request):
    user = request.user
    user = User.objects.get(email=user.email)
    password = request.GET.get('password', '')
    user.set_password(password)
    user.save()
    send_mail(
        'Your account password has been changed',
        'Your account password has been changed by your manager. Password: {}'.format(password),
        DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        auth_user=get_env_variable('SENDGRID_USER'),
        auth_password=get_env_variable('SENDGRID_PASS'),
    )
    return JsonResponse({"success": "true"})


def manage_user(request):
    if request.method == "POST":
        cur_user = request.user
        cur_user = User.objects.get(username=cur_user.username)
        actionType = request.POST.get("actionType")
        emails = request.POST.getlist("users[]")
        if actionType == "Remove":
            for email in emails:
                user = User.objects.get(email=email)
                user.userprofilebase.delete()
            if len(emails) == 1:
                messages.success(request, "The selected user has been deleted.")
            else:
                messages.success(request, "Selected users have been deleted.")
            return JsonResponse({"success": "true"})
        elif actionType == "Change":
            role = request.POST.get("role")
            for email in emails:
                user = User.objects.get(email=email)
                if role == 0:
                    user.is_staff = True
                else:
                    user.is_staff = False
                user.save()

                if hasattr(cur_user.userprofilebase, 'generalpracticeuser'):
                    user.userprofilebase.generalpracticeuser.role = role
                    user.userprofilebase.generalpracticeuser.save()
                elif hasattr(cur_user.userprofilebase, 'clientuser'):
                    user.userprofilebase.clientuser.role = role
                    user.userprofilebase.clientuser.save()

            if len(emails) == 1:
                messages.success(request, "The role of selected user has been changed.")
            else:
                messages.success(request, "All the roles of the selected users have been changed.")
            return JsonResponse({"success": "true"})


def count_gpusers(queryset):
    all_count = queryset.count()
    pmanager_count = queryset.filter(userprofilebase__generalpracticeuser__role=0).count()
    gp_count = queryset.filter(userprofilebase__generalpracticeuser__role=1).count()
    sars_count = queryset.filter(userprofilebase__generalpracticeuser__role=2).count()
    overall_users_number = {
        'All': all_count,
        'Manager': pmanager_count,
        'GP': gp_count,
        'SARS': sars_count
    }
    return overall_users_number


def count_clientusers(queryset):
    all_count = queryset.count()
    admin_count = queryset.filter(is_staff=True).count()
    client_count = queryset.filter(is_staff=False).count()
    overall_users_number = {
        'All': all_count,
        'Admin': admin_count,
        'Client': client_count
    }
    return overall_users_number


@login_required(login_url='/accounts/login')
def view_users(request):
    header_title = "User Management"
    profiles = UserProfileBase.all_objects.all()
    user = request.user
    user = User.objects.get(username=user.username)

    if 'status' in request.GET:
        filter_type = request.GET.get('type', '')
        filter_status = request.GET.get('status', -1)
        if filter_status == 'undefined':
            filter_status = -1
        else:
            filter_status = int(filter_status)        
        if filter_type == 'undefined':
            filter_type = 'allType'
    else:
        filter_type = request.COOKIES.get('type', '')
        filter_status = int(request.COOKIES.get('status', -1))

    query_set = user.get_query_set_within_organisation()

    if filter_type == 'active':
        query_set = query_set.filter(userprofilebase__in=profiles.alive())
    elif filter_type == 'deactivated':
        query_set = query_set.filter(userprofilebase__in=profiles.dead())

    if hasattr(user.userprofilebase, 'generalpracticeuser'):
        overall_users_number = count_gpusers(query_set)
    elif hasattr(user.userprofilebase, 'clientuser'):
        overall_users_number = count_clientusers(query_set)

    if filter_status != -1:
        if hasattr(user.userprofilebase, 'generalpracticeuser'):
            query_set = query_set.filter(userprofilebase__generalpracticeuser__role=filter_status)
        elif hasattr(user.userprofilebase, 'clientuser'):
            query_set = query_set.filter(userprofilebase__clientuser__role=filter_status)

    if hasattr(user.userprofilebase, 'generalpracticeuser'):
        table = GPUserTable(query_set)
    elif hasattr(user.userprofilebase, 'clientuser'):
        table = ClientUserTable(query_set)
        
    table.order_by = request.GET.get('sort', '-created')
    RequestConfig(request, paginate={'per_page': 5}).configure(table)

    if hasattr(user.userprofilebase, 'generalpracticeuser'):
        newuser_form = NewGPForm()
        user_type = "gp"
    elif hasattr(user.userprofilebase, 'clientuser'):
        newuser_form = NewClientForm()
        user_type = "client"

    response = render(request, 'user_management/user_management.html', {
        'user': user,
        'table': table,
        'overall_users_number': overall_users_number,
        'header_title': header_title,
        'user_type': user_type
    })

    return response


@login_required(login_url='/accounts/login')
def create_user(request):
    header_title = "Add New User"

    cur_user = request.user
    cur_user = User.objects.get(username=cur_user.username)

    if request.method == 'POST':
        if hasattr(cur_user.userprofilebase, 'generalpracticeuser'):
            organisation = cur_user.userprofilebase.generalpracticeuser.organisation
            newuser_form = NewGPForm(request.POST)
        elif hasattr(cur_user.userprofilebase, 'clientuser'):
            organisation = cur_user.userprofilebase.clientuser.organisation
            newuser_form = NewClientForm(request.POST)
        
        user_role = request.POST.get("user_role")
        if not user_role:
            messages.warning(request, 'Please input all the fields properly.')
        elif newuser_form.is_valid():
            user = User.objects.filter(
                Q(username=newuser_form.cleaned_data['username']) |
                Q(email=newuser_form.cleaned_data['email'])
            )
            if not user.exists():
                user = User.objects.create(
                    first_name=newuser_form.cleaned_data['first_name'],
                    last_name=newuser_form.cleaned_data['last_name'],
                    username=newuser_form.cleaned_data['username'],
                    email=newuser_form.cleaned_data['email']
                )

                if hasattr(cur_user.userprofilebase, 'generalpracticeuser'):
                    user.type=GENERAL_PRACTICE_USER
                elif hasattr(cur_user.userprofilebase, 'clientuser'):
                    user.type=CLIENT_USER

                if user_role == "0":
                    user.is_staff = True
                
                user.set_password(newuser_form.cleaned_data['password'])
                user.save()
                to_email = newuser_form.cleaned_data['email']
                newuser = newuser_form.save(commit=False)
                newuser.organisation = organisation
                newuser.role = user_role
                newuser.user = user
                newuser.save()
                if newuser_form.cleaned_data['send_email']:
                    send_mail(
                        'New Account',
                        'You have a new Account. Click here {} to see it.'.format(ACCOUNT_LINK),
                        DEFAULT_FROM_EMAIL,
                        [to_email],
                        fail_silently=False,
                        auth_user=get_env_variable('SENDGRID_USER'),
                        auth_password=get_env_variable('SENDGRID_PASS'),
                    )
                messages.success(request, 'New User Account created successfully.')
                return redirect("accounts:view_users")
            else:
                messages.warning(request, 'User Account Existing In Database')
        else:
            messages.warning(request, 'Please input all the fields properly.')
    
    if hasattr(cur_user.userprofilebase, 'generalpracticeuser'):
        newuser_form = NewGPForm()
        user_type = "gp"
    elif hasattr(cur_user.userprofilebase, 'clientuser'):
        newuser_form = NewClientForm()
        user_type = "client"

    response = render(request, 'user_management/new_user.html', {
        'header_title': header_title,
        'newuser_form': newuser_form,
        'user_type': user_type
    })

    return response
    