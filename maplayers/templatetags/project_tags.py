# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
from maplayers.tag_utils import parse_img_feed, parse_youtube_feed
from maplayers.utils import is_empty
from maplayers.constants import PROJECT_STATUS, GROUPS, COMMENT_STATUS

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
        result = """<div id="edit_project">
                        <a href='/edit_project/%s/'>Edit this project</a>
                    </div>""" % project.id
    return result
    
@register.simple_tag
def projects_for_review_link(user):
    if (set([GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS]) & set([g.name for g in user.groups.all()])):
        return '<li><a href="/projects_for_review/">Projects for Review</li>'
    return ''
    
@register.simple_tag
def my_projects_header(user):
    result = '<tr>'
    result += '<th>Project title</th><th>Project Status</th><th>Edit</th>'
    if set((GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS)) & set([g.name for g in user.groups.all()]):
        result += '<th>Publish</th>'
	result +='</tr>'
	return result

@register.simple_tag
def my_project(project, user):
    result = '<tr id="project_%s"><td><a href="/projects/id/%s/">%s</a></td>' % (str(project.id),str(project.id), project.name)
    result += "<td>%s</td>" % status_text(project)
    result += '<td><a href="/edit_project/%s/">Edit</a></td>' % project.id
    if set((GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS)) & set([g.name for g in user.groups.all()]):
        result += '<td>%s</td>' % publish_text(project)
    result += '</tr>'
    return result
    
@register.simple_tag
def project_success_message(request):
    message = ""
    if request.session.has_key("success_message"):
        message = '<div class="flash_message_box"><div class="flash_message">%s</div></div>' % request.session["success_message"]
        del request.session["success_message"]
    return message
    
    
@register.simple_tag
def project_comments(project):
    result = ""
    comments = [comment for comment in project.projectcomments_set.all() if comment.status == COMMENT_STATUS.PUBLISHED]
    if comments:
        result += '<span>Comments: </span>'
    for comment in comments:
        result += '<div id="comment_%s" class="suggestion">' % comment.id
        result += '<span class="comment floatleft">%s</span>' % comment.text
        result += '<span class="comment_by">%s</span>' % comment.comment_by
        result += '<span class="comment_date">%s</span>' % comment.date
        result += '</div>'
    return result
    
    
def status_text(project):
    if not project.status == PROJECT_STATUS.REQUEST_CHANGES:
        return project.status
    return '<span class="first changes_preview" id="previewchanges_' + str(project.id) + '">' + project.status + '</span>'
    
def publish_text(project):
    if project.status == PROJECT_STATUS.PUBLISHED:
        return '<span class="unpublish_link first" id="%s">Unpublish</span>' % str(project.id)
    else:
        return '<span class="publish_link first" id="%s">Publish</span>' % str(project.id)

@register.simple_tag
def my_projects_link():
    result = """<a href='/my_projects/' id="my_projects">My Projects</a>"""
    return result

    
@register.simple_tag
def admin_links(project, user):
    result = ""
    if project.is_publishable_by(user):
        action = ("unpublish" if project.status == PROJECT_STATUS.PUBLISHED else "publish")
        input_field = '<input type="hidden" name="link" value="/projects/%s/%s/"/>' % (action, project.id)
        publish_span = '''<span class="publish_link" id="publish_%s">%s%s</span>''' % (str(project.id),  action.capitalize(), input_field)
        delete_span = '<span class="delete_link" id="delete_%s">Delete</span>' % (str(project.id))
        result = '<div class="admin_actions">%s | %s</div>' % (publish_span, delete_span)
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
def get_thumbnail_img(img_url):
    url = img_url.replace("_m.", "_s.")
    return url
    

@register.simple_tag
def youtube_playlist_player(playlist_id):
    return """
        <object class="youtube_playlist_player">
        <param name="movie" value="http://www.youtube.com/p/%(play_id)s&amp;hl=en&amp;fs=1"></param>
        <param name="allowFullScreen" value="true"></param>
        <param name="allowscriptaccess" value="always"></param>
        <param name="wmode" value="opaque"></param>
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
