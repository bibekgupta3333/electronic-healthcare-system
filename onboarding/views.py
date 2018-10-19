from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login')
def emr_setup(request):
    return HttpResponse('Feature coming soon')
