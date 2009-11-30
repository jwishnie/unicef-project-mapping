# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from maplayers import utils

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
        self.assertTrue(all(utils.is_empty(obj) for obj in self.empty_list))

        for obj in self.not_empty_list:
            self.assertFalse(utils.is_empty(obj))
                             
    def testNotEmpty(self):
        self.assertFalse(all(utils.is_not_empty(obj) for obj in self.empty_list))

        for obj in self.not_empty_list:
            self.assertTrue(utils.is_not_empty(obj))

    def testEscapeStringsWithDoubleQuotes(self):
        self.assertTrue(utils.html_escape('This is a "test"'), "This is a &quot;test&quot;")

    def testEscapeStringWithSingleQuote(self):
        self.assertTrue(utils.html_escape("""This "is" a 'test'"""), "This &quot;is&quot; a &apos;test&apos;")

if __name__=='__main__':
    unittest.main() 
