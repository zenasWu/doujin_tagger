doujin_tagger
=============

|travis|

doujin_tagger 是一个同人音声音频的批量标签处理程序.

安装
=============
::
    
    git clone https://github.com/maybeRainH/doujin_tagger
    cd doujin_tagger
    python setup.py install

用法
======

-h, --help            显示帮助
--orig ORIG, -o ORIG  源文件夹
--dest DEST, -d DEST  处理好的文件需要移动过去的目标文件夹
--cov, -c             保存封面(默认)
--nocov, -q           不保存封面
--debug               单线程测试用
--show                显示保存在本地文件里的 ``orig`` 和 ``dest`` 配置
--lang LANG, -l LANG  0: 日语标签(默认), 1: 中文标签

第一次使用::

    doutag -o <文件夹> -d <文件夹> -q
    
再成功处理了一次以后,就可以省略 ``orig`` and ``dest``::

    doutag -q

``orig`` and ``dest`` 选项的设置会被保存在本地配置文件中.

为了覆盖本地文件配置,你必须同时再次提供 ``orig`` and ``dest`` 的配置选项.

现在,dlsite有中文翻译了,特别是标签,所以使用``--lang=1``来下载中文标签

如何工作
=============
1. 递归的匹配源文件夹里的符合 ``(?i)RJ\d+`` 的文件夹
#. 利用上一步匹配到的信息生成 ``Artwork`` 实例,并找出所有该文件夹下的匹配的音频文件
#. 从dlsite等网站上抓取标签的信息
#. 从信息里找到 ``image_url`` ,下载封面数据
#. 检查匹配的音频里是否为空,或者有不能处理的文件,如: Wav,Ape.
#. 保存抓取的标签和封面到每一个匹配的音频文件中
#. 将整个文件夹移到目标文件夹

注意
=========
* ``orig`` 和 ``dest`` **必须** 处于同一分区
* ``orig`` 和 ``dest`` **不能** 一个是另一个的子文件夹甚至同一文件夹
* **暂时不支持WAV文件**
* 保存封面 **可能** 很慢如果文件很大,使用 ``--nocov`` 来禁用保存封面的功能


.. |travis| image:: https://travis-ci.org/maybeRainH/doujin_tagger.svg?branch=master
    :target: https://travis-ci.org/maybeRainH/doujin_tagger