from maplayers.constants import VIMEO_REGEX, YOUTUBE_REGEX, VIDEO_PROVIDER
import re

class VideoUrl(object):
    def __new__(cls, url):
        if re.compile(YOUTUBE_REGEX).match(url):
            return Youtube(url)
        elif re.compile(VIMEO_REGEX).match(url):
            return Vimeo(url)
        else:
            return NoVideo(url)


class Youtube(object):
    def __init__(self, url):
        self.url = url
        self.provider = VIDEO_PROVIDER.YOUTUBE
        self.is_valid = True 

    def video_id(self):
        return self._try_find_video_id_in_url()

    def _try_find_video_id_in_url(self):
        pattern = re.compile(YOUTUBE_REGEX)
        match = pattern.match(self.url)
        return match.group(1)


class Vimeo(object):
    def __init__(self, url):
        self.url = url
        self.provider = VIDEO_PROVIDER.VIMEO
        self.is_valid = True 

    def video_id(self):
        return self._try_find_video_id_in_url()

    def _try_find_video_id_in_url(self):
        pattern = re.compile(VIMEO_REGEX)
        match = pattern.match(self.url)
        return match.group(1)

class NoVideo(object):
    def __init__(self, url):
        self.url = url
        self.is_valid = False 
