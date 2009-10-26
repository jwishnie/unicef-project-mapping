# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response
from maplayers.models import Project, Sector, Implementor, SubProject
import decimal
from django.http import Http404
from maplayers.utils import is_empty


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
                               'rss_youtube_feed_max_entries': 5}
                              )
    else:
        return render_to_response('gallery.html',
                              {'rss_img_feed_url': urls[gallery_type],
                               'rss_img_feed_max_entries': 5}
                              )

def homepage(request):
    sectors = __get_sectors__(request)
    sector_ids = [sector.id for sector in sectors]
    implementors  = __get_implementors__(request)
    implementor_ids = [implementor.id for implementor in implementors]
    left, bottom, right, top = __get_bounding_box__(request)
    
    projects = __get_projects__(left, bottom, right, top, sector_ids, implementor_ids)
    return render_to_response(
                              'homepage.html', 
                              {'projects' : projects, 
                               'sectors' : sectors, 
                               'implementors' : implementors,
                               'left': left, 'right' : right,
                               'top': top, 'bottom' : bottom}
                              ) 
    
def projects(request):
    projects = Project.objects.all()
    return render_to_response("projects.html", {'projects' : projects})
    
def projects_in_map(request, left, bottom, right, top):
    sector_ids =  __filter_ids__(request, "sector") or \
                [sector.id for sector in Sector.objects.all()]
    implementor_ids =  __filter_ids__(request, "implementor") or \
                [implementor.id for implementor in Implementor.objects.all()]
        
    projects = __get_projects__(left, bottom, right, top, sector_ids, implementor_ids)
    return render_to_response(
                              'projects_in_map.json',
                              {'projects': projects}
                              )

def project(request, project_id):
    try:
        project = Project.objects.all()[int(project_id)]
        subprojects = SubProject.objects.filter(
                                                project__id=int(project_id) + 1
                                                ).distinct()
    except IndexError:
        raise Http404
    return render_to_response('project.html', 
                              {'project': project, 
                               'links' : project.link_set.all(), 
                               'subprojects' : subprojects,
                               }) 
                              

def __filter_ids__(request, filter_name):
    """
    returns a list of selected filter_id from the request
    """
    return [int(filter_id.split("_")[1]) for filter_id in \
            request.GET.keys() if filter_id.find(filter_name +"_") >=0]
    
def __get_sectors__(request):
    """
    returns a list of selected sectors present in the request OR all sectors as default
    """
    ids = __filter_ids__(request, "sector")
    return Sector.objects.filter(id__in=ids) if ids else Sector.objects.all()
    
def __get_implementors__(request):
    """
    returns a list of selected implementors present in the request OR all implementors as default
    """
    ids = __filter_ids__(request, "implementor")
    return Implementor.objects.filter(id__in=ids) if ids else Implementor.objects.all()
    
def __get_projects__(left, bottom, right, top, sector_ids, implementor_ids):
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
                                      
                            
def __get_bounding_box__(request):
    left = request.GET.get('left', '-180')
    right = request.GET.get('right', '180')
    top = request.GET.get('top', '90')
    bottom = request.GET.get('left', '-90')
    return (left, bottom, right, top)
    
    
