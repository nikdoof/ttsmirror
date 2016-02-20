import os
import logging
import requests
from urllib.parse import urlparse, urljoin
import json

__version__ = '0.1'
__author__ = 'Andrew Williams'


def iterate_save(obj, output_path, url_prefix):
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
            res = iterate_save(val, output_path, url_prefix)
            obj[key] = res
        if isinstance(val, str):
            parsed = urlparse(val)
            if parsed.scheme and parsed.scheme in ['http', 'https', 'ftp']:
                # Generate new filename
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
                    if res.status_code == 404:
                        raise Exception
                obj[key] = urljoin(url_prefix, new_filename)
    return obj


def process_save(filename, output_path, url_prefix):
    """Parses TTS JSON save file and mirrors the required objects."""
    new_filename = '%s_new.json' % filename.replace('.', '_')
    with open(filename, 'r') as fobj:
        save = json.load(fobj)
    try:
        new_save = iterate_save(save, output_path, url_prefix)
    except Exception as e:
        logging.exception('Unable to process save: %s' % e)
    new_save['SaveName'] = '%s - Mirrored' % new_save['SaveName']
    with open(new_filename, 'w') as outfobj:
        outfobj.write(json.dumps(new_save))
    logging.debug('Done, wrote %s', new_filename)


def main():
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser('ttsmirror.py')
    parser.add_argument('save_file')
    parser.add_argument('output_path', default=os.path.curdir)
    parser.add_argument('url_prefix')

    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()

    if not os.path.exists(os.path.abspath(args.save_file)):
        logging.error('Unknown file %s' % args.save_file)
        sys.exit(1)

    process_save(args.save_file, args.output_path, args.url_prefix)


if __name__ == '__main__':
    main()
