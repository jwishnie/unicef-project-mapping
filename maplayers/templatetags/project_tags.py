# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
from maplayers.tag_utils import parse_img_feed
from maplayers.utils import is_empty
from maplayers.constants import PROJECT_STATUS, GROUPS, COMMENT_STATUS, VIDEO_PROVIDER
from maplayers.models import Project, ProjectComment, ReviewFeedback
from maplayers.resource_icons import ResourceIcon

register = template.Library()  

@register.simple_tag
def sector_checkbox(sector, sectors):
    result = '<input type="checkbox" name="sector_%s" value="%s" class="sectorbox" ' % (sector.id, sector.name)
    if sector in sectors:
        result += 'checked="checked"'
    result += '/>'
    return result
  
@register.simple_tag
def implementor_checkbox(implementor, implementors):
    result = '<input type="checkbox" name="implementor_%s" value="%s" class="implementorbox" ' % (implementor.id, implementor.name)
    if implementor in implementors:
        result += 'checked="checked"'
    result += '/>'
    return result
    

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
        result = """<li class='first'>
                            <a href='/edit_project/%s/'>Edit this project</a>
                        </li>""" % project.id
    return result
    
    
@register.simple_tag
def add_sub_project_link(project, user):
    result = ""
    if project.is_editable_by(user) and project.is_parent_project():
        result = """<li>
                        <a href='/add_project?parent_id=%s'>Add SubProject</a>
                    </li>""" % project.id
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
        
    result = '''<h4>Related Videos :</h4>
                    <div id="current_video" class="floatleft">    
                        <object width="400" height="385">
                        <param name="allowfullscreen" value="true">
                        <param name="allowscriptaccess" value="always"> 
                        <param name="movie" value="%s">
                        <embed src="%s" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="400" height="385">
                        </object> 
                    </div>''' % (video_url, video_url)
    return result
               

@register.simple_tag
def video_playlist(project):
    thumbnail_urls = []
    videos = project.video_set.all()
    if len(videos) < 2: return ""
    result = "<div id='video_playlist' class='floatleft'><ul>"
    
    for video in videos:
        if(video.provider == VIDEO_PROVIDER.YOUTUBE):
            thumbnail_url = "http://img.youtube.com/vi/%s/default.jpg" % video.video_id
            result += "<li><img src='%s' id='video_%s' class='video_thumbnail'></li>"  % (thumbnail_url, video.id)
        else:
            pass
            
    result += "</ul></div>"
    return result
    

@register.simple_tag
def projects_for_review_link(user):
    if (set([GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS]) & set([g.name for g in user.groups.all()])):
        projects_for_review_count = Project.objects.filter(status=PROJECT_STATUS.REVIEW).count()
        if projects_for_review_count:
            return '<li id="projs_for_review_li"><a href="/projects_for_review/">Projects for Review<span class="notification">%s</span></a></li>' % str(projects_for_review_count)
        else:
            return '<li id="projs_for_review_li"><a href="/projects_for_review/">Projects for Review</a></li>'
    return ''

@register.simple_tag
def site_admin_link(user):
    if (set([GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS]) & set([g.name for g in user.groups.all()])):
        return '<li id="site_admin_li"><a href="/admin/">Site admin</a></li>'
    else:    
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
def project_comments(project, mode="display", number='3'):
    result = ""
    comments = [comment for comment in project.projectcomment_set.all() if comment.status == COMMENT_STATUS.PUBLISHED]
    number = int(number)
    comments_list = comments if number == -1 else comments[0:number]
    if comments and number!= -1:
        if(mode=="display"):
            result += '<span>So far there\'s been %d comments </span>' % len(comments)
        else:
            result += '<span class="comments_header">Comments:</span>'    
    for comment in comments_list:
        result += '<div id="comment_%s">' % comment.id
        result += '<span class="comment_text">%s</span>' % comment.text
        result += '<p class="comment_metainfo">'
        result += '<span class="comment_by">By: %s,</span>' % comment.comment_by
        result += '<span class="comment_date"> %s</span>' % comment.date.strftime("%B %d, %Y")
        result += '</p>'
        if(mode=="edit"):
            result += '<span class="delete_comment" id="delete_comment_%s">Remove</span>' % comment.id
        result += '</div>'
    if number != -1 and len(comments) > 3:
        result += '<span><a href="/project/comments/%s/all/%s/">See all comments >></a></span>' % (str(project.id), mode)
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
        return '<a href="/my_projects/" id="my_projects_link">My Projects<span class="notification">%s</span></a>' % str(my_project_notifications)
    else:
        return '<a href="/my_projects/" id="my_projects_link">My Projects</a>'

    
@register.simple_tag
def admin_links(project, user):
    result = ""
    if project.is_publishable_by(user):
        action = ("unpublish" if project.is_published() else "publish")
        input_field = '<input type="hidden" name="link" value="/projects/%s/%s/"/>' % (action, project.id)
        publish_span = '''<li><span class="publish_link" id="publish_%s">%s%s</span></li>''' % (str(project.id),  action.capitalize(), input_field)
        delete_span = '<li><span class="delete_link" id="delete_%s">Delete</span></li>' % (str(project.id))
        result = '%s %s' % (publish_span, delete_span)
    return result
    
@register.simple_tag
def show_project_links(links):
    result = ''
    for link in links:
        link_url = link.url if link.url.startswith("http") else "http://" + link.url
        result += '<div class="sub_div"><a href="%s" target="_new">%s</a></div>' % (link_url, link.title)
    return result


@register.simple_tag
def add_project_link():
    result = """<a href='/add_project?parent_id=' id="add_project_link">Add project</a>"""
    return result    
    
@register.simple_tag
def sign_up_link():
    result = """<li class="last"><a href='/user_registration' id="sign_up">Sign up</a></li>"""
    return result   

@register.simple_tag
def add_admin_unit_related_links(user):
    if (set((GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS)) & set([g.name for g in user.groups.all()])):            
        result = """<li id='add_admin_unit_li'><a href='/add_admin_unit' id='add_admin_unit_lnk'>Add admin unit</a></li>
        <li id='admin_units_li'><a href='/admin_units' id='admin_units_links'>Admin Units</a></li>
        <li id="add_kml_li"><a href="/add_kml" id="add_kml_link">Add kml layer</a></li>"""
        return result
    else:
        return ''    
            
@register.simple_tag
def project_image(project):
    result = []
    filename = project.project_image
    if filename :
        result.append('<img alt="%s" src="../../static/project-photos/%s" />' % (filename, filename))
        result.append('<a class="photo-remove-edit" href="#">remove</a>')
        result.append('<a href="#" style="display:none" id="photo-attach" class="photo-attach" name="photo-attach">Attach a file</a>')
    else:
        result.append('<a href="#" id="photo-attach" class="photo-attach" name="photo-attach">Attach a file</a>')
        
    result = "".join(result)
    return result
    
@register.simple_tag
def file_list(resources):
    result = []
    for index, resource in enumerate(resources):
        filename = "_".join(resource.filename.split("_")[1:])
        file_extension = filename.split(".")[-1:][0]
        resource_icon = ResourceIcon().icon(file_extension)
        filesize = resource.filesize / 1024
        result.append('<li id="file-%s" class="file" style="background-color: transparent;">' % str(index+1))
        result.append('<span class="resource_icon" style="background:transparent url(%s) no-repeat scroll top left"></span>' % resource_icon)
        result.append('<div>')
        result.append('<span class="file-title">%s</span>' % filename)
        result.append('<span class="file-size">%s KB</span>' % str(filesize))
        result.append('<a class="file-remove-edit" href="#">remove</a>')
        result.append('</div>')
        result.append('</li>')
        
    result = "".join(result)
    if result:
        result = '<ul id="file-list">' + result + '</ul>'
    return result
    
@register.simple_tag
def resource_list(resources):
    result = []
    html = ""
    if resources:
        for index, resource in enumerate(resources):
            filename = resource.original_file_name()
            resource_icon = ResourceIcon().icon(resource.file_extension)
            if resource.is_audio_file:
                pass
            else:
                result.append('<div>')
                result.append('<span class="resource_icon" style="background:transparent url(%s) no-repeat scroll top left"></span>' % resource_icon)
                result.append('<div>')
                result.append('<div class="sub_div"><a href="/static/resources/%s">%s</a></div>' %(filename, resource.title))
                result.append('</div>')
            
        html = "".join(result)
    return html

@register.simple_tag
def resource_icon(resource):
    file_extension = resource.title.split(".")[-1:][0]
    return ResourceIcon().icon(file_extension)
        
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
    if(img_url.__contains__("flickr")):
        url = img_url.replace("_m.", "_s.")
    else:
        url = img_url.replace("/s144/", "/s72/")
    return url
    
@register.simple_tag
def get_img(img_url):
    if(img_url.__contains__("flickr")):
        url = img_url.replace("_m.", ".")
    else:
        url = img_url.replace("/s144/", "/s720/")
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
        
        
@register.simple_tag
def video_url_tag(video_urls):
    if len(video_urls) < 2:
        video_url = video_urls[0] if video_urls else ""
        return '''<div id="video_urls">
        			<div id="video_url_1" class="add_video_url">
        				<label>Video URL : </label>
        				<input type="text" name="video_url_1" value="%s"></input>
        			</div>	
        		</div>''' % video_url
        		
    i = 1
    result = '<div id="video_urls">'
    for video_url in video_urls:
        result += '<div id="video_url_%s" class="add_video_url"><label>Video URL : </label>' % str(i)
        result += '<input type="text" name="video_url_%s" value="%s"></input>' % (str(i), video_url)
        result += '<input type="radio" name="default_video" value="video_%s"></input>' % str(i)
        result += '<span class="remove_video" id="remove_video_%s">remove</span></div>' % str(i)
        i += 1
    result += "</div>"
    return result
        
    

