import pytest
from testfixtures import TempDirectory
from doujin_tagger.audio import AudioFile, DictMixin

# dir:
# music/
#     RJ23232/
#         test.mp3
#     sub/
#         RJ45454/
#             title/
#                 test2.mp3
#     RJ67676/
#         title/
#             test3.mp3
#         another/
#             test4.mp4


@pytest.fixture(scope='module')
def dir():
    with TempDirectory() as dir:
        dir.write('music/RJ23232/test.mp3', b'this is test.mp3 file')
        dir.write('music/sub/RJ45454/title/test2.mp3', b'this is test2.mp3')
        dir.write('music/RJ67676/title/test3.mp3', b'this is test3.mp3')
        dir.write('music/RJ67676/another/test4.mp3', b'this is test4.mp3')
        yield dir


# we can't do this in test_audio.py bacause of the weird
# class and file execution order of pytest
@pytest.fixture(scope='session')
def prep():
    # test_concrete.py will register everything,so we clear it before
    AudioFile._registry.clear()

    class ID3(AudioFile, ext=None):
        pass

    class MP3(ID3, ext=['.mp3', '.mpeg2']):
        pass

    class MP4(AudioFile, ext='.m4a'):
        pass

    # hack into Custom class above ,invoke DictMixin's __init__
    def init(self, filename):
        DictMixin.__init__(self, filename=filename)
    ID3.__init__ = init
    MP4.__init__ = init
    yield {'AudioFile': AudioFile, 'MP3': MP3, 'MP4': MP4}
