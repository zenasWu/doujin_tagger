import pytest
from doujin_tagger.audio import DictMixin


class Foo(DictMixin):
    pass


class TestDictMixin:
    @pytest.fixture(autouse=True, scope='function')
    def setup(self):
        self.f1 = Foo({'a': 1, 'b': 2}, a='3')

    def test_init(self):
        with pytest.raises(TypeError):
            f = Foo({'a': 1}, {'b': 2})  # noqa
        f1 = Foo({'a': 1, 'b': 2}, filename='3', rjcode='RJ0')
        f2 = Foo(filename='test', rjcode='RJ0')
        assert dict(f1) == {'a': '1', 'b': '2',
                            'rjcode': 'RJ0', 'filename': '3'}
        assert dict(f2) == {'filename': 'test', 'rjcode': 'RJ0'}

    def test_setitem(self):
        assert self.f1['a'] == '1\n3'

    def test_add(self):
        self.f1.add('b', 'add1')
        self.f1.add('b', 'add2')
        assert self.f1['b'] == '2\nadd1\nadd2'

    def test_remove(self):
        # invalid value
        self.f1.remove('a', 1)
        assert dict(self.f1) == {'a': '1\n3', 'b': '2'}
        # invalid key
        self.f1.remove('invalid', '1')
        assert dict(self.f1) == {'a': '1\n3', 'b': '2'}
        # normal remove
        self.f1.remove('a', '1')
        assert dict(self.f1) == {'a': '3', 'b': '2'}
        # remove all
        f = Foo(filename=[1, 2], doujin=1)
        f.remove('filename')
        assert 'filename' not in f
        f = Foo(filename=[1, 2], doujin=1)
        f.remove('filename', '1\n2')
        assert 'filename' not in f
        # you can delete by list of str
        f = Foo(filename=[1, 2], doujin=1)
        f.remove('filename', ['1', '2'])
        assert 'filename' not in f
        # but not by list of int
        f = Foo(filename=[1, 2], doujin=1)
        f.remove('filename', [1, 2])
        assert f['filename'] == '1\n2'

    def test_tolist(self):
        self.f1.add('a', 'tolist')
        assert self.f1.tolist('a') == ['1', '3', 'tolist']
        assert self.f1.tolist('invalid') == []
        empty_f = Foo(a='')
        assert empty_f.tolist('') == []
        f2 = Foo(a='')
        f2.add('a', '1')
        assert f2.tolist('a') == ['1']

    def test_missing_contains(self):
        f = Foo(a=1)
        assert f['b'] == ''
        assert 'b' not in f
        # test .get() works pass __getitem__
        assert 'haha' == f.get('b', 'haha')

    def test_list_repr(self):
        assert self.f1.list_repr() == {'a': ['1', '3'], 'b': ['2']}

# some weird things happened


class TestAudioFile:
    # AudioFile._registry.clear()
    # class ID3(AudioFile, ext=None):pass
    # class MP3(ID3, ext=['.mp3', '.mpeg2']): pass
    # class MP4(AudioFile, ext='.m4a'): pass
    # # hack into Custom class above ,invoke DictMixin's __init__
    # def init(self, filename):
        # DictMixin.__init__(self, filename=filename)
    # ID3.__init__ = init
    # MP4.__init__ = init

    def test_registry(self, prep):
        assert prep['AudioFile']._registry == {'.mp3': prep['MP3'],
                                               '.m4a': prep['MP4'],
                                               '.mpeg2': prep['MP3']}

    def test_factory(self, prep):
        # Testclass ID3 has no __init__ to invoke DictMixin's __init__,
        # we pass a dict instead to prevent DictMixin raising a excetion
        a = prep['AudioFile']('E:/test/test.mp3')
        assert isinstance(a, prep['MP3'])
        a = prep['AudioFile']('E:/test/test.mpeg2')
        assert isinstance(a, prep['MP3'])
        # with pytest.raises(NoMatchError):
        #     a = AudioFile('E:/test/test.invalid')
