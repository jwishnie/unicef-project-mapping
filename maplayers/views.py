# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import decimal
import logging
import simplejson as json
from StringIO import StringIO
from datetime import datetime
from eventlet.green import urllib2

from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse,\
                        HttpResponseNotFound, HttpResponseServerError
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from tagging.models import TaggedItem, Tag

from maplayers.utils import is_empty
from maplayers.models import Project, Sector, Implementor, ProjectComment, Video
from maplayers.forms import UserForm, ChangePasswordForm
from maplayers.constants import PROJECT_STATUS, EMAIL_REGEX, COMMENT_STATUS, GROUPS, VIDEO_PROVIDER
from maplayers.utils import html_escape
from maplayers.models import AdministrativeUnit, KMLFile
from maplayers.admin_request_parser import convert_text_to_dicts


def homepage(request):
    sectors = _get_sectors(request)
    sector_ids = [sector.id for sector in sectors]
    implementors  = _get_implementors(request)
    implementor_ids = [implementor.id for implementor in implementors]
    left, bottom, right, top = _get_bounding_box(request)
    projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)
    kml_layers = KMLFile.objects.all()
    context_data = {'projects' : projects, 'sectors' : sectors, 'tag': "",
                    'implementors' : implementors,'left': left, 'right' : right,
                    'top': top, 'bottom' : bottom, 'kml_layers' : kml_layers} 
    return render_to_response(
                              'homepage.html', 
                              context_data,
                              context_instance=RequestContext(request)
                              ) 
    

def search_admin_units(request, admin_manager=AdministrativeUnit.objects):
    if request.method == 'GET':        
        text = request.GET.get('text')
        admin_unit_req = convert_text_to_dicts(text)
        admin_unit = _get_admin_model(admin_manager, admin_unit_req)
        admin_unit_json = convert_admin_units_to_json(admin_unit)

        response = HttpResponse()
        response.write(admin_unit_json)
        return response
        
class GeoServer(object):
    def __init__(self):
        self.url = ""
    def get_list_of_countries_with_shapefiles(self):
        request_url = ""
        response = urllib2.urlopen("http://localhost:8080/geoserver/rest/workspaces.json")
        data = json.loads(response.read())
        return self.extract_countries(data)

    def extract_countries(self, data):
        workspaces = data['workspaces']['workspace']
        regions = [region['name'] for region in  workspaces]
        regions_without_world_layer = filter(lambda x: not x.__contains__('GADM'), regions)
        return regions_without_world_layer

    def get_admin_units_for_country(self, country):
        try:
            request_url = "http://localhost:8080/geoserver/rest/workspaces/%s/datastores/%s/featuretypes.json" % (country, country)
            response = urllib2.urlopen(request_url)
            data = json.loads(response.read())
            return self.extract_admin_units(data)
        except urllib2.HTTPError, ex:
            return "Unable to find region data for the country"

    def extract_admin_units(self, data):
        if(isinstance(data, dict)):
            featuretypes = data['featureTypes']['featureType']
            admin_units = [admin_unit['name'] for admin_unit in featuretypes]
            return admin_units
        else:
            return data

class GeoNames(object):
    def __init__(self):
        self.url = "http://ws.geonames.org/countryInfoJSON?country="
    def query_for_country(self,country_code):
        try:
            request_url = self.url + str(country_code)
            data = urllib2.urlopen(str(request_url)).read()
            return data
        except urllib2.HTTPError, ex:
            return ""

def country_details(request, geonames=GeoNames(), geoserver=GeoServer()):
    if request.method == 'GET':        
        try:
            text = request.GET.get('text')
            bbox = {}
            country_details = convert_text_to_dicts(text)
            print country_details
            country_code = country_details['ISO2']
            callback = geonames.query_for_country(country_code)
            response = json.loads(callback)
            region_data = response['geonames'][0] 
            print geoserver.get_admin_units_for_country(region_data['countryName'])
            admin_units = geoserver.get_admin_units_for_country(region_data['countryName'])
            bbox['admin_units'] = [region_data['countryName'] + ":" + admin_unit for admin_unit in admin_units]
            bbox['west'] = float(region_data['bBoxWest'])
            bbox['south'] = float(region_data['bBoxSouth'])
            bbox['east'] = float(region_data['bBoxEast'])
            bbox['north'] = float(region_data['bBoxNorth'])
            bbox['country'] = "You have clicked on %s" % region_data['countryName'] 
            bbox['adm1'] =  "%s:%s" % (region_data['countryName'], bbox['admin_units'][0])
            response = HttpResponse()
            response.write(json.dumps(bbox))
            return response
        except Exception, ex:
            print ex
            response = HttpResponse()
            region_data = {'west' : -90, 'south' : -180, 'east' : 90, 'north' : 180, 'country' : 'Request failed', 'adm1' : []}
            response.write(json.dumps(region_data))
            return response
        
def projects_in_map(request, left, bottom, right, top):
    sector_ids =  _filter_ids(request, "sector") or \
                [sector.id for sector in Sector.objects.all()]
    implementor_ids =  _filter_ids(request, "implementor") or \
                [implementor.id for implementor in Implementor.objects.all()]
    search_term = request.POST.get("q", "")
    if request.GET.get('tag', ''):
        projects = _get_projects_with_tag(left, bottom, right, top, sector_ids, implementor_ids, request.GET['tag'])
        
    elif request.GET.get(search_term, ''):
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
    implementors = [implementor.name for implementor in project.implementor_set.all()]
    sectors = [sector.name for sector in project.sector_set.all()]
    tags = project.tags.split(" ") if len(project.tags.strip()) > 0 else []
    resources = project.resource_set.all()
    context = {'project': project, 
               'links' : project.link_set.all(), 
               'rss_img_feed_url': project.imageset_feedurl, 
               'subprojects' : subprojects, 
               'implementors' : implementors, 
               'sectors' : sectors, 
               'tags' : tags,
               'resources' : resources}
    context.update(bbox)          
    
    return render_to_response('project.html', context,
                               context_instance=RequestContext(request)
                              )
                              
                              
def project_video(request, video_id):
    video=Video.objects.get(id=video_id)
    if(video.provider == VIDEO_PROVIDER.YOUTUBE):
        video_url = "http://www.youtube.com/v/%s&autoplay=1" % video.video_id
    else:
        video_url = "http://vimeo.com/moogaloop.swf?clip_id=%s&autoplay=1" % video.video_id
    return render_to_response("video.html", {'video_url' : video_url},
                             context_instance= RequestContext(request))
    

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
        
def check_username(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        responseText = "Sorry, the username is not available"
        try:
            user = User.objects.get(username=name)
        except Exception, ex:
            responseText = "Available"
        response = HttpResponse()
        response.write(responseText)
        return response
        
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
                         
def all_comments(request, project_id, mode):
    project = Project.objects.get(id=int(project_id))
    return render_to_response('all_comments.html', {'project' : project, 'mode' : mode}, 
                              context_instance=RequestContext(request))
                              
                              
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
    

def projects_search(request, project_manager=Project.objects):
    search_term = request.POST.get("q", "")
    qset = _construct_queryset_for_project_search(search_term)
    filtered_projects = project_manager.filter(qset, parent_project=None, status=PROJECT_STATUS.PUBLISHED).distinct()
    left, right, top, bottom = (-180, 180, -90, 90)

    return render_to_response("projects_search.html", { 'projects' : convert_to_json(filtered_projects),
                                                        'left' : left, 'right' : right,
                                                        'top' : top, 'bottom' : bottom,
                                                        'search_term' : search_term
                                                        },
                                                        context_instance=RequestContext(request))
   
def projects_tag_search(request, tag_term):
    projects = TaggedItem.objects.get_by_model(Project, Tag.objects.filter(name__in=[tag_term]))
    left, right, top, bottom = (-180, 180, -90, 90)
    
    return render_to_response(
                              'projects_search.html',
                              {
                               'projects' : convert_to_json(projects), 
                               'tag' : tag_term,
                               'search_term' : tag_term,
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
                                  
def _get_admin_model(admin_manager, details):
    try:
        adminModel = admin_manager.get(name=details['NAME_1'])
        adminModel.found = True
    except:
        adminModel = AdministrativeUnit()
        adminModel.found = False
    
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
    
def convert_admin_units_to_json(admin_unit):
    return json.dumps(admin_unit.__dict__)

def write_project_list_to_response(projects):
    response = HttpResponse()
    response.write(convert_to_json(projects))
    return response
    
def _check_for_comment_errors(username, email, comment_text, errors):
    if not username: errors['username'] = "Name is required"
    if not email: errors['email'] = 'Email is required'
    if not comment_text: errors['comment'] = 'Comment is required'
    if email and not EMAIL_REGEX.match(email): errors['email'] = "Invalid email"
    
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
    username = form.cleaned_data['username'].lower()
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
        

