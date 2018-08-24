from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django_tables2 import RequestConfig
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from .models import Instruction
from .tables import InstructionTable
from .model_choices import *
from .filters import InstructionFilter


def count_instructions():
    all_count = Instruction.objects.all().count()
    new_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_NEW).count()
    progress_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_PROGRESS).count()
    overdue_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_OVERDUE).count()
    complete_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_COMPLETE).count()
    rejected_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_REJECT).count()
    overall_instructions_number = {
        'All': all_count,
        'New': new_count,
        'In Progress': progress_count,
        'Overdue': overdue_count,
        'Complete': complete_count,
        'Rejected': rejected_count
    }
    return overall_instructions_number


@login_required(login_url='/admin')
def instruction_pipeline_view(request):
    header_title = "Instructions Pipeline"
    user = request.user
    filter_type = request.GET.get('type', '')
    filter_status = int(request.GET.get('status', -1))
    if filter_type and filter_type != 'allType':
        query_set = Instruction.objects.filter(type=filter_type,)
    else:
        query_set = Instruction.objects.filter()

    if filter_status != -1:
        query_set = query_set.filter(status=filter_status)

    table = InstructionTable(query_set)

    overall_instructions_number = count_instructions()

    table.order_by = request.GET.get('sort', 'created')
    RequestConfig(request, paginate={'per_page': 5}).configure(table)
    return render(request, 'instructions/instruction_views.html', {
        'user': user,
        'table': table,
        'overall_instructions_number': overall_instructions_number,
        'header_title': header_title
    })
