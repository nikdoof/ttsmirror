ttsmirror
=========

Copyright (c) Andrew Williams 2015

A quick tool to parse a Tabletop Simulator save file, mirror the required
elements locally, and produce an updated save file.

Due to the numerous takedowns of several popular game saves, its useful to
mirror any games you wish to play, while TTS itself actually caches the content
if for some reason the local cache gets invalidated then the game is no longer
playable. The solution is to build a mirror which you can host on a server
of your choice.

Usage
-----

    usage: ttsmirror.py [-h] save_file output_path url_prefix

```ttsmirror.py``` takes three arguments:

* ```save_file``` - the original TTS .json file.
* ```output_path``` - the directory you want the mirrored files to be sorted.
* ```url_prefix``` - the new prefix to add to any assets linked by HTTP/S (for example ```http://mywebsite.com/ttsmods/mod1/```).

License
-------

This project is licensed under the MIT license, see ```LICENSE``` file for more
information.
