# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Utilities for dealing with RSS Feeds

"""
from __future__ import with_statement

import urlparse
import re
import feedparser
from django.core.cache import cache
from maplayers.utils import is_empty
import simplejson as json   
import urllib2


IMAGE_TYPES = [
               'image/jpeg',
               'image/pjpeg',
               'image/gif',
               'image/png',
               ]

VIDEO_TYPES = [
               'application/x-shockwave-flash',
               'video/3gpp',
               ]

YOUTUBE_EMBED_TYPE = VIDEO_TYPES[0]

FLICKR_FEED_FORMAT = 'format=atom'

FLICKR_MEDIUM_IMAGE_PATTERN = re.compile(".*src=([^\s]+).*")



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
    

def parse_feed(url):
    if is_empty(url):
        return None
    
    # fix url for use by feedparser
    clean_url = clean_feed_url(url)
        
    # see if it's a file url, 'cause parse feeder doesn't handle them
    # correctly
    is_file_url = clean_url.lower().startswith('file://')
                        
    # Try to retrieve from cache using cleaned url. 
    # In case of file url, don't bother with the cache, just re-read
    # each time
    parsed_feed = (None if is_file_url else cache.get(clean_url))
    
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
        # no cached one, go get it, handling files for
        # dumb ass feedparser
        to_parse = clean_url
        if is_file_url:
            with open(clean_url[7:]) as f:
                to_parse = f.read()
                
        parsed_feed = feedparser.parse(to_parse)
        if len(parsed_feed.feed) > 0:
            cache.set(clean_url, parsed_feed)
        elif cache.has_key(clean_url):
            del cache[clean_url]
            
    return parsed_feed
    

def parse_img_feed(url, max_entries=None):  

    parsed_feed=parse_feed(url)
    if parsed_feed is None:
        return []
          
    # extract media info
    max_ = (int(max_entries) \
            if max_entries is not None else -1)

    media = []
    for e in parsed_feed.entries:
        if max_ == 0:
            break
        
        if url.__contains__("flickr"):
            max_ = _get_flickr_medium_image(e.content, media, max_)
        else:
            max_ = _get_picasa_medium_image(e.media_thumbnail, media, max_)

         
    # extract feed info
    f = parsed_feed.feed
    feed_meta = {'title':
                        (f.title if f.has_key('title') else ''),
                  'url':
                        (f.link if f.has_key('link') else '')}
    return { 'feed': feed_meta, 'images': media }
    
    
def _get_flickr_medium_image(items, media, _max):
    for item in items:
        content = item.value.replace("\n", "")
        medium_image_url = FLICKR_MEDIUM_IMAGE_PATTERN.match(content).group(1)
        media.append({"img_url" : medium_image_url})
        _max = _max -1
    return _max
        
        
def _get_picasa_medium_image(items, media, _max):
    url = items[1]['url']
    media.append({"img_url" : url})
    return _max - 1
        