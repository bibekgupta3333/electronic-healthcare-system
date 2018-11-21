from django.shortcuts import redirect
from accounts.models import User, GeneralPracticeUser, MEDIDATA_USER, GENERAL_PRACTICE_USER
from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_REJECT, INSTRUCTION_STATUS_COMPLETE,\
        INSTRUCTION_STATUS_PROGRESS, INSTRUCTION_STATUS_NEW
from django.shortcuts import get_object_or_404


decorator_with_arguments = lambda decorator: lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)


def check_status_with_url(is_valid, path, status):
    if 'view-reject' in path and status != INSTRUCTION_STATUS_REJECT:
        is_valid = False
    elif 'final-report' in path and status != INSTRUCTION_STATUS_COMPLETE:
        is_valid = False
    elif 'patient-emis-number' in path and status != INSTRUCTION_STATUS_NEW:
        is_valid = False
    elif 'edit' in path and status != INSTRUCTION_STATUS_PROGRESS:
        is_valid = False
    elif 'review-instruction' in path and status != INSTRUCTION_STATUS_NEW:
        is_valid = False
    elif 'consent-contact' in path and status not in [INSTRUCTION_STATUS_NEW, INSTRUCTION_STATUS_PROGRESS]:
        is_valid = False
    return is_valid

def check_permission(func):
    def check_and_call(request, *args, **kwargs):
        instruction_id = kwargs["instruction_id"]
        user = User.objects.get(pk=request.user.pk)
        instruction = get_object_or_404(Instruction, pk=instruction_id)
        client_user = instruction.client_user
        gp_user = instruction.gp_user
        patient = instruction.patient
        gp_practice = instruction.gp_practice
        is_valid = False
        if client_user and user.pk == client_user.user.pk:
            is_valid = True
        elif gp_user and user.pk == gp_user.user.pk:
            is_valid = True
        elif patient and user.pk == patient.user.pk:
            is_valid = True

        if hasattr(user.userprofilebase, "generalpracticeuser") and\
            user.userprofilebase.generalpracticeuser.role == GeneralPracticeUser.PRACTICE_MANAGER and\
            user.userprofilebase.generalpracticeuser.organisation == gp_practice:
            is_valid = True

        if hasattr(user.userprofilebase, "generalpracticeuser") and not gp_user and(\
            "review-instruction" in request.path or "patient-emis-number" in request.path or\
            "consent-contact" in request.path):
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
