import os
import logging
import json
import hashlib
from urllib.parse import urljoin
import requests

__version__ = '0.1'
__author__ = 'Andrew Williams'


class MirrorExceptionBase(Exception):
    """Base exception for all mirroring issues"""
    def __init__(self, msg):
        self.msg = msg

    def __unicode__(self):
        return self.msg

    def __str__(self):
        return self.__unicode__()


class MissingFileExecption(MirrorExceptionBase):
    """Raised when a source file is missing"""
    pass


class UnknownErrorException(MirrorExceptionBase):
    """Raised when an unknown issue is encountered when mirroring"""
    pass


def iterate_save(obj, output_path, url_prefix, hash_filename=False):
    """
    Iterate a save, download assets, and update the locations as needed.

    :param obj:
    :param output_path:
    :param url_prefix:
    :return:
    :rtype: dict
    """
    if isinstance(obj, dict):
        iter = obj.items()
    elif isinstance(obj, list):
        iter = enumerate(obj)

    for key, val in iter:
        if isinstance(val, dict) or isinstance(val, list):
            res = iterate_save(val, output_path, url_prefix, hash_filename)
            obj[key] = res
        if isinstance(val, str):
            if key.lower()[-3:] == 'url' and val.strip() != '':

                # If the Unique URL tag is added, remove it and ensure we set it later
                if '{Unique}' in val:
                    val = val.replace('{Unique}', '')
                    unique = True
                else:
                    unique = False

                # Generate new filename
                if hash_filename:
                    new_filename = hashlib.sha1(val.encode('utf-8')).hexdigest()
                else:
                    new_filename = val
                    for rep in [':', '/', '?', '=']:
                        new_filename = new_filename.replace(rep, '_')
                # Check if exists
                if not os.path.exists(os.path.join(output_path, new_filename)):
                    res = requests.get(val, stream=True)
                    if res.ok:
                        res.raw.decode_content = True
                        with open(os.path.join(output_path, new_filename), 'wb') as outfile:
                            for chunk in res:
                                outfile.write(chunk)
                    elif res.status_code == 404:
                        raise MissingFileExecption('%s returned a 404' % val)
                    else:
                        raise UnknownErrorException('URL %s returned code %d' % (val, res.status_code))
                if unique:
                    new_filename = new_filename + '{Unique}'
                obj[key] = urljoin(url_prefix, new_filename)
    return obj


def process_save(filename, output_path, url_prefix, hash_filename):
    """Parses TTS JSON save file and mirrors the required objects."""
    new_filename = '%s_new.json' % filename.replace('.', '_')
    with open(filename, 'r') as fobj:
        save = json.load(fobj)
    try:
        new_save = iterate_save(save, output_path, url_prefix, hash_filename)
    except Exception:
        logging.exception('Unable to process save')
        return
    new_save['SaveName'] = '%s - Mirrored' % new_save['SaveName']
    with open(new_filename, 'w') as outfobj:
        outfobj.write(json.dumps(new_save, sort_keys=True, indent=4, separators=(',', ': ')))
    logging.debug('Done, wrote %s', new_filename)


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser('ttsmirror.py')
    parser.add_argument('save_file')
    parser.add_argument('output_path', default=os.path.curdir)
    parser.add_argument('url_prefix')
    parser.add_argument('--hash_filename', action='store_true', dest='hash_filename')

    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()

    if not os.path.exists(os.path.abspath(args.save_file)):
        logging.error('Unknown file %s', args.save_file)
        sys.exit(1)

    process_save(args.save_file, args.output_path, args.url_prefix, args.hash_filename)


if __name__ == '__main__':
    main()
