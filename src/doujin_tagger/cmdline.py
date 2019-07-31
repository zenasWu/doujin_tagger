import sys
from argparse import ArgumentParser

from doujin_tagger import __author__, __version__


def banner():
    print('''
  _____                    _______
 |  __ \                  |__   __|
 | |  | |   ___    _   _     | |      __ _    __ _
 | |  | |  / _ \  | | | |    | |     / _` |  / _` |
 | |__| | | (_) | | |_| |    | |    | (_| | | (_| |
 |_____/   \___/   \__,_|    |_|     \__,_|  \__, |
                                              __/ |
                                             |___/
                                       v%s by %s
''' % (__version__, __author__))


def cmd_parser():
    parser = ArgumentParser(description="a doujin voice tagger")
    parser.add_argument("--orig", "-o", type=str, dest="orig",
                        action="store", help="directory to process")
    parser.add_argument("--dest", "-d", type=str,
                        dest="dest", action="store", help="destination")
    parser.add_argument("--cov", "-c", action="store_true",
                        dest="cover", default=True, help="save cover(default)")
    parser.add_argument("--nocov", "-q", action="store_false",
                        dest="cover", help="do not save cover")
    parser.add_argument("--debug", action="store_true", dest="debug",
                        default=False, help="run in single thread for debug")
    parser.add_argument("--show", action="store_true", dest="show",
                        default=False, help="show orig & dest in config file")
    parser.add_argument("--lang", "-l", type=int, dest="lang", action="store",
                        default=0, help="0 for Japanese(default), 1 for Chinese")
    options = parser.parse_args(sys.argv[1:])
    return options
