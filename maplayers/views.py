# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import decimal
import logging
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.http import HttpResponseRedirect 
from django.db.models import Q

from maplayers.utils import is_empty
from maplayers.models import Project, Sector, Implementor

from django.contrib.auth import logout

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
    except Project.DoesNotExist:
        raise Http404
    return render_to_response('project.html', 
                              {'project': project, 
                               'links' : project.link_set.all(), 
                               'rss_img_feed_url': project.imageset_feedurl,
                               'subprojects' : subprojects,
                               'implementors' : implementors,
                               'rss_youtube_feed_url':'feed://gdata.youtube.com/feeds/api/users/' + project.youtube_username +'/uploads',
                               'rss_youtube_feed_max_entries': 4,
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

def _get_implementors_for_projects_in_result(results):
    pass
    
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
