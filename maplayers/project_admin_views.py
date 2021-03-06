# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import uuid
import os, stat, re
import logging

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from datetime import datetime

from maplayers.constants import GROUPS, PROJECT_STATUS, COMMENT_STATUS, VIMEO_REGEX, YOUTUBE_REGEX, VIDEO_PROVIDER
from maplayers.models import Project, Sector, Implementor, Resource, Link, AdministrativeUnit, ReviewFeedback, ProjectComment, Video
from maplayers.forms import ProjectForm, AdminUnitForm
from maplayers.utils import html_escape
from maplayers.video_url import VideoUrl
import simplejson as json
from admin_views import my_projects
from maplayers.models import Sector
from django.views.decorators.cache import never_cache
    
# Authentication helpers
def _is_project_author(user):
    for g in user.groups.all():
        if g.name in (GROUPS.ADMINS, GROUPS.PROJECT_AUTHORS, GROUPS.EDITORS_PUBLISHERS):
            return True
    return False
    
@login_required
@never_cache
def add_project(request): 
    parent_project = _get_parent(request.META['QUERY_STRING'])
    # check for authorness... Can't use 'user_passes_test' decorator
    # because it doesn't handle redirects properly
    if not _is_project_author(request.user):
        return HttpResponseRedirect('/permission_denied/add_project/not_author')

    if parent_project:
        if not _is_author_of_parent_project(request.user, parent_project.created_by):
            return HttpResponseRedirect('/permission_denied/add_project/not_parent_project_author')

    sectors = ", ".join([sector.name for sector in Sector.objects.all()])
    implementors = ", ".join([implementor.name for implementor in Implementor.objects.all()])
    action = 'add_project?parent_id='
    if parent_project:
        action = action + str(parent_project.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        project_id = request.POST.get("project_id")
        link_titles = request.POST.getlist('link_title')
        link_urls =  request.POST.getlist('link_url')
        video_urls = [request.POST.get(video_id) for video_id in request.POST.keys() if video_id.startswith("video_url")]
        project = Project.objects.get(id=int(project_id))

        if form.is_valid():
            _create_links(request, project_id, link_titles, link_urls)
            _set_project_status(project, request)
            _add_project_details(form, project, request, parent_project)
            return _add_edit_success_page(project, request, "add")
        else:
            return _render_response(request, form, action, sectors, 
                                    implementors, project, parent_project, video_urls, link_titles, 
                                    link_urls, project.resource_set.all(), title="Add Project")
    else:
        form = ProjectForm()
        project = _create_new_project(request)
        return _render_response(request, form, action, 
                                sectors, implementors, project, parent_project, title="Add Project")

@login_required
def edit_project(request, project_id): 
    project = Project.objects.select_related(depth=1).get(id=int(project_id))
    parent_project = project.parent_project
    if not project.is_editable_by(request.user):
        return HttpResponseRedirect('/permission_denied/edit_project/not_author')

    if parent_project:
        if not _is_author_of_parent_project(request.user, parent_project.created_by):
            return HttpResponseRedirect('/permission_denied/add_project/not_parent_project_author')

    sectors = ", ".join([sector.name for sector in Sector.objects.all()])
    implementors = ", ".join([implementor.name for implementor in Implementor.objects.all()])
    action = "edit_project/" + project_id + "/"
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        link_titles = request.POST.getlist('link_title')
        link_urls =  request.POST.getlist('link_url')
        tags = request.POST.get("tags")
        video_urls = [request.POST.get(video_id) for video_id in request.POST.keys() if video_id.startswith("video_url")]
        
        if form.is_valid(): 
            project.link_set.all().delete()
            project.sector_set.clear()
            project.implementor_set.clear()
            _set_project_status(project, request)
            project.save()
            _create_links(request, project_id, link_titles, link_urls)
            _add_project_details(form, project, request, parent_project)
            return _add_edit_success_page(project,request,"edit")
        else:
            return _render_response(request, form, action, sectors, implementors, 
                                    project, parent_project, video_urls, link_titles, link_urls, 
                                    project.resource_set.all(), title="Edit Project")
    else:
        form = _create_initial_data_from_project(project)
        video_urls = [video.url for video in project.video_set.all()]
        links = project.link_set.all()
        link_titles = [link.title for link in links]
        link_urls = [link.url for link in links]
        return _render_response(request, form, action, sectors, implementors, 
                                project, parent_project, video_urls, link_titles, link_urls, 
                                project.resource_set.all(), title="Edit Project")

def _get_parent(query_string):
    match = re.search('parent_id=(?P<parent_id>\d+)', query_string)
    if match:
        project_id = match.groups(0)[0]
        return Project.objects.get(id=int(project_id))
    return None

def reject_if_not_project_author(user):
    if not _is_project_author(user):
        return HttpResponseRedirect('/permission_denied/add_project/not_author')
    
def file_upload(request):
    uploaded_file = request.FILES['Filedata']
    uploaded_file_name = request.POST.get('Filename', '')
    project_id = request.POST.get('project_id')
    file_size = uploaded_file.size
    app_dir = _get_app_dir(__file__)
    file_name = str(uuid.uuid1()) + "_" + uploaded_file_name
    destination_name = app_dir + "/static/resources/" + file_name
    logging.debug("Destination path of resource: %s" % destination_name)
    _create_dir_if_not_exists(destination_name)
    destination = open(destination_name, 'wb+')
    for chunk in uploaded_file.chunks(): 
        destination.write(chunk) 
        destination.close()
    os.chmod(destination_name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRWXG | stat.S_IROTH | stat.S_IWOTH) 
    project = Project.objects.get(id=project_id)
    project.resource_set.add(Resource(title = uploaded_file_name, filename=file_name, project=project, filesize=file_size))
    return HttpResponse("OK")
    
def photo_upload(request):
    uploaded_file = request.FILES['Filedata']
    uploaded_file_name = request.POST.get('Filename', '')
    project_id = request.POST.get('project_id')
    app_dir = _get_app_dir(__file__)
    project_photo_name = str(uuid.uuid1()) + "_" + uploaded_file_name
    destination_name = app_dir + "/static/project-photos/"+ project_photo_name
    logging.debug("Destination path of photo: %s" % destination_name)
    try:
        _create_dir_if_not_exists(destination_name)
        destination = open(destination_name, 'wb+')
        for chunk in uploaded_file.chunks(): 
            destination.write(chunk) 
            destination.close()
        os.chmod(destination_name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRWXG | stat.S_IROTH | stat.S_IWOTH) 
        project_in_request = Project.objects.get(id=int(project_id))
        project_in_request.project_image = project_photo_name
        project_in_request.save()
        return HttpResponse("OK")
    except Exception, ex:
        response = HttpResponse()
        response.write("Photo upload failed")
        return response

def _get_app_dir(path_of_script):
    file_path_name = path_of_script
    directory_of_file = os.path.dirname(__file__)
    last_slash_index = directory_of_file.rindex("/")
    directory_of_index = directory_of_file[0:last_slash_index]
    return directory_of_index
    
@login_required
def project_comments(request, project_id):
    project = Project.objects.get(id=project_id)
    if not project.created_by == request.user:
        return HttpResponseRedirect('/permission_denied/add_project/not_author')
        
    comments = project.projectcomment_set.filter(status=COMMENT_STATUS.UNMODERATED)
    if not comments: return my_projects(request)
    return render_to_response('project_comments.html',
                              {'project' : project,
                               'comments' : comments},
                              context_instance=RequestContext(request)  
                             )
                             
@login_required                       
def publish_comments(request):
    _publish_or_delete_comments(request, "publish")
    return project_comments(request, request.POST.get('project_id'))
    
    
@login_required                       
def delete_comments(request):
    _publish_or_delete_comments(request, "delete")
    return project_comments(request, request.POST.get('project_id'))

@login_required
def remove_attachment(request):
    project_id = request.GET.get('project_id')
    filename = request.GET.get('file-name')
    project = Project.objects.get(id=int(project_id))
    resource = Resource.objects.filter(filename__contains=filename, project=project)[0]
    file_to_remove = _get_app_dir(__file__) + "/static/resources/" + resource.filename
    os.remove(file_to_remove)
    resource.delete()
    return HttpResponse("OK")

@login_required
def remove_photo(request):
    project_id = request.GET.get('project_id')
    app_dir = _get_app_dir(__file__)
    project_in_request = Project.objects.get(id=int(project_id))
    destination_filename = app_dir + "/static/project-photos/" + project_in_request.project_image
    os.remove(destination_filename)
    project_in_request.project_image = ""
    project_in_request.save()
    return HttpResponse("OK")

@login_required                     
def publish_project(request, project_id):
    project = Project.objects.get(id=int(project_id))
    if not project.is_publishable_by(request.user):
        return HttpResponseRedirect('/permission_denied/edit_project/not_author')
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
def request_changes(request, project_id):
    feedback = request.POST.get('feedback', '')
    response_json = {}
    project = Project.objects.get(id=int(project_id))
    response_json["authorized"] = True if project.is_publishable_by(request.user) else False
    
    if not feedback:
        response_json["error"] = "Feedback is required"
    else:
        project.status = PROJECT_STATUS.REQUEST_CHANGES
        review_changes = ReviewFeedback()
        review_changes.feedback = feedback
        review_changes.project = project
        review_changes.reviewed_by = request.user
        review_changes.date = datetime.today()
        review_changes.save()
        project.save()
    return HttpResponse(json.dumps(response_json))
        

@login_required                     
def delete_project(request, project_id):
    project = Project.objects.get(id=int(project_id))
    if not project.is_editable_by(request.user):
        return HttpResponse("{'authorized' : false}")
    if project.project_image:
        os.remove(project.project_image)
    for resource in project.resource_set.all():
        os.remove(resource.filename)
        resource.delete()
    project.delete()
    return HttpResponse("Deleted")

@login_required
def unpublish_project(request, project_id):
    project = Project.objects.get(id=int(project_id))
    if not project.is_publishable_by(request.user):
        return HttpResponse("{'authorized' : false}")
    return _project_status_change_json_response(request, project, 
                    PROJECT_STATUS.UNPUBLISHED, "Unpublished")


@login_required
def add_administrative_unit(request):
    if request.method == 'POST':
        form = AdminUnitForm(request.POST)
        if form.is_valid():
            _create_admin_unit(form)
            return HttpResponseRedirect('/admin_unit_creation/success/')
        else:
            return render_to_response('add_admin_unit.html',
                                      {'form': form},
                                      context_instance=RequestContext(request)
                                      ) 
    else:
        form = AdminUnitForm()
        return render_to_response('add_admin_unit.html',
                                  {'form' : form},
                                  context_instance=RequestContext(request)
                                  )

def _create_admin_unit(form):
    admin_unit = AdministrativeUnit()
    admin_unit.name = form.cleaned_data['name']
    admin_unit.country = form.cleaned_data['country']
    admin_unit.region_type = form.cleaned_data['region_type']
    admin.region_statistics = form.cleaned_data['region_statistics']
    admin_unit.save()

def _add_edit_success_page(project,request, action):
    if project.is_published():
        message = "published"
    elif project.status == PROJECT_STATUS.UNPUBLISHED:
        message = "saved"
    else:
        message = "submitted for review"
        
    request.session['message'] = "Project has been " + message + " successfully"
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

def _add_project_details(form, project, request, parent_project=None):
    description = form.cleaned_data['description']
    description = description.replace('<p>&nbsp;</p>', '')
    description = description.replace('\n', '')
    description = description.replace('\r', '')
    project.name = form.cleaned_data['name'].replace('&','&amp;').replace('<','&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'",'&#39;')
    project.description = description
    project.latitude = form.cleaned_data['latitude']
    project.longitude = form.cleaned_data['longitude']
    project.location = form.cleaned_data['location']
    project.website_url = form.cleaned_data['website_url']
    sector_ids = form.cleaned_data['project_sectors']
    implementor_ids = form.cleaned_data['project_implementors']
    project.imageset_feedurl = form.cleaned_data['imageset_feedurl']
    project.tags = form.cleaned_data['tags']
    if parent_project:
        project.parent_project = parent_project
    project.save()
    _add_sectors_and_implementors(project, sector_ids, implementor_ids)
    _add_project_videos(project, request)


def _create_links(request, project_id, link_titles, link_urls):
    for i in range(len(link_titles)):
        link = Link(project_id=project_id, title=link_titles[i], url=link_urls[i])
        link.save()

def _add_sectors_and_implementors(project, sectors_ids,implementor_ids):
    sectors = Sector.objects.filter(id__in=sectors_ids)
    implementors = Implementor.objects.filter(id__in=implementor_ids)
    for sector in sectors:
        project.sector_set.add(sector)
    for implementor in implementors:
        project.implementor_set.add(implementor)


def _add_project_videos(project, request):
    project.video_set.all().delete()
    video_url_ids = [video_id for video_id in request.POST.keys() if video_id.startswith("video_url")]
    default_video = request.POST.get('default_video', 'video_1').split("_")[1]
    for video_url_id in video_url_ids:
        video_url = VideoUrl(request.POST.get(video_url_id, ''))
        if not (video_url.is_valid): continue
        video_input_id = video_url_id.split("_")[2]
        set_default = True if default_video == video_input_id else False
        video_id = video_url.video_id()
        provider = video_url.provider
        video = Video(provider=provider, project=project, video_id = video_id, default=set_default, url=video_url.url)
        video.save()

def _create_initial_data_from_project(project):
    form = ProjectForm()
    form.fields['name'].initial = project.name
    form.fields['description'].initial = project.description
    form.fields['latitude'].initial = project.latitude
    form.fields['longitude'].initial = project.longitude
    form.fields['location'].initial = project.location
    form.fields['website_url'].initial = project.website_url
    form.fields['project_sectors'].initial = tuple([str(sector.id) for sector in project.sector_set.all()])
    form.fields['project_implementors'].initial = tuple([str(implementor.id) for implementor in project.implementor_set.all()])
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
                     project, parent_project=None, video_urls = [], link_titles=[], link_urls=[], resources=[], title =""):
    link_titles_and_values = zip(link_titles, link_urls)
    publishable = project.is_publishable_by(request.user)
    check_publish = 'checked="yes"' if project.is_published() else ""
    submit_label = "Submit" if publishable else "Submit for Review" 
    return render_to_response(
                              'add_project.html', 
                              {
                               'form': form,
                               'sectors' : sectors, 'implementors' : implementors,
                               'project' : project, 'resources' : resources,  
                               'title_and_values' : link_titles_and_values,
                               'action' : action, 'publishable' : publishable,
                               'checked' : check_publish, 'submit_label' : submit_label,
                               'mode' : "edit", 'video_urls' : video_urls,
                               'parent_project': parent_project, 'title': title
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
        
def _publish_or_delete_comments(request, action):
    comment_ids = [int(comment_id.split("_")[1]) for comment_id in \
            request.POST.keys() if comment_id.find("comment_") >=0]
    if not comment_ids: return 
    if action == "delete":
        ProjectComment.objects.filter(id__in=comment_ids).delete()
    else:
        ProjectComment.objects.filter(id__in=comment_ids).update(status=COMMENT_STATUS.PUBLISHED)
    
        

def _create_dir_if_not_exists(filename):
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def _is_author_of_parent_project(request_user, parent_author):
    if request_user.username == parent_author.username:
        return True
    return False
