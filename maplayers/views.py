# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import decimal
import logging
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse,\
                        HttpResponseNotFound, HttpResponseServerError
from django.db.models import Q
from django.contrib.auth import logout

from maplayers.utils import is_empty
from maplayers.models import Project, Sector, Implementor, ProjectComment
import decimal
from tagging.models import TaggedItem, Tag
from django.contrib.auth import logout
from maplayers.forms import UserForm, ChangePasswordForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from maplayers.constants import PROJECT_STATUS, EMAIL_REGEX, COMMENT_STATUS, GROUPS
from maplayers.utils import html_escape
from datetime import datetime
import simplejson as json
from maplayers.models import AdministrativeUnit, KMLFile
from admin_request_parser import convert_text_to_dicts


def homepage(request):
    sectors = _get_sectors(request)
    sector_ids = [sector.id for sector in sectors]
    implementors  = _get_implementors(request)
    implementor_ids = [implementor.id for implementor in implementors]
    left, bottom, right, top = _get_bounding_box(request)
    projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)
    context_data = {'projects' : projects, 'sectors' : sectors, 'tag': "",
                    'implementors' : implementors,'left': left, 'right' : right,
                    'top': top, 'bottom' : bottom}
    return render_to_response(
                              'homepage.html', 
                              context_data,
                              context_instance=RequestContext(request)
                              ) 
    

def search_admin_units(request):
    if request.method == 'POST':        
        text = request.POST.get('text')
        admin_unit_req = convert_text_to_dicts(text)
        admin_unit = _get_admin_model(admin_unit_req)
        response = HttpResponse()
        response.write(admin_unit.region_statistics)
        return response
        
        
        
def projects_in_map(request, left, bottom, right, top):
    sector_ids =  _filter_ids(request, "sector") or \
                [sector.id for sector in Sector.objects.all()]
    implementor_ids =  _filter_ids(request, "implementor") or \
                [implementor.id for implementor in Implementor.objects.all()]
    
    if request.GET.get('tag', ''):
        projects = _get_projects_with_tag(left, bottom, right, top, sector_ids, implementor_ids, request.GET['tag'])
    elif request.GET.get('search_term', ''):
        projects = _get_projects_with_search(left, bottom, right, top, sector_ids, implementor_ids, request.GET['search_term'])
    else:
        projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)

    return write_project_list_to_response(projects)   


def project(request, project_id, project_manager=Project.objects):
    logging.debug("View project details [project_id] : %s" % project_id)
    project = project_manager.select_related(depth=1).get(id=int(project_id))
    if not (project.is_editable_by(request.user) or project.is_published()): raise Http404
    
    subprojects = project.project_set.filter(status=PROJECT_STATUS.PUBLISHED)
    bbox = _get_bounding_box_for_project(project, subprojects)
    implementors = ", ".join([implementor.name for implementor in project.implementor_set.all()])
    tags = project.tags.split(" ")
    resources = project.resource_set.all()
    context = {'project': project, 
               'links' : project.link_set.all(), 
               'rss_img_feed_url': project.imageset_feedurl, 
               'subprojects' : subprojects, 
               'implementors' : implementors, 
               'tags' : tags,
               'resources' : resources}
    context.update(bbox)          
    
    return render_to_response('project.html', context,
                               context_instance=RequestContext(request)
                              )


def kml_layers(request):
    kml_files = KMLFile.objects.all()
    return render_to_response("kml_files.json",
                            {'kmls' : kml_files},
                            context_instance=RequestContext(request)
                            )

    
def user_registration(request):
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
                         

                              
def project_comment(request, project_id):
    project = Project.objects.get(id=int(project_id))
    username = request.POST.get('name', '')
    email = request.POST.get('email', '')
    comment_text = request.POST.get('comment', '')
    response_json = {}
    _check_for_comment_errors(username, email, comment_text, response_json)
    if not response_json:
        comment = ProjectComment(comment_by=username, email = email, status = COMMENT_STATUS.UNMODERATED,
                    text = comment_text, project = project, date = datetime.today())
        comment.save()
        response_json['message'] = "Thank you for your comment. The Author of the project will be notified of this"
    
    return HttpResponse(json.dumps(response_json))
    

def projects_search(request, search_term):
    qset = _construct_queryset_for_project_search(search_term)
    projects = Project.objects.filter(qset, parent_project=None, status=PROJECT_STATUS.PUBLISHED).distinct()

    return write_project_list_to_response(projects)   
   
def projects_tag_search(request, tag_term):
    projects = TaggedItem.objects.get_by_model(Project, Tag.objects.filter(name__in=[tag_term]))
    sectors = Sector.objects.all()
    implementors = Implementor.objects.all() 
    left, right, top, bottom = (-180, 180, -90, 90)
    
    return render_to_response(
                              'homepage.html',
                              {
                               'projects' : projects, 
                               'sectors' : sectors, 
                               'implementors' : implementors,
                               'tag' : tag_term,
                               'left' : left, 'right' : right,
                               'top' : top, 'bottom' : bottom
                               },
                               context_instance=RequestContext(request)
                              )     

def view_404(request):
    response = HttpResponseNotFound()
    template = loader.get_template('404.html')
    response.write(template.render(RequestContext(request)))
    return response
    
def view_500(request):
    response = HttpResponseServerError()
    template = loader.get_template('500.html')
    response.write(template.render(RequestContext(request)))
    return response
    
def _filter_ids(request, filter_name):
    """
    returns a list of selected filter_id from the request
    """
    return [int(filter_id.split("_")[1]) for filter_id in \
            request.GET.keys() if filter_id.find(filter_name +"_") >=0]
    
def _get_sectors(request):
    """
    returns a list of selected sectors present in the request OR all sectors as default
    """
    ids = _filter_ids(request, "sector")
    return Sector.objects.filter(id__in=ids) if ids else Sector.objects.all()
    
def _get_implementors(request):
    """
    returns a list of selected implementors present in the request OR all implementors as default
    """
    ids = _filter_ids(request, "implementor")
    return Implementor.objects.filter(id__in=ids) if ids else Implementor.objects.all()
    
def _get_projects(left, bottom, right, top, sector_ids, implementor_ids):
    """
    returns a list of projects that match the filter criteria and are within the bounding box
    """
    left, bottom, right, top = \
        [decimal.Decimal(p) for p in (left, bottom, right, top)]
    
    return Project.objects.filter(longitude__gte=left, 
                                  longitude__lte=right,  
                                  latitude__gte=bottom, 
                                  latitude__lte=top, 
                                  sector__in=sector_ids,
                                  implementor__in=implementor_ids,
                                  status=PROJECT_STATUS.PUBLISHED,
                                  parent_project=None
                                  ).distinct()
                                      
def _get_bounding_box(request):
    left = request.GET.get('left', '-180')
    right = request.GET.get('right', '180')
    top = request.GET.get('top', '90')
    bottom = request.GET.get('bottom', '-90')
    return (left, bottom, right, top)

def _construct_queryset_for_project_search(search_term):
    return  (Q(name__icontains=search_term) |
             Q(description__icontains=search_term) |
             Q(location__icontains=search_term) |
             Q(implementor__name__icontains=search_term))
             
def _construct_queryset_for_adminunit_search(detail):
    return (Q(name=detail['NAME_1']) |
    Q(region_type=detail['TYPE_1']) |
    Q(country_type=detail['NAME_0']))

def _get_projects_with_tag(left, bottom, right, top, sector_ids, implementor_ids, tag):
    projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)
    results = []
    for project in projects:
        if project.contains_tag(tag) and project.is_parent_project():
            results.append(project)
    return results

def _get_projects_with_search(left, bottom, right, top, sector_ids, implementor_ids, search):
    left, bottom, right, top = \
        [decimal.Decimal(p) for p in (left, bottom, right, top)]
    
    return Project.objects.filter(_construct_queryset_for_project_search(search),
                                  longitude__gte=left, 
                                  longitude__lte=right,  
                                  latitude__gte=bottom, 
                                  latitude__lte=top, 
                                  sector__in=sector_ids,
                                  implementor__in=implementor_ids,
                                  status=PROJECT_STATUS.PUBLISHED,
                                  ).distinct()
                                  
def _get_admin_model(details):
    try:
        adminModel = AdministrativeUnit.objects.get(name=details['NAME_1'])
    except:
        adminModel = AdministrativeUnit()
        adminModel.region_statistics = "Sorry, We don't have the Region Statistics for the district"
    
    return adminModel
 
def _filter_projects_for_request(request):
   if request.GET.get('tag', ''):
       projects = _get_projects_with_tag(left, bottom, right, top, sector_ids, implementor_ids, request.GET.get('tag'))
   elif request.GET.get('search_term', ''):
       projects = _get_projects_with_tag(left, bottom, right, top, sector_ids, implementor_ids, request.GET.get('search_term'))
   else:
       projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)
   return projects


def convert_to_json(projects):
    result = []
    for project in projects:
        project_json = '''{"latitude" : %.2f, "longitude" : %.2f, "snippet" : "%s", "id" : %d, "sectors" : %s, "implementors" : %s}''' %(project.latitude, project.longitude,
                html_escape(project.snippet()), project.id, project.sectors_in_json(), project.implementors_in_json())
        result.append(project_json)
    return "[" + ", ".join(result) + "]"

def write_project_list_to_response(projects):
    response = HttpResponse()
    response.write(convert_to_json(projects))
    return response
    
def _check_for_comment_errors(username, email, comment_text, errors):
    if not username: errors['username'] = "Name is required"
    if not email: errors['email'] = 'Email is required'
    if not comment_text: errors['comment'] = 'Comment is required'
    if email and not EMAIL_REGEX.match(email): errors['email' ] = "Invalid email"
    
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
    
def _get_bounding_box_for_project(project, subprojects):
    latitudes = [project.latitude]
    longitudes = [project.longitude]
    
    for subproject in subprojects:
        latitudes.append(subproject.latitude)
        longitudes.append(subproject.longitude)
    
    left = (min(longitudes) - 2) if min(longitudes) - 2 > -180 else min(longitudes)
    right = (max(longitudes) + 2) if max(longitudes) + 2 < 180 else max(longitudes)
    top = (max(latitudes) + 1) if max(latitudes) + 1 < 90 else max(latitudes)
    bottom = (min(latitudes) - 1) if min(latitudes) - 1 > -90 else min(latitudes)
    return {'left' : left, 'right' : right, 'top' : top, 'bottom' : bottom}
        

