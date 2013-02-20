'''
This file is part of the Python EJTP library.

The Python EJTP library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Python EJTP library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Python EJTP library.  If not, see 
<http://www.gnu.org/licenses/>.
'''

from ejtp.util.compat import unittest 
from ejtp.util.py2and3 import RawData, StringDecorator

from ejtp import frame

class TestRegistration(unittest.TestCase):
    def setUp(self):
        '''
        Stores all previously registered frame types
        '''
        self._old_frametypes = frame.registration._frametypes
        frame.registration._frametypes = {}

    def tearDown(self):
        '''
        Loads all previously stored frame types
        '''
        frame.registration._frametypes = self._old_frametypes

    def test_register_frame(self):
        self.assertRaises(TypeError, frame.RegisterFrame, 1234)
        self.assertRaises(ValueError, frame.RegisterFrame, 'ab')

        self.assertFalse(frame.registration._frametypes.get('x', False))

        @frame.RegisterFrame('x')
        class MyXFrame(frame.base.BaseFrame):
            pass
        
        self.assertEqual(frame.registration._frametypes[RawData('x')], MyXFrame)
        self.assertRaises(ValueError, frame.RegisterFrame, 'x')

        decorator = frame.RegisterFrame('y')
        class MyYFrame(frame.base.BaseFrame):
            pass
        decorator(MyYFrame)
        self.assertEqual(frame.registration._frametypes[RawData('y')], MyYFrame)
        decorator(MyXFrame)
        self.assertEqual(frame.registration._frametypes[RawData('y')], MyYFrame)

        def test_create_class():
            @frame.RegisterFrame('q')
            class NotAFrame(object):
                pass
        
        self.assertRaises(TypeError, test_create_class)
    
    def test_create_frame(self):
        @frame.RegisterFrame('a')
        class MyAFrame(frame.base.BaseFrame):
            pass
        
        f = frame.registration.createFrame('afoobar')
        self.assertTrue(isinstance(f, MyAFrame))
        self.assertRaises(ValueError, frame.registration.createFrame,  'qfoobar')
        self.assertRaises(TypeError, frame.registration.createFrame, 1234)

        
class TestBaseFrame(unittest.TestCase):
    def test_init(self):
        self.assertEqual(frame.base.BaseFrame('foobar')._content, RawData('foobar'))
        self.assertRaises(TypeError, frame.base.BaseFrame, 1234)
        ancestor = frame.base.BaseFrame('oldfoobar')
        self.assertEqual(frame.base.BaseFrame('foobar', [ancestor])._ancestors, [ancestor.crop()])
        self.assertRaises(TypeError, frame.base.BaseFrame, 'foobar', 123)
        self.assertRaises(TypeError, frame.base.BaseFrame, 'foobar', [object()])

    def test_eq(self):
        f1 = frame.base.BaseFrame('foo')
        f2 = frame.base.BaseFrame('bar', [f1])
        self.assertEqual(f1, frame.base.BaseFrame('foo'))
        self.assertEqual(f2, frame.base.BaseFrame('bar', [f1]))
        self.assertNotEqual(f2, frame.base.BaseFrame('bar'))
    
    def test_decode(self):
        self.assertRaises(NotImplementedError, frame.base.BaseFrame('foobar').decode)
    
    def test_unpack(self):
        class MyFrame(frame.base.BaseFrame):
            @StringDecorator(args=False, ret=True, strict=True)
            def decode(self, ident_cache = None):
                return self._content

        self.assertEqual(MyFrame('[1,2,3]').unpack(), [1,2,3])

        @frame.RegisterFrame('c')
        class MyFrame(frame.base.BaseFrame):
            def decode(self, ident_cache = None):
                return self._content
       
        f = MyFrame('cfoobar') 
        self.assertEqual(f.unpack(), MyFrame(f.content, [f.crop()]))

        class MyFrame(frame.base.BaseFrame):
            def decode(self, ident_cache = None):
                return object()
        
        self.assertRaises(TypeError, MyFrame('foobar').unpack)

    def test_crop(self):
        self.assertEqual(frame.base.BaseFrame('foobar').crop(), frame.base.BaseFrame('f\x00'))
        self.assertEqual(frame.base.BaseFrame('foobar\x00baz').crop(), frame.base.BaseFrame('foobar\x00'))
 
    def test_header_length(self):
        self.assertEqual(frame.base.BaseFrame('foobar').header_length, -1)
        self.assertEqual(frame.base.BaseFrame('foobar\x00baz').header_length, 5)
    
    def test_header(self):
        self.assertEqual(frame.base.BaseFrame('foobar').header, RawData())
        self.assertEqual(frame.base.BaseFrame('foobar\x00baz').header, RawData('oobar'))

    def test_body(self):
        self.assertEqual(frame.base.BaseFrame('foobar').body, RawData('oobar'))
        self.assertEqual(frame.base.BaseFrame('foobar\x00baz').body, RawData('baz'))
    
    def test_content(self):
        f = frame.base.BaseFrame('foobar')
        self.assertEqual(f.content, f._content)
    
    def test_last_category(self):
        class MyFrame(frame.base.BaseCategory, frame.base.BaseFrame):
            pass
        f1 = MyFrame('foo')
        f2 = MyFrame('bar', [f1])
        self.assertEqual(f2.last_category(frame.base.BaseCategory), f1.crop())
        self.assertRaises(TypeError, f2.last_category, object())
        class MyCategory(frame.base.BaseCategory):
            pass
        self.assertTrue(f2.last_category(MyCategory) is None)
 
