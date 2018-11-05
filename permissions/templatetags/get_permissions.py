from django import template
from accounts.models import GENERAL_PRACTICE_USER, User
from permissions.models import InstructionPermission
from instructions.models import Instruction
from instructions.model_choices import AMRA_TYPE
register = template.Library()


def create_amra(user_id):
    permission = False
    user = User.objects.get(pk=user_id)
    if user.type != GENERAL_PRACTICE_USER:
        return permission
    role = user.userprofilebase.generalpracticeuser.role
    organisation = user.userprofilebase.generalpracticeuser.organisation
    instruction_permission = InstructionPermission.objects.filter(role=role, organisation_id=organisation.id).first()
    if instruction_permission:
        permission = instruction_permission.create_amra
    return permission

def create_sars(user_id):
    permission = False
    user = User.objects.get(pk=user_id)
    if user.type != GENERAL_PRACTICE_USER:
        return permission
    role = user.userprofilebase.generalpracticeuser.role
    organisation = user.userprofilebase.generalpracticeuser.organisation
    instruction_permission = InstructionPermission.objects.filter(role=role, organisation_id=organisation.id).first()
    if instruction_permission:
        permission = instruction_permission.create_sars
    return permission

def reject_instruction(user_id, instruction_id):
    permission = False
    user = User.objects.get(pk=user_id)
    instruction = Instruction.objects.get(pk=instruction_id)
    if user.type != GENERAL_PRACTICE_USER:
        return permission
    role = user.userprofilebase.generalpracticeuser.role
    organisation = user.userprofilebase.generalpracticeuser.organisation
    instruction_permission = InstructionPermission.objects.filter(role=role, organisation_id=organisation.id).first()
    if instruction_permission and instruction:
        if instruction.type == AMRA_TYPE:
            permission = instruction_permission.reject_amra
        else:
            permission = instruction_permission.reject_sars
    return permission

def process_instruction(user_id, instruction_id):
    permission = False
    user = User.objects.get(pk=user_id)
    instruction = Instruction.objects.get(pk=instruction_id)
    if user.type != GENERAL_PRACTICE_USER:
        return permission
    role = user.userprofilebase.generalpracticeuser.role
    organisation = user.userprofilebase.generalpracticeuser.organisation
    instruction_permission = InstructionPermission.objects.filter(role=role, organisation_id=organisation.id).first()
    if instruction_permission and instruction:
        if instruction.type == AMRA_TYPE:
            permission = instruction_permission.process_amra
        else:
            permission = instruction_permission.process_sars
    return permission

def allocate_instruction(user_id):
    permission = False
    user = User.objects.get(pk=user_id)
    if user.type != GENERAL_PRACTICE_USER:
        return permission
    role = user.userprofilebase.generalpracticeuser.role
    organisation = user.userprofilebase.generalpracticeuser.organisation
    instruction_permission = InstructionPermission.objects.filter(role=role, organisation_id=organisation.id).first()
    if instruction_permission:
        permission = instruction_permission.allocate_gp
    return permission

def sign_off_report(user_id, instruction_id):
    permission = False
    user = User.objects.get(pk=user_id)
    instruction = Instruction.objects.get(pk=instruction_id)
    if user.type != GENERAL_PRACTICE_USER:
        return permission
    role = user.userprofilebase.generalpracticeuser.role
    organisation = user.userprofilebase.generalpracticeuser.organisation
    instruction_permission = InstructionPermission.objects.filter(role=role, organisation_id=organisation.id).first()
    if instruction_permission and instruction:
        if instruction.type == AMRA_TYPE:
            permission = instruction_permission.sign_off_amra
        else:
            permission = instruction_permission.sign_off_sars
    return permission

def view_complete_report(user_id, instruction_id):
    permission = False
    user = User.objects.get(pk=user_id)
    instruction = Instruction.objects.get(pk=instruction_id)
    if user.type != GENERAL_PRACTICE_USER:
        return permission
    role = user.userprofilebase.generalpracticeuser.role
    organisation = user.userprofilebase.generalpracticeuser.organisation
    instruction_permission = InstructionPermission.objects.filter(role=role, organisation_id=organisation.id).first()
    if instruction_permission and instruction:
        if instruction.type == AMRA_TYPE:
            permission = instruction_permission.view_completed_amra
        else:
            permission = instruction_permission.view_completed_sars
    return permission

register.filter('create_amra', create_amra)
register.filter('create_sars', create_sars)
register.filter('reject_instruction', reject_instruction)
register.filter('process_instruction', process_instruction)
register.filter('allocate_instruction', allocate_instruction)
register.filter('sign_off_report', sign_off_report)
