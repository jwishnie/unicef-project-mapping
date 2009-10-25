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
            'http://picasaweb.google.com/data/feed/base/user/flyvideo2/albumid/5228431042645681505?alt=rss&kind=photo&hl=en_US'
            }
    return render_to_response('gallery.html',
                              {'rss_img_feed_url': urls[gallery_type],
                               'rss_img_feed_max_entries': 5}
                              )

def homepage(request):
    sectors = Sector.objects.all()
    implementors  = Implementor.objects.all()
    projects = Project.objects.all()
    return render_to_response(
                              'homepage.html', 
                              {'projects' : projects, 
                               'sectors' : sectors, 
                               'implementors' : implementors}
                              ) 
    
def projects(request):
    projects = Project.objects.all()
    return render_to_response("projects.html", {'projects' : projects})
    
def projects_in_map(request, left, bottom, right, top):
    sector_ids =  _filter_ids(request, "sector") or \
                [sector.id for sector in Sector.objects.all()]
    implementor_ids =  _filter_ids(request, "implementor") or \
                [implementor.id for implementor in Implementor.objects.all()]
        
    left, bottom, right, top = \
        [decimal.Decimal(p) for p in (left, bottom, right, top)]
    
    projects = Project.objects.filter(
                                      longitude__gte=left, 
                                      longitude__lte=right,  
                                      latitude__gte=bottom, 
                                      latitude__lte=top, 
                                      sector__in=sector_ids,
                                      implementor__in=implementor_ids,
                                      ).distinct()
                                      
    return render_to_response(
                              'projects_in_map.json',
                              {'projects': projects,
                               "left" : left, 
                               "right" : right, 
                               "top" : top, 
                               "bottom" : bottom}
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
                              

def _filter_ids(request, filter_name):
    """
    returns a list of selected filter_id from the request
    """
    return [int(filter_id.split("_")[1]) for filter_id in request.POST.keys() if filter_id.find(filter_name +"_") >=0]
