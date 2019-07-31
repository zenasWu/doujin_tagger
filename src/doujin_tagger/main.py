import re
import json
import logging
from os import path
from multiprocessing import Pool, freeze_support

from doujin_tagger.util import match_path
from doujin_tagger.artwork import ArtWork
from doujin_tagger.cmdline import banner, cmd_parser

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
filelog = logging.FileHandler(
    path.expanduser("~/dt_info.txt"), encoding="utf-8")
filelog.setLevel(logging.DEBUG)
fileformatter = logging.Formatter(
    "%(asctime)s %(name)-8s %(funcName)-13s| %(levelname)-8s | %(message)s",
    datefmt="[%Y-%m-%d %H:%M]")
filelog.setFormatter(fileformatter)
ch = logging.StreamHandler()
chformatter = logging.Formatter(
    "%(name)-8s %(funcName)-16s| %(levelname)-8s | %(message)s")
ch.setFormatter(chformatter)
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.addHandler(filelog)

RJPAT = re.compile(r"(RJ\d+)", flags=re.IGNORECASE)
PATH = path.expanduser("~/doutag.json")


def read_config():
    try:
        with open(PATH, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    return config


def save_config(config):
    with open(PATH, "w") as f:
        json.dump(config, f)


def show_config(config):
    logger.info(f"orig = {config.get('orig','no value')}")
    logger.info(f"dest = {config.get('dest','no value')}")


def merge_config(options, config):
    if not options.dest or not options.orig:
        logger.info("no orig or dest supplied, reading from file")
        config = read_config()
        if not config:
            logger.info("no config found,please supply by cmdline")
            return None, None, -1
        else:
            show_config(config)
            orig = config["orig"]
            dest = config["dest"]
            return orig, dest, 0
    else:
        orig = options.orig
        dest = options.dest
        return orig, dest, 1


def worker(args):
    rjcode, root, dest, cover, lang = args
    a = ArtWork(rjcode, root, dest)
    a.fetch_and_feed(cover, lang)
    a.save_all()


def main():
    banner()
    options = cmd_parser()
    config = read_config()
    if options.show:
        show_config(config)
        return
    orig, dest, reflush = merge_config(options, config)
    if reflush == -1:
        return
    if not path.exists(orig) or not path.exists(dest):
        logger.error("orig or dest does not exist")
        return
    # for file rename, we must have both on the same mount point.
    # XXX not tested on *nix if two on different mount point
    if path.splitdrive(orig)[0] != path.splitdrive(dest)[0]:
        logger.error("orig and dest not in the same drive")
        return
    logger.info("starting")
    cover, lang = options.cover, options.lang
    work_list = [(rjcode, root, dest, cover, lang)
                 for rjcode, root in match_path(orig, RJPAT)]
    if not work_list:
        logger.info("no match found")
        return
    if options.debug:
        for args in work_list:
            worker(args)
    else:
        with Pool() as pool:
            pool.map(worker, work_list)
    if reflush == 1:
        config = {"dest": dest, "orig": orig}
        logger.info("saving config to file")
        save_config(config)


if __name__ == '__main__':
    freeze_support()
    main()
