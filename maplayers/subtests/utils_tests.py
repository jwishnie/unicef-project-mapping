# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

'''
Created on Oct 22, 2009

@author: jwishnie
'''
import unittest
from utils import *

class UtilsTest(unittest.TestCase):
    empty_list = [
                  '',
                  '\t',
                  '\n'
                  '\r',
                  '   \n \r \t   ',
                  u'',
                  u'\t',
                  u'\n'
                  u'\r',
                  u'   \n \r \t   ',
                  None,
                  {},
                  [],
                  ()
                ]
    
    not_empty_list = [
                        'a',
                        '  a',
                        'a  ',
                        '  a  ',
                        u'a',
                        u'  a',
                        u'a  ',
                        u'  a  ', 
                        [1],
                        [''],
                        {1:1},
                        {1:''},
                        1
                     ]
    
    def testEmpty(self):
        self.assertTrue(all(is_empty(obj) for obj in self.empty_list))

        for obj in self.not_empty_list:
            self.assertFalse(is_empty(obj))
                             
    def testNotEmpty(self):
        self.assertFalse(all(is_not_empty(obj) for obj in self.empty_list))

        for obj in self.not_empty_list:
            self.assertTrue(is_not_empty(obj))

if __name__=='__main__':
    unittest.main()