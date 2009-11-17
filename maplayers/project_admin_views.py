# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import uuid
import os, stat

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User, Group

from maplayers.constants import GROUPS, PROJECT_STATUS
from maplayers.models import Project, Sector, Implementor, Resource, Link
from maplayers.forms import ProjectForm

# Authentication helpers
def _is_project_author(user):
    for g in user.groups.all():
        if g.name in (GROUPS.ADMINS, GROUPS.PROJECT_AUTHORS, GROUPS.EDITORS_PUBLISHERS):
            return True
    return False
    
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
        project = Project.objects.get(id=int(project_id))

        if form.is_valid(): 
            _create_links(request, project_id, link_titles, link_urls)
            _set_project_status(project, request)
            _add_project_details(form, project)
            return _add_edit_success_page(project, request)
        else: 
            return _render_response(request, form, "add_project", sectors, 
                                    implementors, project, link_titles, link_urls, 
                                    project.resource_set.all())
    else: 
        form = ProjectForm()
        project = _create_new_project(request)
        return _render_response(request, form, "add_project", 
                                sectors, implementors, project)


@login_required
def edit_project(request, project_id): 
    project = Project.objects.get(id=int(project_id))
    if not project.is_editable_by(request.user):
        return HttpResponseRedirect('/permission_denied/edit_project/not_author')

    sectors = ", ".join([sector.name for sector in Sector.objects.all()[:5]])
    implementors = ", ".join([implementor.name for implementor in Implementor.objects.all()[:5]])
    action = "edit_project/" + project_id
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        link_titles = request.POST.getlist('link_title')
        link_urls =  request.POST.getlist('link_url')
        tags = request.POST.get("tags")
        if form.is_valid(): 
            project.link_set.all().delete()
            project.sector_set.clear()
            project.implementor_set.clear()
            _set_project_status(project, request)
            project.save()
            _create_links(request, project_id, link_titles, link_urls)
            _add_project_details(form, project)
            return _add_edit_success_page(project,request)
        else:
            return _render_response(request, form, action, sectors, implementors, 
                                    project, link_titles, link_urls, 
                                    project.resource_set.all())
    else:
        form = _create_initial_data_from_project(project)
        links = project.link_set.all()
        link_titles = [link.title for link in links]
        link_urls = [link.url for link in links]
        return _render_response(request, form, action, sectors, implementors, 
                                project,link_titles, link_urls, 
                                project.resource_set.all())
                                
    
@login_required                            
def file_upload(request):
    uploaded_file = request.FILES['Filedata']
    uploaded_file_name = request.POST.get('Filename', '')
    project_id = request.POST.get('project_id')
    file_size = uploaded_file.size
    destination_name = "static/resources/" + str(uuid.uuid1()) + "_" + uploaded_file_name
    destination = open(destination_name, 'wb+')
    for chunk in uploaded_file.chunks(): 
        destination.write(chunk) 
        destination.close()
    os.chmod(destination_name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR) 
    project = Project.objects.get(id=project_id)
    project.resource_set.add(Resource(title = uploaded_file_name, filename=destination_name, project=project, filesize=file_size))
    return HttpResponse("OK")
    

@login_required
def remove_attachment(request):
    project_id = request.GET.get('project_id')
    filename = request.GET.get('file-name')
    project = Project.objects.get(id=int(project_id))
    resource = Resource.objects.filter(filename__contains=filename, project=project)[0]
    os.remove(resource.filename)
    resource.delete()
    return HttpResponse("OK")


@login_required                     
def publish_project(request, project_id):
    project = Project.objects.get(id=int(project_id))
    if not project.is_publishable_by(request.user):
        return HttpResponse("{'authorized' : false}")
    return _project_status_change_json_response(request, project, 
                    PROJECT_STATUS.PUBLISHED, "Published")
                    
@login_required                     
def reject_project(request, project_id):
    project = Project.objects.get(id=int(project_id))
    if not project.is_publishable_by(request.user):
        return HttpResponse("{'authorized' : false}")
    return _project_status_change_json_response(request, project, 
                    PROJECT_STATUS.REJECTED, "Rejected")
                    
@login_required                     
def delete_project(request, project_id):
    project = Project.objects.get(id=int(project_id))
    if not project.is_editable_by(request.user):
        return HttpResponse("{'authorized' : false}")
    project.delete()
    return HttpResponse("Deleted")

@login_required
def unpublish_project(request, project_id):
    project = Project.objects.get(id=int(project_id))
    if not project.is_publishable_by(request.user):
        return HttpResponse("{'authorized' : false}")
    return _project_status_change_json_response(request, project, 
                    PROJECT_STATUS.UNPUBLISHED, "Unpublished")


def _add_edit_success_page(project,request):
    if project.status == PROJECT_STATUS.PUBLISHED:
        message = "published"
    elif project.status == PROJECT_STATUS.UNPUBLISHED:
        message = "unpublished"
    else:
        message = "submitted for review"
        
    request.session['success_message'] = "Project has been " + message + " successfully"
    url = "/projects/id/%s/" % str(project.id)
    return HttpResponseRedirect(url)
                              
def _project_status_change_json_response(request, project, status, message):
    project.status=status
    project.save()
    return render_to_response(
                              'change_project_status.json', 
                              {
                                'project' : project,
                                'message' : message, 
                                'publishable' : project.is_publishable_by(request.user)
                              },
                              context_instance=RequestContext(request)
                              )

def _add_project_details(form, project):
    project.name = form.cleaned_data['name']
    project.description = form.cleaned_data['description']
    project.latitude = form.cleaned_data['latitude']
    project.longitude = form.cleaned_data['longitude']
    project.location = form.cleaned_data['location']
    project.website_url = form.cleaned_data['website_url']
    project.project_image = form.cleaned_data['project_image']
    sector_names = form.cleaned_data['project_sectors']
    implementor_names = form.cleaned_data['project_implementors']
    project.youtube_playlist_id = form.cleaned_data['youtube_playlist_id']
    project.imageset_feedurl = form.cleaned_data['imageset_feedurl']
    project.tags = form.cleaned_data['tags']
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
    form.fields['youtube_playlist_id'].initial = project.youtube_playlist_id
    form.fields['imageset_feedurl'].initial = project.imageset_feedurl
    form.fields['tags'].initial = project.tags
    return form
    

def _create_new_project(request):
    project = Project()
    project.status = PROJECT_STATUS.DRAFT
    project.created_by = request.user
    project.save()
    project.groups = request.user.groups.all()
    return project

def _render_response(request, form, action, sectors, implementors, 
                     project, link_titles=[], link_urls=[], resources=[]):
    link_titles_and_values = zip(link_titles, link_urls)
    publishable = project.is_publishable_by(request.user)
    check_publish = 'checked="yes"' if PROJECT_STATUS.PUBLISHED == project.status else ""
    submit_label = "Submit" if publishable else "Submit for Review" 
    return render_to_response(
                              'add_project.html', 
                              {
                               'form': form,
                               'sectors' : sectors, 'implementors' : implementors,
                               'project_id' : project.id, 'resources' : resources,  
                               'title_and_values' : link_titles_and_values,
                               'action' : action, 'publishable' : publishable,
                               'checked' : check_publish, 'submit_label' : submit_label
                              },
                              context_instance=RequestContext(request)
                              )
                              
def _set_project_status(project, request):
    if project.is_publishable_by(request.user):
        if request.POST.get('publish_project'):
            project.status=PROJECT_STATUS.PUBLISHED
        else:
            project.status=PROJECT_STATUS.UNPUBLISHED
    else:
        project.status = PROJECT_STATUS.REVIEW
