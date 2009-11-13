# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
from maplayers.tag_utils import parse_img_feed, parse_youtube_feed
from maplayers.utils import is_empty
from maplayers.constants import PROJECT_STATUS

register = template.Library()  

@register.simple_tag
def project_links(titles_and_urls):
    link_id = 0
    link_tag = []
    for (title, url) in titles_and_urls:
        link_id += 1
        link_tag.append('<div id="link_%d"><label>Title: </label>' % link_id)
        link_tag.append('<input type="text" name="link_title" value="%s"></input><label>Url: </label>' % title)
        link_tag.append('<input type="text" name="link_url"  value="%s"></input></div>' % url)
    return "".join(link_tag).encode("UTF-8")
    
@register.simple_tag
def edit_project_link(project, user):
    result = ""
    if project.is_editable_by(user):
        result = """<p>
                        <a href='/edit_project/%s/' id="edit_project">Edit this project</a>
                    </p>""" % project.id
    return result
    

@register.simple_tag
def my_project(project, user):
    result = "<tr><td>%s</td>" % project.name
    result += "<td>%s</td>" % project.status
    result += '<td><a href="/edit_project/%s/">Edit</a></td>' % project.id
    result += '<td>%s</td>' % review_text(project)
    result += '<td>%s</td></tr>' % publish_text(project, user)
    return result
    
    
def review_text(project):
    if project.status == PROJECT_STATUS.DRAFT:
        return '<a href="/projects/submit_for_review/%s/">Submit for review</a>' % project.id
    elif project.status == PROJECT_STATUS.REVIEW:
        return "Under Review"
    else:
        return project.status
    
def publish_text(project, user):
    if project.is_publishable_by(user):
        if project.status == PROJECT_STATUS.PUBLISHED:
            return '<a href="/projects/unpublish/%s/">Unpublish</a>' % project.id
        else:
            return '<a href="/projects/publish/%s/">Publish</a>' % project.id

@register.simple_tag
def my_projects_link():
    result = """<a href='/my_projects/' id="my_projects">My Projects</a>"""
    return result

    
@register.simple_tag
def publish_project_link(project, user):
    result = ""
    if project.is_publishable_by(user):
        action = ("unpublish" if project.status == PROJECT_STATUS.PUBLISHED else "publish")
        result = '''<div class="publish_div">
                        <a href="#publish" class="publish_link" id="%s">%s</a>
                    </div>''' % (str(project.id), action.capitalize())
    if project.status == PROJECT_STATUS.DRAFT:
        result += '''<div class="review_div">
                            <a href="#review" class="review_link" id="%s">%s</a>
                    </div>''' % (str(project.id), "Submit for Review")
    return result
    

@register.simple_tag
def add_project_link():
    result = """<a href='/add_project/' id="add_project">Add a new project</a>"""
    return result    
    
    
@register.simple_tag
def file_list(resources):
    result = []
    for index, resource in enumerate(resources):
        filename = "_".join(resource.filename.split("_")[1:])
        filesize = resource.filesize / 1024
        result.append('<li id="file-%s" class="file" style="background-color: transparent;">' % str(index+1))
        result.append('<span class="file-title">%s</span>' % filename)
        result.append('<span class="file-size">%s KB</span>' % str(filesize))
        result.append('<a class="file-remove-edit" href="#">remove</a>')
        result.append('</li>')
        
    result = "".join(result)
    if result:
        result = '<ul id="file-list">' + result + '</ul>'
    return result
    
    
 
@register.tag(name='parse_img_rss_feed')
def do_parse_img_rss_feed(parser, token):
    return ParseImgRssFeedNode()
    
class ParseImgRssFeedNode(template.Node):
    """ Render node for parse_img_rss_feed """
    def __init__(self):
        pass
    
    def render(self, context):
        """
        Expects context to hold:
        - rss_img_feed_url
        - rss_img_feed_max_entries (optional)
        
        Adds a dictionary named 'rss_img_feed' to the context of form:
        {
            feed: {
                    title: 'some title',
                    url: 'http://feedurl...'
                   }
            images: [
                        { type: 'image/jpeg', # mime type
                          url: 'http://etc...',
                          caption: 'some caption'
                        },
                        ...
                    ]
        }  
        
        """
        
        # pull vars
        url = None
        if context.has_key('rss_img_feed_url'):
            url = context['rss_img_feed_url']
            if is_empty(url):
                url = None
           
        max_ = None
        if context.has_key('rss_img_feed_max_entries'):
            max_ = int(context['rss_img_feed_max_entries'])
        
        # parse_feed does all the work
        context['rss_img_feed'] = ( parse_img_feed(url, max_) if \
                                  not url is None else \
                                   { 'feed': {'title': '', 'url': ''}, 'images': []} )

        return ''
  


@register.simple_tag
def youtube_playlist_player(playlist_id):
    return """
        <object class="youtube_playlist_player">
        <param name="movie" value="http://www.youtube.com/p/%(play_id)s&amp;hl=en&amp;fs=1"></param>
        <param name="allowFullScreen" value="true"></param>
        <param name="allowscriptaccess" value="always"></param>
        <embed class="youtube_playlist_player" src="http://www.youtube.com/p/%(play_id)s&amp;hl=en&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true"></embed>
        </object>

        """ % {'play_id':playlist_id}

"""
YouTube feed

DEPRECATED -- Use the playlist player tag instead
  
"""
  
@register.tag(name='parse_youtube_rss_feed')
def do_parse_youtube_rss_feed(parser, token):
    return ParseYouTubeRssFeedNode()
    
class ParseYouTubeRssFeedNode(template.Node):
    """ Render node for parse_img_rss_feed """
    def __init__(self):
        pass
    
    def render(self, context):
        """
        Expects context to hold:
        - rss_youtube_feed_url
        - rss_youtube_feed_max_entries (optional)
        
        Adds a dictionary named 'rss_youtube_feed' to the context of form:
        {
            feed: {
                    title: 'some title',
                    url: 'http://feedurl...'
                   }
            videos: [
                        { type: 'image/jpeg', # mime type
                          url: 'http://etc...',
                          caption: 'some caption'
                        },
                        ...
                    ]
        }  
        
        """
        
        # pull vars
        url = None
        if context.has_key('rss_youtube_feed_url'):
            url = context['rss_youtube_feed_url']
            if is_empty(url):
                url = None
           
        max_ = None
        if context.has_key('rss_youtube_feed_max_entries'):
            max_ = int(context['rss_youtube_feed_max_entries'])
        
       
        # parse_feed does all the work
        context['rss_youtube_feed'] = ( parse_youtube_feed(url, max_) if \
                                  not url is None else \
                                   { 'feed': {'title': '', 'url': ''}, 'videos': []} )

        return ''                              
