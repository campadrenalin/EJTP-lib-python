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

def is_string(value):
    '''
    Checks, if value is a string. In python 2.x it checks if value is an
    instance of basestring. In python 3.x it checks if it is an instance of
    str or bytes, since all strings in python 3 derivate from str rather than
    basestring and bytes isn't a subclass of str anymore.

    '''

    if isinstance(value, str):
        return True
    if bytes == str:
        # In python 2.x bytes is equal with str, in python 3.x not.
        return isinstance(value, basestring)
    return isinstance(value, bytes)

def get_unicode():
    '''
    Returns an unicode class. In python 2.x thats unicode but in python 3.x
    there is no uncode class anymore, because str itself is unicode.
    '''

    if bytes == str:
        return unicode
    return str

class RawData(object):
    '''
    This class is supposed to store raw data and behaves similar to str in
    python 2.x and bytes in python 3.x
    '''
    def __init__(self, value=()):
        '''
        Takes an iterable value that should contain either integers in range(256)
        or corresponding characters.

        >>> repr(RawData((1, 2, 3))) == 'RawData(010203)'
        True
        >>> repr(RawData('abc')) == 'RawData(616263)'
        True
        >>> repr(RawData(String('abc'))) == 'RawData(616263)'
        True
        '''
        if isinstance(value, int):
            value = (value,)
        try:
            iter(value)
        except TypeError:
            raise TypeError('value must be iterable')
        if isinstance(value, bytes):
            # this makes sure that iterating over value gives one byte at a time
            # in python 2 and 3
            if bytes == str:
                # in python 2 iterating over bytes gives characters instead of integers
                value = (ord(c) for c in value)
            value = tuple(value)
        elif isinstance(value, str) or (bytes==str and isinstance(value, unicode)):
            # only unicode strings will get here
            value = tuple(value.encode('utf-8'))
        elif isinstance(value, String):
            value = value.toRawData()._data
        else:
            # maybe a list of ints?
            try:
                value = tuple((int(i) for i in value))
            except ValueError:
                raise ValueError('values must be ints')

            for i in value:
                if i < 0 or i > 255:
                    raise ValueError('values not in range(256)')

        self._data = value

    def __eq__(self, other):
        '''
        >>> RawData('abc') == RawData((97, 98, 99))
        True
        >>> RawData('abc') == 'abc'
        False
        '''
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return NotImplemented

    def __add__(self, other):
        '''
        >>> RawData('ab') + RawData('c') == RawData('ab') + 99 == RawData('abc')
        True
        >>> RawData('ab') + object() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TypeError: unsupported operand type(s) for +: 'RawData' and 'object'
        '''
        if not isinstance(other, self.__class__):        
            try:
                other = self.__class__(other)
            except (TypeError, ValueError):
                return NotImplemented
        return self.__class__(self._data.__add__(other._data))
    
    def __len__(self):
        '''
        >>> len(RawData('ab')) == 2
        True
        '''
        return self._data.__len__()

    def __getitem__(self, key):
        '''
        >>> RawData('ab')[1] == RawData('b')
        True
        '''
        return self.__class__(self._data.__getitem__(key))

    def __iter__(self):
        '''
        >>> for c in RawData('abc'):
        ...     print(c)
        ...
        97
        98
        99
        '''
        return self._data.__iter__()

    def __repr__(self):
        '''
        >>> repr(RawData('abc')) == 'RawData(616263)'
        True
        '''
        return 'RawData(' + str().join([format(c, '02x') for c in self._data]) + ')'
    
    def toString(self):
        '''
        >>> RawData('abc').toString() == String('abc')
        True
        '''
        if bytes == str:
            return String(bytes().join(chr(c) for c in self._data).decode('utf-8'))
        return String(bytes(self._data).decode('utf-8'))

class String(object):
    '''
    This class stores unicode strings and treats them depending on the python
    version.
    '''
    def __init__(self, string):
        '''
        Takes an string or RawData and converts it to unicode.
        '''

        if isinstance(string, RawData):
            string = string.toString()._data
        if isinstance(string, bytes):
            string = RawData(string).toString()._data
        elif (bytes == str):
            # python2 only here
            if not isinstance(string, unicode):
                raise TypeError('string must be of type str, unicode or RawData')
        elif not isinstance(string, str):
            # python3 only here
            raise TypeError('string must be of type bytes, str or RawData')
        self._data = string

    def __eq__(self, other):
        '''
        >>> String('abc') == String(RawData((97, 98, 99)))
        True
        >>> String('abc') == 'abc'
        False
        '''
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return NotImplemented

    def __add__(self, other):
        '''
        >>> String('a') + String('b') == String('ab')
        True
        >>> String('a') + 'b' == String('ab')
        True
        >>> String('a') + RawData(98) == String('ab')
        True
        >>> String('abc') + object() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TypeError: unsupported operand type(s) for +: 'RawData' and 'object'
        '''
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except TypeError:
                return NotImplemented
        return self.__class__(self._data.__add__(other._data))

    def __len__(self):
        '''
        >>> len(String('abc')) == 3
        True
        '''
        return self._data.__len__()
    
    def __getitem__(self, key):
        '''
        >>> String('abc')[1] == String('b')
        True
        '''
        return self.__class__(self._data.__getitem__(key))
    
    def __iter__(self):
        '''
        >>> val = True
        >>> for c in String('aaa'):
        ...     val &= (c == 'a')
        ...
        >>> val
        True
        '''
        # in python2 unicode somehow only iterates with iter()
        if hasattr(self._data, '__iter__'):
            return self._data.__iter__()
        return iter(self._data)
    
    def __repr__(self):
        '''
        >>> repr(String('abc')) == "String('abc')"
        True
        '''
        rep = self._data.__repr__()
        if rep[0] == 'u':
            # in python2 for unicode
            rep = rep[1:]
        return 'String(' + rep + ')'

    def toRawData(self):
        '''
        >>> String('abc').toRawData() == RawData('abc')
        True
        '''
        return RawData(self._data.encode('utf-8'))
