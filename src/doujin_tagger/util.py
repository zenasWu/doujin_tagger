import os
import re
import sys
import logging
import datetime
import contextlib
from pathlib import Path

import mutagen
import requests

from .audio import MutagenBug, AudioFileError

logger = logging.getLogger(__name__)

USER_AGENT = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36"
              "(KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")


@contextlib.contextmanager
def translate_errors():
    """Context manager for mutagen calls to load/save. Translates exceptions
    to local ones.
    """

    try:
        yield
    except AudioFileError:
        raise
    except mutagen.MutagenError as e:
        reraise(AudioFileError, e)
    except Exception as e:
        reraise(MutagenBug, e)


def dl_cover(url):
    headers = {
        "User-Agent": USER_AGENT,
        "Host": "img.dlsite.jp",
    }
    retry = 3
    while retry > 0:
        try:
            url = "https:" + url
            res = requests.get(url, timeout=10, headers=headers)
            res.raise_for_status()
            break
        except requests.RequestException as e:
            logger.warning(f"ERROR OCCUR! RETRYING! {e}")
            retry -= 1
            continue
    else:
        logger.error("REACH MAX RETRIES! DL Fail! ABORT!")
        return b""
    return res.content


def process_info(info):
    for key, val in info.items():
        if key == "date":
            val = val[0]
            try:
                date_tuple = re.search(r"(\d+)年(\d+)月(\d+)日", val).groups()
                fmt_date = datetime.datetime(*map(int, date_tuple))
                val = fmt_date.strftime("%Y-%m")
                info[key] = [val, ]
            except (AttributeError, TypeError):
                logger.warning("PROCESS DATE ERROR")
                info[key] = ["", ]
        elif key in ("tags", "artist"):
            new = []
            for each in val:
                temp = each.strip()
                each = each.replace("/", "").strip()
                if each:
                    new.append(temp)
            info[key] = new
        else:
            info[key] = val
    return info


def match_path(path, pat):
    """find dirs matched RJPAT under given path"""
    for root, dirs, _ in os.walk(path):
        matchobj = pat.search(root)
        if matchobj:
            rjcode = matchobj.group(1).upper()
            # stop searching deeper
            dirs.clear()
            yield (rjcode, root)


def find_inner_most(orig):
    '''find the most inner dirs that holds the data'''
    orig = Path(orig)
    while len(list(orig.iterdir())) == 1:
        orig = next(orig.iterdir())
        if not orig.is_dir():
            orig = orig.parent
            break
    return orig


def reraise(tp, value, tb=None):
    """Reraise an exception with a new exception type and
    the original stack trace
    """

    if tb is None:
        tb = sys.exc_info()[2]
    raise tp(value).with_traceback(tb)
