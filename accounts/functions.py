from .models import User, UserProfileBase, GeneralPracticeUser
from .models import GENERAL_PRACTICE_USER, CLIENT_USER, MEDIDATA_USER
from django.contrib import messages
from django.core.mail import send_mail
from .forms import NewGPForm, NewClientForm
from .tables import UserTable
from common.functions import get_env_variable
from django.conf import settings
DEFAULT_FROM = settings.DEFAULT_FROM


def reset_password(request):
    emails = request.POST.getlist("users[]")
    PASSWORD = 'medi2018'
    user_cnt = len(emails)
    for email in emails:
        user = User.objects.get(email=email)
        user.set_password(PASSWORD)
        user.save()
        # send_mail(
        #     'Your account password has been changed',
        #     'Your account password has been changed by your manager. Password: {}'.format(PASSWORD),
        #     DEFAULT_FROM,
        #     [user.email],
        #     fail_silently=False,
        #     auth_user=get_env_variable('SENDGRID_USER'),
        #     auth_password=get_env_variable('SENDGRID_PASS'),
        # )

    if user_cnt == 1:
        messages.success(request, "The selected user's password has been reset. Password: {}".format(PASSWORD))
    else:
        messages.success(request, "All the passwords of the selected users have been reset. Password: {}".format(PASSWORD))

def change_role(request):
    cur_user = request.user
    cur_user = User.objects.get(username=cur_user.username)
    role = request.POST.get("role")
    emails = request.POST.getlist("users[]")
    user_cnt = len(emails)
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

    if user_cnt == 1:
        messages.success(request, "The role of selected user has been changed.")
    else:
        messages.success(request, "All the roles of the selected users have been changed.")

def remove_user(request):
    emails = request.POST.getlist("users[]")
    user_cnt = len(emails)
    for email in emails:
        user = User.objects.get(email=email)
        user.userprofilebase.delete()

    if user_cnt == 1:
        messages.success(request, "The selected user has been deleted.")
    else:
        messages.success(request, "Selected users have been deleted.")

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


def count_users(queryset):
    all_count = queryset.count()
    admin_count = queryset.filter(userprofilebase__clientuser__role=0).count()
    client_count = queryset.filter(userprofilebase__clientuser__role=1).count()
    pmanager_count = queryset.filter(userprofilebase__generalpracticeuser__role=0).count()
    gp_count = queryset.filter(userprofilebase__generalpracticeuser__role=1).count()
    sars_count = queryset.filter(userprofilebase__generalpracticeuser__role=2).count()
    medi_count = queryset.filter(type=MEDIDATA_USER).count()
    overall_users_number = {
        'All': all_count,
        'Admin': admin_count,
        'Client': client_count,
        'Manager': pmanager_count,
        'GP': gp_count,
        'SARS': sars_count,
        'Medidata': medi_count
    }
    return overall_users_number


def get_table_data(user, query_set, filter_query):
    if hasattr(user.userprofilebase, 'generalpracticeuser'):
        return {
            "user_type": "gp",
            "overall_users_number": count_gpusers(query_set),
            "table": UserTable(filter_query)
        }
    elif hasattr(user.userprofilebase, 'clientuser'):
        return {
            "user_type": "client",
            "overall_users_number": count_clientusers(query_set),
            "table": UserTable(filter_query)
        }
    elif hasattr(user.userprofilebase, 'medidatauser'):
        return {
            "user_type": "medidata",
            "overall_users_number": count_users(query_set),
            "table": UserTable(filter_query)
        }


def get_post_new_user_data(cur_user, request, user_role):
    if hasattr(cur_user.userprofilebase, 'generalpracticeuser'):
        return {
            "organisation": cur_user.userprofilebase.generalpracticeuser.organisation,
            "newuser_form": NewGPForm(request.POST),
            "user_type": GENERAL_PRACTICE_USER,
            "is_staff": True if user_role == '0' else False
        }
    elif hasattr(cur_user.userprofilebase, 'clientuser'):
        return {
            "organisation": cur_user.userprofilebase.clientuser.organisation,
            "newuser_form": NewClientForm(request.POST),
            "user_type": CLIENT_USER,
            "is_staff": True if user_role == '0' else False
        }


def get_user_type_form(cur_user):
    if hasattr(cur_user.userprofilebase, 'generalpracticeuser'):
        return {
            "newuser_form": NewGPForm(),
            "user_type": "gp"
        }
    elif hasattr(cur_user.userprofilebase, 'clientuser'):
        return {
            "newuser_form": NewClientForm(),
            "user_type": "client"
        }
