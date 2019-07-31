doujin_tagger
=============

|travis|

`中文说明 <README.zh_cn.rst>`__

doujin_tagger is a doujin voice audio file tagger.

Installation
=============
::
    
    git clone https://github.com/maybeRainH/doujin_tagger
    cd doujin_tagger
    python setup.py install

Usage
======

-h, --help            show this help message and exit
--orig ORIG, -o ORIG  directory to process
--dest DEST, -d DEST  destination
--cov, -c             save cover(default)
--nocov, -q           do not save cover
--debug               run in single thread for debug
--show                show orig and dest saved in config file
--lang LANG, -l LANG  0 for Japanese(default), 1 for Chinese

For the first time, use::

    doutag -o <dir> -d <dir> -q
    
And next time you can ignore ``orig`` and ``dest``::

    doutag -q

The ``orig`` and ``dest`` config are saved in a json file.

To override the file settings, you must supply **both** ``orig`` and ``dest`` again

The dlsite tags now have Chinese translation version, So use ``--lang=1`` to download  Chinese tags

How It Works
=============
1. recursively match ``(?i)RJ\d+`` pattern in ``orig``.
#. make a ``Artwork`` instance and find out all ``audios`` under artwork's directory
#. fecth infomation from dlsite.
#. check whether ``image_url`` is in there, if so, download and store data in ``cover``.
#. check if ``audios`` is empty and has unsupport audio formats.
#. save metadata and cover into each audio in ``audios``.
#. move to ``dest``.

Attention
=========
* ``orig`` and ``dest`` **MUST** under the same mount point.
* ``orig`` and ``dest`` **MUST** NOT be the same or one is a subdirectory of other.
* **not support WAV** for now.
* Saving cover CAN be very slow if the file is very large. Use ``--nocov`` to disable.


.. |travis| image:: https://travis-ci.org/maybeRainH/doujin_tagger.svg?branch=master
    :target: https://travis-ci.org/maybeRainH/doujin_tagger   
