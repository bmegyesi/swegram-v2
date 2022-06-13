"""
import text 
"""

import argparse

from import_text import create_text



def get_text(*args, **kwargs):
    return
    return create_text()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
      description="Pipeline to generate text anntation"
    )
    # create_text(lang, filename, label, eligible, checkNormalization, checkPOS, annotated=False)
    parser.add_argument('-lang', '--language', dest='lang', help='working language, only en and sv are available')
    parser.add_argument('-i', '--input-file', dest='input_file', help='incoming file path to be parsed')
    parser.add_argument('-o', '--ouput-file', dest='output_file', default='.', help='output file path')
    
    parser.add_argument('-pos', )
    
    args = parser.parse_args()
    
    # get_text(args)
  

    
    
