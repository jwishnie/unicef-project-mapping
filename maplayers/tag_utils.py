# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Utilities for dealing with RSS Feeds

"""
import urlparse
import re
import feedparser
from django.core.cache import cache
from maplayers.utils import is_empty


IMAGE_TYPES = (
               'image/jpeg',
               'image/pjpeg',
               'image/gif',
               'image/png'
               )

FLICKR_FEED_FORMAT='format=atom'

"""

Turns out this is more compicated since it has to handle template variables.

Not worth implementing at this time.

def parse_tag_args(tag_token=None, var_list=None, var_name_default=None):    
    if is_empty(tag_token) or \
        is_empty(var_list):
        raise ValueError
    
    # figure out var name
    var_name = None
    tokes = tag_token.split_contents()
    if len(tokes)>=3:
        if tokes[-2].lower() == 'as':
            var_name = tokes[-1]
            # remove 'as var_name' from list
            tokes = tokes[:-2]
        
    if var_name is None:
        var_name = var_name_default
    
    if var_name is None:
        var_name = tokes[0]
        
    # parse args (skipping tagname)
    args = []
    for key,val in (arg.split('=',1) for arg in tokes[1:]):
        try:
            klass = var_list[key]
            arg = klass(val)
            first_last = "".join((arg[0],arg[-1]))
            # strip quotes
            if klass == str and \
                (first_last == '""' or first_last == "''"):
                arg = arg[1:-1]
            args.append(arg)
        except:
            raise ValueError
    
    return args 
"""

def clean_feed_url(url):
    """
    Clean up urls for use with universal parser which:
    - doesn't understand 'feed'
    - doesn't seem to read flickr rss2.0 format without enclosures
    
    This basically encapsulates hacks need to get the feeds from
    different services to work properly with the feed parser library
    
    """
    
    # swap out 'feed:' for 'http:' as the python libraries seem to choke on it
    url = re.sub(r'^feed:', 'http:',url)
    
    # parse URL, note this call does _not_ throw any exceptions
    # and always returns something, even if garbage
    split_url = urlparse.urlsplit(url)
    scheme, loc, path, query, frag = split_url
    
    # if this is flickr, make sure the format is what we want
    if loc.endswith('flickr.com'):
        m = re.search(r'(format=[^&]+)', query)
        if m is not None:
            query = query.replace(m.group(1), FLICKR_FEED_FORMAT)
        else:
            prefix = ('&' if len(query)>0 else '')
            query = "%s%s%s" % (query, prefix, FLICKR_FEED_FORMAT)
     
    return urlparse.urlunsplit((scheme, loc, path, query, frag))
    
def parse_img_feed(url, max_entries=None):
    if is_empty(url):
        return []
    
    # fix url for use by feedparser
    clean_url = clean_feed_url(url)
                                
    # Try to retrieve from cache using cleaned url
    parsed_feed = cache.get(clean_url)
    
    # if we got one, make a etags or modified request to see if any updates
    if parsed_feed is not None:
        updated_feed = None
        if parsed_feed.has_key('etag'):
            updated_feed = feedparser.parse(clean_url, etag=parsed_feed.etag)
        elif parsed_feed.has_key('modified'):
            updated_feed = \
                feedparser.parse(clean_url, modified=parsed_feed.modified)
                
        # did we get any changes?  
        if updated_feed is not None and updated_feed.status == 200:
            parsed_feed = updated_feed
            cache.set(clean_url, parsed_feed)
    else:
        # no cached one, go get it
        parsed_feed = feedparser.parse(clean_url)
        cache.set(clean_url, parsed_feed)
        
    # extract media info
    max_ = (int(max_entries) \
            if max_entries is not None else 0)
    if max_ < 0:
        max_ = 0
        
    media = []
    for e in parsed_feed.entries:
        if max_ == 0:
            break
        
        # check for all required info
        if e.has_key('enclosures') and \
            len(e.enclosures)>0:
            img = e.enclosures[0]
            
            if img.has_key('type') and \
                img.type in IMAGE_TYPES and \
                img.has_key('href'):
            
                # add info
                media.append({'img_url': img.href,
                              'title': 
                                  (e.title if e.has_key('title') else ''),
                              'entry_url': 
                                  (e.link if e.has_key('link') else '')})
                max_ = max_ -1
                
    # extract feed info
    f = parsed_feed.feed
    feed_meta = {'title':
                        (f.title if f.has_key('title') else ''),
                  'url':
                        (f.link if f.has_key('link') else '')}

    return { 'feed': feed_meta, 'images': media }
        