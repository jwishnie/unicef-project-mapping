from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from maplayers.models import Project, Sector, Implementor, Resource, Link
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
    # check for authorness... Can't use 'user_passes_test' decorator
    # because it doesn't handle redirects properly
    if not _is_project_author(request.user):
        return HttpResponseRedirect('/permission_denied/add_project/not_author')
    
    sectors = ", ".join([sector.name for sector in Sector.objects.all()[:5]])
    implementors = ", ".join([implementor.name for implementor in Implementor.objects.all()[:5]])
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        project_id = request.POST.get("project_id")
        link_titles = request.POST.getlist('link_title')
        link_urls =  request.POST.getlist('link_url')
        
        if form.is_valid(): 
            _create_links(request, project_id, link_titles, link_urls)
            _create_project(form, project_id)
            return HttpResponseRedirect('/project_created_successfully/')
        else: 
            return _render_response(request, form, "add_project", sectors, 
                                    implementors, project_id, link_titles, link_urls)
    else: 
        form = ProjectForm()
        project = Project()
        project.save()
        return _render_response(request, form, "add_project", 
                                sectors, implementors, project.id)
        
        
@login_required
def edit_project(request, project_id): 
    
    if not _is_project_author(request.user):
        return HttpResponseRedirect('/permission_denied/edit_project/not_author')
    project = Project.objects.get(id=int(project_id))

    sectors = ", ".join([sector.name for sector in Sector.objects.all()[:5]])
    implementors = ", ".join([implementor.name for implementor in Implementor.objects.all()[:5]])

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        link_titles = request.POST.getlist('link_title')
        link_urls =  request.POST.getlist('link_url')
        if form.is_valid(): 
            project.link_set.all().delete()
            project.sector_set.clear()
            project.implementor_set.clear()
            project.save()
            _create_links(request, project_id, link_titles, link_urls)
            _create_project(form, project_id)
            return HttpResponseRedirect('/project_edited_successfully/')
        else:
            action = "edit_project/" + project_id
            return _render_response(request, form, action, sectors, implementors, 
                                    project_id, link_titles, link_urls)
    else:
        form = _create_initial_data_from_project(project)
        links = project.link_set.all()
        link_titles = [link.title for link in links]
        link_urls = [link.url for link in links]
        action = "edit_project/" + project_id
        return _render_response(request, form, action, sectors, implementors, 
                                project_id, link_titles, link_urls)
    
  
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
    
def _create_links(request, project_id, link_titles, link_urls):
    for i in range(len(link_titles)):
        link = Link(project_id=project_id, title=link_titles[i], url=link_urls[i])
        link.save()


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
        
def _create_initial_data_from_project(project):
    form = ProjectForm()
    form.fields['name'].initial = project.name
    form.fields['description'].initial = project.description
    form.fields['latitude'].initial = project.latitude
    form.fields['longitude'].initial = project.longitude
    form.fields['location'].initial = project.location
    form.fields['website_url'].initial = project.website_url
    form.fields['project_image'].initial = project.project_image
    form.fields['project_sectors'].initial = ", ".join([sector.name for sector in project.sector_set.all()])
    form.fields['project_implementors'].initial = ", ".join([implementor.name for implementor \
                                                            in project.implementor_set.all()])
    form.fields['youtube_username'].initial = project.youtube_username
    form.fields['imageset_feedurl'].initial = project.imageset_feedurl
    return form

def _render_response(request, form, action, sectors, implementors, project_id, link_titles=[], link_urls=[]):
    link_titles_and_values = zip(link_titles, link_urls)
    return render_to_response(
                              'add_project.html', 
                              {
                               'form': form,
                               'sectors' : sectors, 'implementors' : implementors,
                               'project_id' : project_id,
                               'title_and_values' : link_titles_and_values,
                               'action' : action
                              },
                              context_instance=RequestContext(request)
                              )

    
