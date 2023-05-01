# Swegram

## Introduction

Swegram is a tool that offers the ability to annotate and analyse Swedish and English texts. You can upload one or more texts and have them linguistically analysed with morphological and syntactic features. These linguistically annotated texts can then be used to perform quantitative linguistic text analysis; for example, the tool provides statistics about sentence lengths, total number of words, various readability metrics, part-of-speech (PoS) distribution, as well as frequency of lemmas, PoS, or misspelled words. The tool also visualize the syntactic relations between words in sentences and give detailed information about the distribution of various syntactic functions and relations in the text.


## Setup ENVIRONMENT VARIABLES
```
source setup.sh
```


## Install swegram command line interface

Before installation, it is strongly recommended to use a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

Go to the root path where setup.py is located.

```console
pip install .
```

Check the usage of swegram cli
```console
(venv) ➜ swegram -h                                                               
usage: SWGRAM 1.0 [-h] -l {en,sv} -i INPUT_PATH [-o OUTPUT_DIR] [--output-format {txt,xlsx,json,csv}] {annotate,statistic} ...

Swegram command line interface description

positional arguments:
  {annotate,statistic}  Swegram subparser
    annotate            Annotation parser help
    statistic           Statistic parser help

optional arguments:
  -h, --help            show this help message and exit
  -l {en,sv}, --language {en,sv}
                        choose the language for annotation
  -i INPUT_PATH, --input-path INPUT_PATH
                        The input path to files/directory where working files are stored
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        The output directory where working files are stored
  --output-format {txt,xlsx,json,csv}
                        The output format
```


## Dependencies

* [udpipe](https://ufal.mff.cuni.cz/udpipe/1/install)

```
g++ 4.7 or newer, clang 3.2 or newer, Visual C++ 2015 or newer
make
SWIG 3.0.8 or newer for language bindings other than C++
```

* [efselab](https://github.com/robertostling/efselab)
* [pandoc](https://pandoc.org)

In order to build dependencies, run

```
./build_dependencies/install.sh
```


## to do

1. Compounds
2. Database
