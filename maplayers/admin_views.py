from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from maplayers.models import Project, Sector, Implementor, Resource
from maplayers.forms import ProjectForm
from django.http import HttpResponse
import uuid

from maplayers.constants import GROUPS

# Authentication helpers
def _is_project_author(u):
    for g in u.groups.all():
        if g.name in (GROUPS.ADMINS, GROUPS.PROJECT_AUTHORS):
            return True
    return False

def _is_project_owner(u, project):
    """
    Must be implemented for _edit_project_ to check that
    the person attempting to edit has perms.
    
    Test should be:
    1. Are they the original creator?
    2. Are they in the same implementing org as the original creator?
    
    """
    return True

@login_required
def add_project(request): 
    # check for authorness... Can't use 'user_passes_test' decoartor
    # because it doesn't handle redirects properly
    if not _is_project_author(request.user):
        return HttpResponseRedirect('/permission_denied/add_project/not_author')
    
    
    sectors = ", ".join([sector.name for sector in Sector.objects.all()[:5]])
    implementors = ", ".join([implementor.name for implementor in Implementor.objects.all()[:5]])
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        project_id = request.POST.get("project_id")
        if form.is_valid(): 
            _create_project(form, project_id)
            return HttpResponseRedirect('/project_created_successfully/')
        else: 
            return render_to_response(
                                      'add_project.html', 
                                      {
                                       'form': form,
                                      'sectors' : sectors, 
                                      'implementors' : implementors,
                                      'project_id' : project_id
                                      },
                                      context_instance=RequestContext(request)
                                      ) 
    else: 
        form = ProjectForm()
        project = Project()
        project.save()
        return render_to_response(
                                  'add_project.html', 
                                  {
                                   'form': form,
                                  'sectors' : sectors, 'implementors' : implementors,
                                  'project_id' : project.id
                                  },
                                  context_instance=RequestContext(request)
                                  ) 
        
        
        
def file_upload(request):
    uploaded_file = request.FILES['Filedata']
    uploaded_file_name = request.POST.get('Filename', '')
    project_id = request.POST.get('project_id')
    destination_name = "static/resources/" + str(uuid.uuid1()) + "_" + uploaded_file_name
    destination = open(destination_name, 'wb+')
    for chunk in uploaded_file.chunks(): 
        destination.write(chunk) 
        destination.close() 
    project = Project.objects.get(id=project_id)
    project.resource_set.add(Resource(title = uploaded_file_name, filename=destination_name, project=project))
    return HttpResponse("OK")
        
def _create_project(form, project_id):
    project = Project.objects.get(id=int(project_id))
    project.name = form.cleaned_data['name']
    project.description = form.cleaned_data['description']
    project.latitude = form.cleaned_data['latitude']
    project.longitude = form.cleaned_data['longitude']
    project.location = form.cleaned_data['location']
    project.website_url = form.cleaned_data['website_url']
    project.project_image = form.cleaned_data['project_image']
    sector_names = form.cleaned_data['project_sectors']
    implementor_names = form.cleaned_data['project_implementors']
    project.youtube_username = form.cleaned_data['youtube_username']
    project.imageset_feedurl = form.cleaned_data['imageset_feedurl']
    project.save()
    _add_sectors_and_implementors(project, sector_names, implementor_names)


def _add_sectors_and_implementors(p, sectors_names,implementor_names):
    sector_names = [name.strip() for name in sectors_names.split(",") if name.strip()]
    implementor_names = [name.strip() for name in implementor_names.split(",") if name.strip()]
    
    all_sectors = Sector.objects.all()
    all_implementors = Implementor.objects.all()
    _add_existing_sectors(p, all_sectors, sector_names)
    _add_existing_implementors(p, all_implementors, implementor_names)
    
    _create_and_add_new_sectors(p, all_sectors, sector_names)
    _create_and_add_new_implementors(p, all_implementors, implementor_names)
    

        
def _add_existing_sectors(p, all_sectors, sectors_names):
    existing_sectors = [sector for sector in all_sectors \
                        if sector.name in sectors_names]
    for sector in existing_sectors:
        p.sector_set.add(sector)
        
        
def _add_existing_implementors(p, all_implementors, implementor_names):
    existing_implementors = [implementor for implementor in all_implementors \
                            if implementor.name in implementor_names]
    for implementor in existing_implementors:
        p.implementor_set.add(implementor)
        
def _create_and_add_new_sectors(p, all_sectors, sector_names):
    all_sector_names = [sector.name for sector in all_sectors]
    new_sectors = set(sector_names) - set(all_sector_names)
    for sector_name in new_sectors:
        p.sector_set.create(name=sector_name)
        
def _create_and_add_new_implementors(p, all_implementors, implementor_names):
    all_implementor_names = [implementor.name for implementor in all_implementors]
    new_implementors = set(implementor_names) - set(all_implementor_names)
    for implementor_name in new_implementors:
        p.implementor_set.create(name=implementor_name)


    