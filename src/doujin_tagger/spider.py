import logging

import requests
from lxml.etree import HTML
from doujin_tagger.util import process_info

logger = logging.getLogger(__name__)

JP_TRANSDICT = {
    "販売日": "date",
    "声優": "artist",
    "年齢指定": "nsfw",
    "ジャンル": "tags",
}

# [TODO] Dlsite now support Chinese.
CN_TRANSDICT = {
    "贩卖日": "date",
    "声优": "artist",
    "年龄指定": "nsfw",
    "分类": "tags",
}
TRANSDICTS = [JP_TRANSDICT, CN_TRANSDICT]
LANG = ["ja;q=1", "zh-CN,zh;q=1"]


def spider_dlsite(rjcode, info=None, lang=0):
    # lang: 0 for Japanese, 1 for Chinese
    dlsite_header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # noqa
    "Accept-Language": LANG[lang],
    "Cookies": "adultchecked=1",
    "User-Agent": ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/"
                   "537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/"
                   "537.36")
    }
    if info is None:
        info = {}
    url_fmt = 'https://www.dlsite.com/maniax/work/=/product_id/{}.html'
    url = url_fmt.format(rjcode)
    maxtries = 3
    while maxtries:
        try:
            res = requests.get(url, headers=dlsite_header, timeout=10)
            break
        except requests.Timeout:
            logger.error(f"<{rjcode}> Timeout, RETRING [{maxtries}]")
            maxtries -= 1
            continue
        except requests.ConnectionError as e:
            logger.error(repr(e) + f"<{rjcode}> RETRING [maxtries]")
            maxtries -= 1
            continue
    else:
        logger.error(f"<{rjcode}> Maxtries Reached")
        return info

    if res.status_code == 404:  # status_code's type is int, not str
        logger.error(f"<{rjcode}> NotFound On Dlsite")
        return info

    html = HTML(res.text)
    for each in html.xpath("//*[@id='work_outline']/descendant::tr"):
        info_name = each.xpath("th/text()")[0]
        info_attr = each.xpath("td/descendant::*/text()")
        if info_name in TRANSDICTS[lang]:
            info[TRANSDICTS[lang][info_name]] = info_attr
    info["maker"] = html.xpath("//*[@class='maker_name']/a/text()")
    info["album"] = html.xpath("//*[@id='work_name']/a/text()")
    info["image_url"] = html.xpath("//img[@itemprop='image']/@src")
    info = process_info(info)
    return info

# def spider_hvdb(rjcode, info=None, lang=0):
    # """hvdb spider you may want to implement

    # `info` is the fetch result of dlsite.
    # """
    # if info is None:
    #     info = {}
    # return info
