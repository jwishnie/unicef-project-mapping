import uuid
import os, stat

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from maplayers.models import Project, ReviewFeedback, AdministrativeUnit, KMLFile

from maplayers.constants import GROUPS, PROJECT_STATUS, COMMENT_STATUS
from maplayers.forms import AdminUnitForm, KMLFilesForm
from utils import create_dir_if_not_exists


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
        form.fields['health'].initial = admin_unit.health
        form.fields['economy'].initial = admin_unit.economy
        form.fields['environment'].initial = admin_unit.environment
        form.fields['governance'].initial = admin_unit.governance
        form.fields['infrastructure'].initial = admin_unit.infrastructure
        form.fields['social_sector'].initial = admin_unit.social_sector
        form.fields['agriculture'].initial = admin_unit.agriculture
        form.fields['dev_partners'].initial = admin_unit.dev_partners
        form.fields['recent_reports'].initial = admin_unit.recent_reports
        form.fields['resources'].initial = admin_unit.resources

        return render_to_response('add_admin_unit.html',
                                  {
                                  'form': form,
                                  'action' : 'edit_admin_unit/' + id
                                  },
                                  context_instance=RequestContext(request)
                                  )

@login_required
def delete_administrative_unit(request, admin_unit_manager=AdministrativeUnit.objects):
    if request.method == 'POST':
        try:
            non_existant_admin_unit = '-999'
            admin_unit_id = request.POST.get('id', non_existant_admin_unit)
            admin_unit_manager.get(id=int(admin_unit_id)).delete()
            request.session['message'] = "Admin unit has been deleted successfully"
            url = "/admin_units/"
            return HttpResponseRedirect(url)
        except Exception, ex:
            request.session['message'] = "Unable to delete Admin unit"
            url = "/admin_units/"
            return HttpResponseRedirect(url)
    
    
@login_required
def add_kml_file(request):
    if request.method == 'POST':
        form = KMLFilesForm(request.POST, request.FILES)
        if form.is_valid():
            kml_name = form.cleaned_data['name']
            uploaded_file = request.FILES['filename']
            file_name = uploaded_file.name
            filename = filename.replace(" ", "_get_app_dir")
            app_dir = _get_app_dir(__file__)
            destination_name = app_dir + '/static/kml/' + file_name
            create_dir_if_not_exists(destination_name)
            destination = open(destination_name, 'wb+')
            for chunk in uploaded_file.chunks(): 
                destination.write(chunk) 
                destination.close()
            kml_file = KMLFile(name=kml_name, filename=('static/kml/' + file_name))
            kml_file.save()
            return HttpResponseRedirect('/')
        else:
            return _render_response(form, request)
    else:
        form = KMLFilesForm()
        return _render_response(form, request)
        
        
@login_required
def delete_kml(request, id):
    KMLFile.objects.get(id=int(id)).delete()
    return HttpResponse('OK')
    
def _render_response(form, request):
     existing_kmls = KMLFile.objects.all()
     return render_to_response('add_kml_files.html',
                               {'form': form,
                               'existing_kmls' : existing_kmls},
                               context_instance=RequestContext(request)
                               )


def _create_admin_unit(form):
    admin_unit = AdministrativeUnit()
    admin_unit.name = form.cleaned_data['name']
    admin_unit.country = form.cleaned_data['country']
    admin_unit.region_type = form.cleaned_data['region_type']
    admin_unit.health = form.cleaned_data['health']
    admin_unit.economy = form.cleaned_data['economy']
    admin_unit.environment = form.cleaned_data['environment']
    admin_unit.governance = form.cleaned_data['governance']
    admin_unit.infrastructure = form.cleaned_data['infrastructure']
    admin_unit.social_sector = form.cleaned_data['social_sector']    
    admin_unit.agriculture = form.cleaned_data['agriculture']
    admin_unit.dev_partners = form.cleaned_data['dev_partners']
    admin_unit.recent_reports = form.cleaned_data['recent_reports']
    admin_unit.resources = form.cleaned_data['resources']
    admin_unit.save()

def _edit_admin_unit(form, unit_id):
    admin_unit = AdministrativeUnit.objects.get(id=int(unit_id))
    admin_unit.name = form.cleaned_data['name']
    admin_unit.country = form.cleaned_data['country']
    admin_unit.region_type = form.cleaned_data['region_type']
    admin_unit.health = form.cleaned_data['health']
    admin_unit.economy = form.cleaned_data['economy']
    admin_unit.environment = form.cleaned_data['environment']
    admin_unit.governance = form.cleaned_data['governance']
    admin_unit.infrastructure = form.cleaned_data['infrastructure']
    admin_unit.social_sector = form.cleaned_data['social_sector']
    admin_unit.agriculture = form.cleaned_data['agriculture']
    admin_unit.dev_partners = form.cleaned_data['dev_partners']
    admin_unit.recent_reports = form.cleaned_data['recent_reports']
    admin_unit.resources = form.cleaned_data['resources']
    admin_unit.save()
    
    
def _get_app_dir(path_of_script):
    file_path_name = path_of_script
    directory_of_file = os.path.dirname(__file__)
    last_slash_index = directory_of_file.rindex("/")
    directory_of_index = directory_of_file[0:last_slash_index]
    return directory_of_index

