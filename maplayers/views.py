# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import decimal
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext

from maplayers.utils import is_empty
from maplayers.models import Project, Sector, Implementor


def gallery(request, gallery_type):
    if is_empty(gallery_type):
        gallery_type = 'flickr'
        
    urls = { 'flickr': \
            'feed://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us',
            'picasa': \
            'http://picasaweb.google.com/data/feed/base/user/flyvideo2/albumid/5228431042645681505?alt=rss&kind=photo&hl=en_US',
            'youtube': \
            'feed://gdata.youtube.com/feeds/api/users/unicef/uploads',
            }
    
    if gallery_type=='youtube':
        return render_to_response('youtube_gallery.html',
                              {'rss_youtube_feed_url': urls[gallery_type],
                               'rss_youtube_feed_max_entries': 5},
                               context_instance=RequestContext(request)
                              )
    else:
        return render_to_response('gallery.html',
                              {'rss_img_feed_url': urls[gallery_type],
                               'rss_img_feed_max_entries': 5},
                               context_instance=RequestContext(request)
                              )

def homepage(request):
    sectors = _get_sectors(request)
    sector_ids = [sector.id for sector in sectors]
    implementors  = _get_implementors(request)
    implementor_ids = [implementor.id for implementor in implementors]
    left, bottom, right, top = _get_bounding_box(request)
    projects = _get_projects(left, bottom, right, top, sector_ids, implementor_ids)
    return render_to_response(
                              'homepage.html', 
                              {'projects' : projects, 
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
        project = Project.objects.get(id__exact=project_id)
        subprojects = Project.objects.filter(parent_project=project_id)
        implementors = ", ".join([implementor.name for implementor in Implementor.objects.filter(projects__in=project_id)])
    except Project.DoesNotExist:
        raise Http404
    return render_to_response('project.html', 
                              {'project': project, 
                               'links' : project.link_set.all(), 
                               'rss_img_feed_url': project.imageset_feedurl,
                               'subprojects' : subprojects,
                               'implementors' : implementors,
                               },
                               context_instance=RequestContext(request)
                               ) 

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
