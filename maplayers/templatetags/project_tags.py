# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
from maplayers.tag_utils import parse_img_feed, parse_youtube_feed
from maplayers.utils import is_empty

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
  
"""
YouTube feed
  
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
