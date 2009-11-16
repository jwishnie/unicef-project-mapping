import uuid
import os, stat

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from maplayers.models import Project

from maplayers.constants import GROUPS
from maplayers.forms import UserForm, ChangePasswordForm


@login_required
def user_registration(request):
    user_groups = [group.name for group in request.user.groups.all()]
    if not GROUPS.ADMINS in user_groups:
        return HttpResponseRedirect('/permission_denied/add_user/not_admin')
        
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            _create_user(form)
            return HttpResponseRedirect('/user_registration/success/')
        else:
            return _user_registration_response(request, form)
    else:
        form = UserForm()
        return _user_registration_response(request, form)

        
@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid() and form.validated_user(request.user):
            user = User.objects.get(username=request.user.username)
            user.set_password(str(form.cleaned_data['new_password']))
            user.save()
            return HttpResponseRedirect('/change_password/success/')
        else:
            return _change_password_response(request, form)
        
    else:
        form = ChangePasswordForm()
        return _change_password_response(request, form)
        

@login_required
def my_projects(request):
    user = request.user
    projects = Project.objects.filter(created_by=user)
    return render_to_response('my_projects.html',
                              {'projects' : projects},
                              context_instance=RequestContext(request)  
                             )
    
    
def _user_registration_response(request, form):
    group_names = ", ".join([str(group.name) for group in Group.objects.all()])
    return render_to_response('user_registration.html',
                             {'form' : form},
                             context_instance=RequestContext(request)
                             )
                             
def _change_password_response(request, form):
    return render_to_response('change_password.html',
                             {'form' : form},
                             context_instance=RequestContext(request)
                             )

    
def _create_user(form):
    username = form.cleaned_data['username']
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    user = User.objects.create_user(username, email, password)
    user.groups.add(Group.objects.get(name=GROUPS.PROJECT_AUTHORS))
    user.save()


    
