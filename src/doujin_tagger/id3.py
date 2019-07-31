import logging

import mutagen
from mutagen.mp3 import MP3
from doujin_tagger.util import translate_errors
from doujin_tagger.audio import AudioFile
from doujin_tagger.image import COVER_FRONT

logger = logging.getLogger(__name__)


class ID3File(AudioFile, ext=None):
    IDS = {
        "TPE1": "artist",
        "TALB": "album",
        "TDRC": "date",
    }
    TXXX_MAP = {
        "DOUJIN": "doujin",
        "MAKER": 'maker',
        "NSFW": "nsfw",
        "TAGS": "tags"
    }

    SDI = {v: k for k, v in IDS.items()}
    PAM_XXXT = {v: k for k, v in TXXX_MAP.items()}

    Kind = MP3

    def __init__(self, filename):
        super().__init__(filename=filename)
        with translate_errors():
            audio = self.Kind(self["filename"])
        if audio.tags is None:
            audio.add_tags()
        self.audio = audio

    def save(self):
        for tagname, framename in self.SDI.items():
            if tagname not in self:
                continue
            FrameKind = mutagen.id3.Frames[framename]
            value = self.tolist(tagname)
            self.audio.tags.add(FrameKind(text=value, encoding=3))

        for key in self.PAM_XXXT:
            if key in self:
                value = self.tolist(key)
                file = mutagen.id3.TXXX(encoding=3,
                                        text=value,
                                        desc=self.PAM_XXXT[key])
                self.audio.tags.add(file)

        with translate_errors():
            self.audio.save()

    def set_image(self, image):
        # do not save
        with image:
            data = image.read()
            self.audio.tags.delall("APIC")
            frame = mutagen.id3.APIC(encoding=3,
                                     mime=image.mime_type,
                                     type=COVER_FRONT,
                                     desc="", data=data)
            self.audio.tags.add(frame)

    def delete_all_tags(self):
        # delete will call save, and image will be deleted
        self.audio.delete()


class MP3File(ID3File, ext=["mp3", "mp2", "mp1", "mpg", "mpeg"]):
    Kind = MP3
