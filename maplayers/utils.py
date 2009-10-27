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

def tfu_enc(in_str, session_id, nonce, max_len=None):
    """
    'Encoding' for TFU flash updater values
    
    """
    
    key='%s%s%s' % (session_id[:5],nonce, session_id)
    
    if max_len is not None:
        in_str = in_str[:max_len]

    # check if input is valid                                                                                                    
    if not (all(ord(c)<=127 for c in in_str) and \
            all(ord(c)<=127 for c in key)):
        return None

    code = []
    keylen=len(key)
    for i in range(len(in_str)):
        code.append(chr(ord(in_str[i]) + ord(key[i%keylen])))

    return ''.join(code).decode('iso-8859-1').encode('utf-8')

    
        