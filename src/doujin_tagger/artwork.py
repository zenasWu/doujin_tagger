import os
import re
import shutil
import logging
import traceback
from pathlib import Path

from doujin_tagger import spider
from doujin_tagger.id3 import ID3File, MP3File  # noqa
from doujin_tagger.mp4 import MP4File  # noqa
from doujin_tagger.util import dl_cover, find_inner_most
from doujin_tagger.xiph import *  # noqa
from doujin_tagger.audio import AudioFile
from doujin_tagger.image import EmbeddedImage

logger = logging.getLogger(__name__)

# \u30FB : Katakana Middle Dot
# \u301c : Wave Dash
# \uFF5E : Fullwidth Tilde (no problem)
# \u2600-\u26ff : Misc Sym
REFMT_REGISTRY = "|".join(AudioFile._registry)
AUDIO_PAT = re.compile(fr".*\.({REFMT_REGISTRY})$")
UNSUPPORT_PAT = re.compile(r".*\.(wav|ape)$")
NO_IMAGE_PAT = re.compile(r"no_img")
ILLEGAL_PAT = re.compile(r"[\\/:*?\"<>|\r\n\u30FB\u301c\u2600-\u26ff]+")


class MyLogger(logging.LoggerAdapter):
    '''add rjcode prompt in the front of logger message'''

    def process(self, msg, kwargs):
        return "<{0.rjcode}> {1!s}".format(self.extra["ref"], msg), kwargs


class ArtWork:
    """one logical album superset with many `AudioFile`s inside"""

    # register all spider functions in spider module
    spiders = {}
    for k, v in vars(spider).items():
        if k.startswith("spider") and callable(v):
            spiders[k] = v

    fields = {"album", "tags"}

    def __init__(self, rjcode, work_path, dest):
        self.rjcode = rjcode
        self.work_path = Path(work_path)
        self.dest = Path(dest)
        self.logger = MyLogger(logger, {"ref": self})
        self.audios = []  # AufioFile objs
        self.has_unsupport_fmt = False
        self._update_audios()
        # <doujin> tag is always set to "1" to distinguish with normal music
        self.info = {"doujin": "1"}

    def _update_audios(self):
        for root, _, files in os.walk(self.work_path):
            for eachfile in files:
                if UNSUPPORT_PAT.match(eachfile):
                    # private,DO NOT use it as a public member
                    self.has_unsupport_fmt = True
                    self.audios.clear()
                elif AUDIO_PAT.match(eachfile):
                    full_path = os.path.join(root, eachfile)
                    self.audios.append(AudioFile(full_path))

    def __len__(self):
        return len(self.audios)

    def _recur_del_and_move(self):
        # make sure this is the last thing to do
        # because we don't want to keep track of the filenames after moving
        dir_name = f"{self.rjcode} {self.info['album'][0]}"
        dir_name = ILLEGAL_PAT.sub("", dir_name)
        full_name = self.dest / dir_name
        path_to_move = find_inner_most(self.work_path)
        try:
            path_to_move.rename(full_name)
        except FileExistsError:
            self.logger.error("SAME DIR IN DEST FOUND!")
            return False
        # rescan and remove all empty dir
        if self.work_path.exists():
            if any(i for i in self.work_path.rglob("*") if i.is_file()):
                self.logger.error("FILES REMAINING")
                return False
            else:
                shutil.rmtree(self.work_path)
        return True

    def _check_field(self):
        """make sure rjcode and album are present to complete rename process"""
        return not (self.fields - self.info.keys())

    def fetch_and_feed(self, cover=True, lang=0):
        """give info fetched by spiders to each `AudioFile`"""

        # info's value must be a list
        langs = ["JP", "CN"]
        for k, func in self.spiders.items():
            self.logger.info(f"scraping [{k}] [{langs[lang]}]")
            self.info = func(self.rjcode, self.info, lang)
        for each in self.audios:
            each.feed(self.info)
        if cover:
            self.logger.info("getting cover")
            self._fetch_cover()

    def _fetch_cover(self):
        image_url = self.info.get("image_url")  # image_url: list
        if not image_url:
            self.logger.warning("IMAGE_URL ATTR NOT EXIST")
        elif NO_IMAGE_PAT.search(image_url[0]):
            self.logger.warning("WORK HAS NO COVER")
        else:
            bytesobj = dl_cover(image_url[0])
            if not bytesobj:
                # use -1 to flag dl_cover error
                # we must abort latter process
                return -1
            self.info["cover"] = bytesobj
        return 1

    def delete_all(self):
        """delete all files' tags in this album"""
        if self.has_unsupport_fmt:
            self.logger.error("HAS UNSUPPORT FMT, ABORT")
            return
        for each in self.audios:
            each.delete_all_tags()
        self.logger.info(f"[{len(self)}] files' info deleted")

    def save_all(self):
        """save infos to all files in this album and move to dest"""
        temp = {k: v for k, v in self.info.items() if k != 'cover'}
        self.logger.debug(f"self.info is {temp}")
        # if we ignore wav/ape... files and not abort,then files moving to dest
        # as if save_all works successfully
        # this files are totally not seen in foobar2k's database
        # with `%DOUJIN% PRESENT` filter on
        if self.has_unsupport_fmt:
            self.logger.error("UNSUPPORT FMT FOUND")
            return False
        if not self.audios:
            self.logger.error("AUDIOS NOT FOUND")
            return False
        if not self._check_field():
            self.logger.error("INFO NOT COMPLETE")
            return False

        coverobj = self.info.get("cover")
        if coverobj == -1:
            return False
        for each in self.audios:
            try:
                if coverobj:
                    img = EmbeddedImage(coverobj)
                    each.set_image(img)
                each.save()
            except Exception:
                self.logger.error("EXCEPTION WHEN SAVING, ABORT!")
                self.logger.debug(traceback.format_exc())
                break
        else:
            # if no error
            if self._recur_del_and_move():
                self.logger.info(f"Success! Saved [{len(self)}]")
                return True
        return False
