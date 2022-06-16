
import argparse
import os
import sys

from src.swegram.version import VERSION

# part 1: pipeline 

# part 2: statistics

def pipeline(args):
    # import pdb
    # pdb.set_trace()
    print(args)
    ...



def statistics(args):
    ...

def _parse_arguments():

    parser = argparse.ArgumentParser(
        description="Swegram"
    )

    subparsers = parser.add_subparsers()

    pipeline_parser = subparsers.add_parser(
        'annotate',
        description='Pipeline parser'
    )
    pipeline_parser.set_defaults(func=pipeline)


    parser.add_argument(
        '-f',
        '--filename',
        dest='filename',
        help='The path to input file name'
    )

    parser.add_argument(
        '-d',
        '--input-dir',
        dest='input_dir',
        default=os.getcwd(),
        help='The path of input directory'
    )

    parser.add_argument(
        '-lang',
        '--language',
        dest='language',
        default='en',
        help='The language to be parsed. Choose "en" or "sv"'
    )
    
    parser.add_argument(
        '-o',
        '--output-filename',
        dest='output_filename',
        default='annotated',
        help='The output filename'
    )
    
    parser.add_argument(
        '-out-dir',
        '--output-directory',
        dest='output_directory',
        default=os.getcwd(),
        help='The output directory'
    )

    pipeline_parser.add_argument(
        '-nlp',
        '--annotations',
        dest='annotations',
        default='token spell tag parse'.split(),
        nargs='+',
        choices='token spell tag parse'.split(),
        help='Choose the annontation actions.'
             'Token, spell, tag, parse demonstrates tokenization, '
             'spelling checking, PoS tagging and syntactic parsing'
             'Tokenization is precondiation for PoS tagging and'
             ' PoS tagging is precondition for syntactic parsing.'
    )
    

    statistic_parser = subparsers.add_parser(
        'stats',
        description='Statistic parser'
    )
    # statistic_parser.set_defaults(func=statistic_parser)
    # statistic_parser.add_argument(
        
    # )
    
    return parser


def main():
    if len(sys.argv) < 2:
        sys.argv.append('--help')
    if sys.argv[1] == '--version':
        print(VERSION)
        sys.exit()
    parser = _parse_arguments()
    args = parser.parse_args(sys.argv[1:])
    
    args.func(args)

if __name__ == '__main__':
    main()
    

    