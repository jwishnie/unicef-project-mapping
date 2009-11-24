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
from maplayers.forms import AdminUnitForm


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




    
