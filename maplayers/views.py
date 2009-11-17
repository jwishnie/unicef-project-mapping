# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import decimal
import logging
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.http import HttpResponseRedirect 
from django.db.models import Q
from django.contrib.auth import logout

from maplayers.utils import is_empty
from maplayers.models import Project, Sector, Implementor
import decimal
from tagging.models import TaggedItem, Tag
from django.contrib.auth import logout
from maplayers.constants import PROJECT_STATUS

def homepage(request):
    sectors = _get_sectors(request)
    sector_ids = [sector.id for sector in sectors]
    implementors  = _get_implementors(request)
    implementor_ids = [implementor.id for implementor in implementors]
    left, bottom, right, top = _get_bounding_box(request)
    projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)
    return render_to_response(
                              'homepage.html', 
                              {
                               'projects' : projects, 
                               'sectors' : sectors, 
                               'tag': "",
                               'implementors' : implementors,
                               'left': left, 'right' : right,
                               'top': top, 'bottom' : bottom
                               },
                               context_instance=RequestContext(request)
                              ) 
    
    
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
    
    return render_to_response(
                              'projects_in_map.json',
                              {'projects': projects},
                               context_instance=RequestContext(request)
                              )

def project(request, project_id):
    try:
        logging.debug("View project details [project_id] : %s" % project_id)
        project = Project.objects.get(id=int(project_id))
        subprojects = Project.objects.filter(parent_project=int(project_id))
        implementors = ", ".join([implementor.name for implementor in Implementor.objects.filter(projects__in=[project])])
        tags = project.tags.split(" ")
    except Project.DoesNotExist:
        raise Http404
    return render_to_response('project.html', 
                              {'project': project, 
                               'links' : project.link_set.all(), 
                               'rss_img_feed_url': project.imageset_feedurl,
                               'subprojects' : subprojects,
                               'implementors' : implementors,
                               'youtube_playlist_id': project.youtube_playlist_id,
                               'tags' : tags,
                               },
                               context_instance=RequestContext(request)
                              )

def projects_search(request, search_term):
    qset = _construct_queryset_for_project_search(search_term)
    results = Project.objects.filter(qset, parent_project=None).distinct()

    return render_to_response(
                              'projects_search_result.json',
                              {'projects': results},
                               context_instance=RequestContext(request)
                              )
    
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

def _get_sectors_for_projects(projects):
    all_sectors = Sector.objects.all()
    sectors = [Sector.objects.filter(projects=project.id) for project in projects]
    result = []
    for project_sectors in sectors:
        for sector in project_sectors:
            result.append(sector)
    return list(set(result))

def _get_implementors_for_projects(projects):
    implementor = [Implementor.objects.filter(projects=project.id) for project in projects]
    result = []
    for project_implementor in implementor:
        for implementor in project_implementor:
            result.append(implementor)
    return list(set(result))
    
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
 
def _filter_projects_for_request(request):
    if request.GET.get('tag', ''):
      projects = _get_projects_with_tag(left, bottom, right, top, sector_ids, implementor_ids, request.GET.get('tag'))
    elif request.GET.get('search_term', ''):
      projects = _get_projects_with_tag(left, bottom, right, top, sector_ids, implementor_ids, request.GET.get('search_term'))
    else:
      projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)
    return projects
