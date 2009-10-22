# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response
from maplayers.models import Project, Sector
import decimal
from django.http import Http404
from django.db import connection


def homepage(request):
    projects = Project.objects.all()
    return render_to_response('homepage.html', {'projects' : projects}) 
    
def projects(request):
    projects = Project.objects.all()
    return render_to_response("projects.html", {'projects' : projects})
    
def projects_in_map(request, left, bottom, right, top):
    sectors = Sector.objects.all()
    sector_ids = [int(sector_id) for sector_id in request.POST.keys()] or \
        [sector.id for sector in sectors]
    left, bottom, right, top = \
        [decimal.Decimal(p) for p in (left, bottom, right, top)]
    
    projects = Project.objects.filter(
                                      longitude__gte=left, 
                                      longitude__lte=right,  
                                      latitude__gte=bottom, 
                                      latitude__lte=top, 
                                      sector__in=sector_ids
                                      ).distinct()
                                      
    return render_to_response(
                              'projects_in_map.html',
                              {'projects': projects, 'sectors' : sectors, 
                               "selected_sectors" : sector_ids,
                               "left" : left, 
                               "right" : right, 
                               "top" : top, 
                               "bottom" : bottom, 
                               "queries" : connection.queries}
                              )

def project(request, project_id):
    try:
        project = Project.objects.all()[int(project_id)]
        project_blog = project.blog_set.all()[0]
    except IndexError:
        raise Http404
    return render_to_response('project.html', 
                              {'project': project, 
                               'links' : project.link_set.all(), 
                               'blog': project_blog }) 
