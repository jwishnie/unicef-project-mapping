from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from maplayers.models import Project, Sector, Implementor
from maplayers.forms import ProjectForm

@login_required
def add_project(request):
    sectors = ", ".join([sector.name for sector in Sector.objects.all()[:5]])
    implementors = ", ".join([implementor.name for implementor in Implementor.objects.all()[:5]])
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid(): 
            _create_project(form)
            return HttpResponseRedirect('/project_created_successfully/')
        else: 
            return render_to_response(
                                      'add_project.html', 
                                      {
                                       'form': form,
                                      'sectors' : sectors, 
                                      'implementors' : implementors
                                      },
                                      context_instance=RequestContext(request)
                                      ) 
    else: 
        form = ProjectForm()
        return render_to_response(
                                  'add_project.html', 
                                  {
                                   'form': form,
                                  'sectors' : sectors, 'implementors' : implementors
                                  },
                                  context_instance=RequestContext(request)
                                  ) 
        
        
def _create_project(form):
    p = Project()
    p.name = form.cleaned_data['name']
    p.description = form.cleaned_data['description']
    p.latitude = form.cleaned_data['latitude']
    p.longitude = form.cleaned_data['longitude']
    p.location = form.cleaned_data['location']
    p.website_url = form.cleaned_data['website_url']
    p.project_image = form.cleaned_data['project_image']
    sector_names = form.cleaned_data['project_sectors']
    implementor_names = form.cleaned_data['project_implementors']
    p.youtube_username = form.cleaned_data['youtube_username']
    p.imageset_feedurl = form.cleaned_data['imageset_feedurl']
    p.save()
    _add_sectors_and_implementors(p, sector_names, implementor_names)



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
    
    
    
    