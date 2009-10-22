# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Small useful utils

"""

def is_empty(obj):
    """
    Is the object None, an empty string,
    a whitespace only string,
    or any countable object of length zero?
    
    """
    
    # None
    if obj is None:
        return True
    
    # String
    if isinstance(obj, basestring):
        return len(obj.strip())==0
    
    # all others
    try:
        return len(obj)==0
    except TypeError:
        # obj does not implement length
        return False
    
def is_not_empty(obj):
    """
    Opposite of is_empty
    
    """
    return not is_empty(obj)