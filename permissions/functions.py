from django.shortcuts import redirect
from accounts.models import User, GeneralPracticeUser, MEDIDATA_USER, GENERAL_PRACTICE_USER
from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_REJECT, INSTRUCTION_STATUS_COMPLETE,\
        INSTRUCTION_STATUS_PROGRESS, INSTRUCTION_STATUS_NEW
from django.shortcuts import get_object_or_404
from permissions.models import InstructionPermission
from permissions.model_choices import INSTRUCTION_PERMISSIONS
from django.contrib.auth.models import Group, Permission


decorator_with_arguments = lambda decorator: lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)


def check_status_with_url(is_valid, path, status):
    if 'view-reject' in path and status != INSTRUCTION_STATUS_REJECT:
        is_valid = False
    elif 'final-report' in path and status not in [INSTRUCTION_STATUS_COMPLETE, INSTRUCTION_STATUS_PROGRESS]:
        is_valid = False
    elif 'patient-emis-number' in path and status != INSTRUCTION_STATUS_NEW:
        is_valid = False
    elif 'edit' in path and status != INSTRUCTION_STATUS_PROGRESS:
        is_valid = False
    elif 'review-instruction' in path and status not in [INSTRUCTION_STATUS_NEW, INSTRUCTION_STATUS_PROGRESS]:
        is_valid = False
    elif 'consent-contact' in path and status not in [INSTRUCTION_STATUS_NEW, INSTRUCTION_STATUS_PROGRESS]:
        is_valid = False
    return is_valid


def check_permission(func):
    def check_and_call(request, *args, **kwargs):
        instruction_id = kwargs.get("instruction_id")
        if not instruction_id:
            if request.method == "GET" and request.GET.get('instruction_id'):
                instruction_id = request.GET.get('instruction_id')
            else:
                return func(request, *args, **kwargs)
        user = User.objects.get(pk=request.user.pk)
        instruction = get_object_or_404(Instruction, pk=instruction_id)
        client_user = instruction.client_user
        gp_user = instruction.gp_user
        patient = instruction.patient
        gp_practice = instruction.gp_practice
        instruction_type = instruction.get_type()
        is_valid = False
        if client_user and user.pk == client_user.user.pk:
            is_valid = True
        elif gp_user and user.pk == gp_user.user.pk:
            is_valid = True
        elif patient and user.pk == patient.user.pk:
            is_valid = True
        elif instruction_type == 'SARS' and request.user.has_perm('instructions.process_sars') and\
            user.userprofilebase.generalpracticeuser.organisation == gp_practice:
            is_valid = True

        if hasattr(user.userprofilebase, "generalpracticeuser") and\
            user.userprofilebase.generalpracticeuser.role == GeneralPracticeUser.PRACTICE_MANAGER and\
            user.userprofilebase.generalpracticeuser.organisation == gp_practice:
            is_valid = True

        if hasattr(user.userprofilebase, "generalpracticeuser") and not gp_user and(\
            "review-instruction" in request.path or "patient-emis-number" in request.path or\
            "consent-contact" in request.path):
            is_valid = True

        if hasattr(user.userprofilebase, "clientuser") and client_user and\
            client_user.organisation == user.userprofilebase.clientuser.organisation:
            is_valid = True

        if is_valid:
            is_valid = check_status_with_url(is_valid, request.path, instruction.status)

        if not is_valid:
            return redirect('instructions:view_pipeline')
        return func(request, *args, **kwargs)
    return check_and_call


@decorator_with_arguments
def access_user_management(func, perm):
    def check_and_call(request, *args, **kwargs):
        if not request.user.has_perm(perm):
            return redirect('instructions:view_pipeline')
        return func(request, *args, **kwargs)
    return check_and_call


def access_template(func):
    def check_and_call(request, *args, **kwargs):
        if not hasattr(request.user.userprofilebase, 'clientuser'):
            return redirect('instructions:view_pipeline')
        return func(request, *args, **kwargs)
    return check_and_call


def generate_gp_permission(organisation):
    for role_choices in GeneralPracticeUser.ROLE_CHOICES:
        role, label = role_choices
        if role != '':
            permission, created = InstructionPermission.objects.get_or_create(
                role=role,
                organisation=organisation
            )
            group, created = Group.objects.get_or_create(
                name='%s : %s'%(permission.get_role_display(),organisation.__str__())
            )
            set_default_gp_perm(group, role)
            permission.group = group
            permission.save()
            permission.allocate_permission_to_gp()


def set_default_gp_perm(group, role):
    for codename in INSTRUCTION_PERMISSIONS:
        if codename == 'view_summary_report' and role != GeneralPracticeUser.PRACTICE_MANAGER: continue
        perm = Permission.objects.get(codename=codename)
        group.permissions.add(perm)
    group.save()


@decorator_with_arguments
def check_user_type(func, user_type):
    def check_and_call(request, *args, **kwargs):
        if request.user.type != user_type:
            return redirect('instructions:view_pipeline')
        return func(request, *args, **kwargs)
    return check_and_call
