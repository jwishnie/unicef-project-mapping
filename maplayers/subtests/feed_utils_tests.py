# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

'''
Created on Oct 22, 2009

@author: jwishnie
'''
import unittest
from maplayers import feed_utils

FRMT = feed_utils.FLICKR_FEED_FORMAT

class FeedUtilsTest(unittest.TestCase):
    urlList = [
               ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=atom',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss_200_enc',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss_200',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?',
                'http://api.flickr.com/services/feeds/photoset.gne?'+FRMT),                
                ('feed://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss_200',
                 'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://www.nytimes.com/',
                'http://www.nytimes.com/'),
                ('Asdadaadfasdfn q3214 124 s,f asdf sdf a',
                 'Asdadaadfasdfn q3214 124 s,f asdf sdf a'),
              ]
    
    def testCleanURL(self):
        for src, expected in self.urlList:
            result = feed_utils.clean_feed_url(src)
            if result != expected:
                print "\nFAILURE\nsrc:\t  %s\nexpected: %s\nreceived: %s" % \
                    (src, expected, result)
                self.assertFalse(True)
    
if __name__=='__main__':
    unittest.main() 
