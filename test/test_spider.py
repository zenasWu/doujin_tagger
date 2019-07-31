import os
from unittest.mock import Mock, patch

import pytest
import requests
from doujin_tagger.spider import spider_dlsite

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')

params = [
    ("RJ249851.html", {
        "artist": ["陽向葵ゅか", "篠守ゆきこ"],
        "album":["【バイノーラル】先輩とお姉さまにメスイキ調教されるあなた【百合 TS催眠】"],
        "nsfw":["18禁"],
        "date":["2019-04"],
        "maker":["ユビノタクト"],
        "image_url":["//img.dlsite.jp/modpub/images2/work/doujin/RJ250000/RJ249851_img_main.jpg"],  # noqa
        "tags":["バイノーラル/ダミヘ", "催眠音声", "女体化", "性転換(TS)", "百合", "レズ/女同士"],
    }),
    # no artist
    ("RJ202459.html", {
        'album': ['オナ指示、オナサポボイス10本セット(CV 如月なずな様10)'],
        'nsfw':["18禁"],
        'date':["2017-06"],
        'maker':['アイボイス'],
        'image_url':['//img.dlsite.jp/modpub/images2/work/doujin/RJ203000/RJ202459_img_main.jpg'],  # noqa
        'tags':['淫語', 'オナニー', '言葉責め', '逆レイプ', '童貞', '包茎']
    })
]


class TestDlsite:
    @pytest.mark.online
    def test_dlsite_404_online(self, caplog):
        spider_dlsite('RJ0')
        # set `log_level = INFO` in pytest.ini
        res = [record for record in caplog.records]
        assert len(res) == 1
        assert 'NotFound' in res[0].message

    @patch('requests.get')
    def test_dlsite_404(self, mock_req, caplog):
        resp = requests.Response()
        resp.status_code = 404
        mock_req.return_value = resp
        spider_dlsite('RJ0')
        res = [record for record in caplog.records]
        assert len(res) == 1
        assert 'NotFound' in res[0].message

    @patch('requests.get')
    def test_dlsite_timeout(self, mock_req, caplog):
        mock_req.side_effect = requests.Timeout('mock timeout')
        spider_dlsite(' RJ0')
        res = [record for record in caplog.records]
        assert len(res) == 4
        assert 'Maxtries' in res.pop().message

    # a lot of resp object made by offline html file
    @patch('requests.get')
    @pytest.mark.parametrize('name,expected', params)
    def test_dlsite_output(self, mock_req, name, expected):
        uri = os.path.join(DATA, name)
        with open(uri, 'rb') as f:
            content = f.read()
        resp = Mock()
        resp.status_code = 200
        resp.text = content
        mock_req.return_value = resp
        mock_req.text = 'haha'
        info = spider_dlsite('RJ0')
        assert info == expected
