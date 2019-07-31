import os

import pytest
from doujin_tagger.id3 import ID3File, MP3File
from doujin_tagger.mp4 import MP4File
from doujin_tagger.xiph import FLACFile
from doujin_tagger.audio import DictMixin
from doujin_tagger.image import EmbeddedImage

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')
MP3_PATH = os.path.join(DATA, 'test.mp3')
MP4_PATH = os.path.join(DATA, 'mtest.m4a')
FLAC_PATH = os.path.join(DATA, 'ftest.flac')
OGG_PATH = os.path.join(DATA, 'otest.ogg')
COVER_PATH = os.path.join(DATA, 'cov.jpg')

info = {
    'album': ['Rain'], 'artist': ['miku', 'reimu'],
    'maker': ['ShangHai Alice'], 'nsfw': ['PG'],
    'tags': ['Jpop', 'Rock'],
    'image_url': ['E:/test/xxx.mp3'],
    'not exclude': ['woops'],
}

IDS = ID3File.IDS
TXXX_MAP = ID3File.TXXX_MAP


@pytest.fixture
def mp3():
    a = MP3File(MP3_PATH)
    # make sure it's empty
    a.delete_all_tags()
    it = [frame for frame in a.audio.tags.values() if frame.FrameID == "APIC"]
    assert len(it) == 0
    try:
        yield a
    finally:
        a.delete_all_tags()


@pytest.fixture
def mp4():
    a = MP4File(MP4_PATH)
    a.delete_all_tags()
    assert "covr" not in a.audio
    try:
        yield a
    finally:
        a.delete_all_tags()


@pytest.fixture
def flac():
    a = FLACFile(FLAC_PATH)
    a.delete_all_tags()
    try:
        yield a
    finally:
        a.delete_all_tags()


@pytest.fixture  # why can't use module scope
def cover():
    with open(COVER_PATH, 'rb') as f:
        with EmbeddedImage(f.read()) as em:
            yield em


def test_mp3_save(mp3):
    mp3.feed(info)
    mp3.save()
    a = MP3File(MP3_PATH)
    for k, v in a.audio.tags.items():
        if k in IDS:
            assert v.text == info[IDS[k]]
        elif k[5:] in TXXX_MAP:
            assert v.text == info[TXXX_MAP[k[5:]]]
        else:
            assert 0  # extra fields found


def test_mp3_set_image(mp3, cover):
    mp3.set_image(cover)
    mp3.save()
    a = MP3File(MP3_PATH)
    it = (frame for frame in a.audio.tags.values() if frame.FrameID == "APIC")
    one = next(it)
    assert len(one.data)


TRANSLATE = MP4File.translate


def test_mp4_save(mp4):
    mp4.feed(info)
    mp4.save()
    a = MP4File(MP4_PATH)
    for k, v in a.audio.items():
        if k in TRANSLATE:
            if k.startswith('----'):
                assert list(each.decode() for each in v) == info[TRANSLATE[k]]
            else:
                assert v == info[TRANSLATE[k]]
        else:
            assert 0


def test_mp4_set_image(mp4, cover):
    mp4.set_image(cover)
    mp4.save()
    a = MP4File(MP4_PATH)
    assert 'covr' in a.audio


def test_xiph_save(flac):
    flac.feed(info)
    flac.save()
    a = FLACFile(FLAC_PATH)
    d = DictMixin(a.audio.tags).list_repr()
    # make sure we didn't save what's in the `exclude`
    # also verify what's not in `exclude` will all be saved
    # when not feed, a is a dict of just one key('filename')
    # all info loaded from previous file's tag info is stored in a.audio.tags
    # Not to merge old info loaded from file with the info we feed
    # we just ignore and delete all old info previously stored in file
    assert 'filename' in a
    assert 'filename' not in a.audio.tags
    assert 'not exclude' in a.audio.tags
    temp = info.copy()
    temp.pop('image_url')
    assert temp == d


def test_xiph_set_image(flac, cover):
    flac.set_image(cover)
    flac.save()
    a = FLACFile(FLAC_PATH)
    assert a.audio.pictures
