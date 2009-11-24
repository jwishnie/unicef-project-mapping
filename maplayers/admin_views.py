import uuid
import os, stat

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from maplayers.models import Project, ReviewFeedback, AdministrativeUnit

from maplayers.constants import GROUPS, PROJECT_STATUS, COMMENT_STATUS
from maplayers.forms import UserForm, ChangePasswordForm, AdminUnitForm


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
    projects = Project.objects.select_related(depth=1).filter(created_by=user).exclude(status=PROJECT_STATUS.DRAFT)
    return render_to_response('my_projects.html',
                              {'projects' : projects},
                              context_instance=RequestContext(request)  
                             )


@login_required
def projects_for_review(request):
    user = request.user
    if not (set((GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS)) & set([g.name for g in user.groups.all()])):
        return HttpResponseRedirect('/permission_denied/add_user/not_admin')
    
    projects = Project.objects.filter(status=PROJECT_STATUS.REVIEW)
    return render_to_response('projects_for_review.html',
                              {'projects' : projects},
                              context_instance=RequestContext(request)  
                             )

@login_required
def review_suggestions(request, project_id):
    project = Project.objects.get(id=project_id)
    suggestions = ReviewFeedback.objects.filter(project=project)
    return render_to_response('review_suggestions.html',
                              {'suggestions' : suggestions},
                              context_instance=RequestContext(request)  
                             )
    
    
@login_required
def admin_units(request):
    admin_units = AdministrativeUnit.objects.all()
    return render_to_response('admin_units.html',
                              {'admin_units' : admin_units},
                              context_instance=RequestContext(request)  
                             )

@login_required
def add_administrative_unit(request):
    if request.method == 'POST':
        form = AdminUnitForm(request.POST)
        if form.is_valid():
            _create_admin_unit(form)
            request.session['message'] = "Admin unit has been added successfully"
            url = "/admin_units/"
            return HttpResponseRedirect(url)

        else:
            return render_to_response('add_admin_unit.html',
                                     {'form': form,
                                      'action' : 'add_admin_unit'
                                      },
                                      context_instance=RequestContext(request)
                                      ) 
    else:
        form = AdminUnitForm()
        return render_to_response('add_admin_unit.html',
                                     {'form': form,
                                      'action' : 'add_admin_unit'
                                      },
                                  context_instance=RequestContext(request)
                                  )


@login_required
def edit_administrative_unit(request, id):
    if request.method == 'POST':
        form = AdminUnitForm(request.POST)
        if form.is_valid():
            _edit_admin_unit(form, id)
            request.session['message'] = "Admin unit has been edited successfully"
            url = "/admin_units/"
            return HttpResponseRedirect(url)
        else:
            return render_to_response('add_admin_unit.html',
                                     {'form': form,
                                      'action' : 'edit_admin_unit/' + id
                                      },
                                      context_instance=RequestContext(request)
                                      ) 
    else:
        form = AdminUnitForm()
        admin_unit = AdministrativeUnit.objects.get(id=int(id))
        form.fields['name'].initial = admin_unit.name
        form.fields['country'].initial = admin_unit.country
        form.fields['region_type'].initial = admin_unit.region_type
        form.fields['region_statistics'].initial = admin_unit.region_statistics

        return render_to_response('add_admin_unit.html',
                                  {
                                  'form': form,
                                  'action' : 'edit_admin_unit/' + id
                                  },
                                  context_instance=RequestContext(request)
                                  )

@login_required
def delete_administrative_unit(request, id):
    AdministrativeUnit.objects.get(id=int(id)).delete()
    request.session['message'] = "Admin unit has been deleted successfully"
    url = "/admin_units/"
    return HttpResponseRedirect(url)

def _create_admin_unit(form):
    admin_unit = AdministrativeUnit()
    admin_unit.name = form.cleaned_data['name']
    admin_unit.country = form.cleaned_data['country']
    admin_unit.region_type = form.cleaned_data['region_type']
    admin_unit.region_statistics = form.cleaned_data['region_statistics']
    admin_unit.save()

def _edit_admin_unit(form, unit_id):
    admin_unit = AdministrativeUnit.objects.get(id=int(unit_id))
    admin_unit.name = form.cleaned_data['name']
    admin_unit.country = form.cleaned_data['country']
    admin_unit.region_type = form.cleaned_data['region_type']
    admin_unit.region_statistics = form.cleaned_data['region_statistics']
    admin_unit.save()

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


    
