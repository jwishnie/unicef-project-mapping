# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
from maplayers.tag_utils import parse_img_feed
from maplayers.utils import is_empty
from maplayers.constants import PROJECT_STATUS, GROUPS, COMMENT_STATUS, VIDEO_PROVIDER
from maplayers.models import Project, ProjectComment, ReviewFeedback

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
        if project.is_parent_project():
            result = """<div id="edit_project">
                            <a href='/edit_project/%s/'>Edit this project</a>
                        </div>""" % project.id
        else:
            result = """<div id="edit_project">
                            <a href='/edit_project/%s/'>Edit this project</a>
                        </div>""" % project.id
    return result
    
@register.simple_tag
def add_sub_project_link(project, user):
    result = ""
    if project.is_editable_by(user) and project.is_parent_project():
        result = """<div id="add_sub_project">
                        <a href='/add_project?parent_id=%s'>Add SubProject</a>
                    </div>""" % project.id
    return result

@register.simple_tag
def add_parent_project_input_tag(parent_project):
    result = ""
    if parent_project:
        result = """<input type="hidden" name="parent_project_id" value="%s"></input>""" % parent_project.id
    return result

@register.simple_tag
def sub_project_header(parent_project):
    result = ""
    if parent_project:
        result = """
				<div>
                    <input type="hidden" name="parent_project_id" value="%s"></input>
					<label for="id_parent_project">Parent Project:</label> 
                        %s
				</div>
                 """ % (parent_project.id, parent_project.name)
    return result
    
@register.simple_tag
def project_video(project):
    video = project.default_video()
    if not video: return ""
    if(video.provider == VIDEO_PROVIDER.YOUTUBE):
        video_url = "http://www.youtube.com/v/" + video.video_id
    else:
        video_url = "http://vimeo.com/moogaloop.swf?clip_id=" + video.video_id
        
    result = '''<object width="400" height="385">
                    <param name="allowfullscreen" value="true">
                    <param name="allowscriptaccess" value="always"> 
                    <param name="movie" value="%s">
                    <embed src="%s" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="400" height="385">
               </object> ''' % (video_url, video_url)
    return result
               

@register.simple_tag
def projects_for_review_link(user):
    if (set([GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS]) & set([g.name for g in user.groups.all()])):
        projects_for_review_count = Project.objects.filter(status=PROJECT_STATUS.REVIEW).count()
        if projects_for_review_count:
            return '<li><a href="/projects_for_review/">Projects for Review<span class="notification">%s</span></a></li>' % str(projects_for_review_count)
        else:
            return '<li><a href="/projects_for_review/">Projects for Review</a></li>'
    return ''
    
    
@register.simple_tag
def my_projects_header(user):
    result = '<tr>'
    result += '<th>Project title</th><th>Project Status</th><th>Edit</th>'
    if set((GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS)) & set([g.name for g in user.groups.all()]):
        result += '<th>Publish</th>'
    result += "<th>Comments</th>"
    result +='</tr>'
    return result
    

@register.simple_tag
def my_project(project, user):
    result = '<tr id="project_%s"><td><a href="/projects/id/%s/">%s</a></td>' % (str(project.id),str(project.id), project.name)
    result += "<td>%s</td>" % status_text(project)
    result += '<td><a href="/edit_project/%s/">Edit</a></td>' % project.id
    if set((GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS)) & set([g.name for g in user.groups.all()]):
        result += '<td>%s</td>' % publish_text(project)
    no_of_comments = project.projectcomment_set.filter(status=COMMENT_STATUS.UNMODERATED).count()
    if no_of_comments:
        comments_text = "comments" if no_of_comments>1 else "comment"
        result += '<td><a href="/projects/comments/%s" class="comment_number"/>%s %s</td>' % (str(project.id), str(no_of_comments), comments_text)
    else:
        result += '<td>No comments</td>'
    result += '</tr>'
    return result
    
@register.simple_tag
def flash_message(request):
    message = ""
    if request.session.has_key("message"):
        message = '<div class="flash_message_box"><div class="flash_message">%s</div></div>' % request.session["message"]
        del request.session["message"]
    return message
    
@register.simple_tag
def project_comments(project, mode="display"):
    result = ""
    comments = [comment for comment in project.projectcomment_set.all() if comment.status == COMMENT_STATUS.PUBLISHED]
    if comments:
        if(mode=="display"):
            result += '<span>So far there\'s been %d comments </span>' % len(comments)
        else:
            result += '<span class="comments_header">Comments:</span>'    
    for comment in comments:
        result += '<div id="comment_%s">' % comment.id
        result += '<span class="comment_text">%s</span>' % comment.text
        result += '<p class="comment_metainfo">'
        result += '<span class="comment_by">By: %s,</span>' % comment.comment_by
        result += '<span class="comment_date"> %s</span>' % comment.date.strftime("%B %d, %Y")
        result += '</p>'
        if(mode=="edit"):
            result += '<span class="delete_comment" id="delete_comment_%s">Remove</span>' % comment.id
        result += '</div>'
    return result
    
    
def status_text(project):
    if not project.status == PROJECT_STATUS.REQUEST_CHANGES:
        return project.status
    return '<span class="first changes_preview" id="previewchanges_' + str(project.id) + '">' + project.status + '</span>'
    
def publish_text(project):
    if project.is_published():
        return '<span class="unpublish_link first" id="%s">Unpublish</span>' % str(project.id)
    else:
        return '<span class="publish_link first" id="%s">Publish</span>' % str(project.id)

@register.simple_tag
def my_projects_link(user):
    projects = Project.objects.select_related(depth=1).filter(created_by=user)
    project_comments_count = ProjectComment.objects.filter(
                                project__in=projects,
                                status=COMMENT_STATUS.UNMODERATED
                             ).count()
    change_requested_count = len([project for project in projects if project.status == PROJECT_STATUS.REQUEST_CHANGES])
    my_project_notifications = project_comments_count + change_requested_count
    if my_project_notifications:
        return '<a href="/my_projects/" id="my_projects">My Projects<span class="notification">%s</span></a>' % str(my_project_notifications)
    else:
        return '<a href="/my_projects/" id="my_projects">My Projects</a>'

    
@register.simple_tag
def admin_links(project, user):
    result = ""
    if project.is_publishable_by(user):
        action = ("unpublish" if project.is_published() else "publish")
        input_field = '<input type="hidden" name="link" value="/projects/%s/%s/"/>' % (action, project.id)
        publish_span = '''<span class="publish_link" id="publish_%s">%s%s</span>''' % (str(project.id),  action.capitalize(), input_field)
        delete_span = '<span class="delete_link" id="delete_%s">Delete</span>' % (str(project.id))
        result = '<div class="admin_actions">%s | %s</div>' % (publish_span, delete_span)
    return result
    

@register.simple_tag
def add_project_link():
    result = """<a href='/add_project?parent_id=' id="add_project">Add a new project</a>"""
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
        result.append('<a class="file-remove-edit" href="#">removef tfytrfytf</a>')
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
def get_img(img_url):
    url = img_url.replace("_m.", ".")
    return url

@register.simple_tag
def youtube_playlist_player(playlist_id):
    return """
        <object class="youtube_playlist_player">
        <param name="movie" value="http://www.youtube.com/p/%(play_id)s&amp;hl=en&amp;fs=1"></param>
        <param name="allowFullScreen" value="true"></param>
        <param name="allowscriptaccess" value="always"></param>
        <param name="wmode" value="opaque">
        <embed class="youtube_playlist_player" src="http://www.youtube.com/p/%(play_id)s&amp;hl=en&amp;fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" wmode="opaque" />
        </object>

        """ % {'play_id':playlist_id}

