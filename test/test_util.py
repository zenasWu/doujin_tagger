import os
import re
import logging

import pytest
from doujin_tagger.util import (dl_cover, match_path, process_info,
                                find_inner_most)

logging.basicConfig(level=logging.DEBUG)


def test_match_path(dir):
    rjpat = re.compile(r"(RJ\d+)", flags=re.IGNORECASE)
    rj23_path = os.path.join(dir.path, 'music', 'RJ23232')
    rj45_path = os.path.join(dir.path, 'music', 'sub', 'RJ45454')
    rj67_path = os.path.join(dir.path, 'music', 'RJ67676')
    res = [('RJ23232', rj23_path), ('RJ45454',
                                    rj45_path), ('RJ67676', rj67_path)]
    for i in res:
        assert i in list(match_path(dir.path, rjpat))


info_date = {'date': ['2019年1月1日']}
info_tags = {'tags': ['school', ' / ', 'ear cleaning  ',
                      ' \n /', ' / \n /', 'pure/love'], }


def test_process_info():
    after_date = process_info(info_date)
    assert after_date == {'date': ['2019-01']}
    after_tags = process_info(info_tags)
    assert after_tags == {'tags': ['school', 'ear cleaning', 'pure/love']}


def test_find_inner_most(dir):
    rj23_path = os.path.join(dir.path, 'music', 'RJ23232')
    rj45_path = os.path.join(dir.path, 'music', 'sub', 'RJ45454')
    rj10_path = os.path.join(dir.path, 'music', 'RJ67676')
    assert rj23_path == str(find_inner_most(rj23_path))
    assert os.path.join(rj45_path, 'title') == str(find_inner_most(rj45_path))
    assert rj10_path == str(find_inner_most(rj10_path))


@pytest.mark.online
def test_dl_cover():
    res = dl_cover(
        "//img.dlsite.jp/modpub/images2/work/doujin/RJ203000/RJ202459_img_main.jpg")  # noqa
    assert res
    assert len(res) != 0
