import base64
import logging

from mutagen.flac import FLAC, Picture
from mutagen.oggflac import OggFLAC
from mutagen.oggopus import OggOpus
from mutagen.oggspeex import OggSpeex
from mutagen.oggtheora import OggTheora
from mutagen.oggvorbis import OggVorbis
from doujin_tagger.util import translate_errors
from doujin_tagger.audio import AudioFile
from doujin_tagger.image import COVER_FRONT

logger = logging.getLogger(__name__)

__all__ = ["OggFile", "OggFLACFile", "OggSpeexFile", "OggTheoraFile",
           "OggOpusFile", "FLACFile"]


class MutagenVCFile(AudioFile, ext=None):

    format = "Unknown Mutagen + vorbiscomment"
    MutagenType = None

    def __init__(self, filename):
        # must super to have *data*
        super().__init__(filename=filename)
        with translate_errors():
            self.audio = self.MutagenType(self["filename"])
        if self.audio.tags is None:
            self.audio.add_tags()

    def delete_all_tags(self):
        self.audio.delete()

    def clear_images(self):
        """Delete all embedded images"""

        # audio = self.MutagenType(self['filename'])
        self.audio.pop("metadata_block_picture", None)
        self.audio.pop("coverart", None)
        self.audio.pop("coverartmime", None)
        self.audio.save()

    def set_image(self, image):
        """Replaces all embedded images by the passed image"""

        with image:
            pic = Picture()
            pic.data = image.read()
            pic.type = COVER_FRONT
            pic.mime = image.mime_type
            pic.width = image.width
            pic.height = image.height

            self.audio.pop("coverart", None)
            self.audio.pop("coverartmime", None)
            self.audio["metadata_block_picture"] = base64.b64encode(
                pic.write()).decode("ascii")

    def save(self):
        for key in self.realkeys():
            self.audio.tags[key.lower()] = self.tolist(key)

        with translate_errors():
            self.audio.save()


class OggFile(MutagenVCFile, ext=["ogg", "oga"]):
    MutagenType = OggVorbis


class OggFLACFile(MutagenVCFile, ext="oggflac"):
    MutagenType = OggFLAC


class OggSpeexFile(MutagenVCFile, ext="spx"):
    MutagenType = OggSpeex


class OggTheoraFile(MutagenVCFile, ext="ogv"):
    MutagenType = OggTheora


class OggOpusFile(MutagenVCFile, ext="opus"):
    MutagenType = OggOpus


class FLACFile(MutagenVCFile, ext="flac"):
    MutagenType = FLAC

    def clear_images(self):
        """Delete all embedded images

        audio.delete can't delete images,so we need to overwrite
        delete_all_tags to call this method"""

        with translate_errors():
            self.audio.clear_pictures()
            self.audio.save()

        super().clear_images()

    def set_image(self, image):
        pic = Picture()
        pic.data = image.read()
        pic.type = COVER_FRONT
        pic.mime = image.mime_type
        pic.width = image.width
        pic.height = image.height
        # pic.depth = image.color_depth

        self.audio.add_picture(pic)
        with translate_errors():
            self.audio.save()
        # clear vcomment tags
        super().clear_images()

    def delete_all_tags(self):
        super().delete_all_tags()
        self.clear_images()
