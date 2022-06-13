
"""
prerequisites: pandoc
"""
import argparse
import logging
import json
import os
import re
import subprocess
import sys
import tempfile


SKIPPED_EXTENTIONS = ['txt', 'json']
SUPPORTED_EXTENTIONS = ['docx', 'odt', 'rtf', 'doc'] # doc and maybe more?

# Detect the file extention
# convert the file to json
# convert the file into organized strings

def get_dir(path):
    pattern = r'.+(?=/.+\.docx)'
    matched = re.match(pattern, path)
    if matched:
        return matched.group()
    else:
        return '.'
    

def convert(fpath):

    if not fpath:
        logging.error('No file path is provided')
        sys.exit()
    if not os.path.exists(fpath):
        logging.error('The provided path does not exist')
        sys.exit()
    format = fpath.split('.')[-1]
    if format not in SUPPORTED_EXTENTIONS:
        logging.error(f"'${format}' is not a supported extention")
        sys.exit()

    if format == 'doc':
        outfile = fpath + 'x'
        outdir = get_dir(outfile)
        subprocess.call(['soffice', '--headless', '--convert-to', 'docx', fpath, '--outdir', outdir])
        response = subprocess.run(["pandoc", "-f", "docx", "-t", "json", outfile], capture_output=True)
    else:
        response = subprocess.run(["pandoc", "-f", format, "-t", "json", outfile], capture_output=True)

    if response.stderr:
        logging.error(f'The file is not properly parsed: ${response.stderr}')
    else:
        return parse(json.loads(response.stdout))


def parse(content: dict):
    temp = tempfile.NamedTemporaryFile()
    
    def parse_help(content: any):
        if isinstance(content, dict):
            if content.get('t') == 'Para':
                temp.file.write(b'\n\n')
            if content.get('t') == 'Str':
                temp.file.write(content.get('c').encode())
            elif content.get('t') == 'Space':
                temp.file.write(b' ')
            else:
                if content.get('c'):
                    parse_help(content.get('c'))
        elif isinstance(content, list):
            for e in content:
                parse_help(e)
        temp.flush()
    
    parse_help(content.get('blocks'))
    with open(temp.name, mode='r', encoding='utf-8') as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(
        description="Text Conversion"
    )
    parser.add_argument('-f', required=True, dest='fpath', help='input file path')
    args = parser.parse_args()
    print(convert(args.fpath))


if __name__ == '__main__':
    main()
