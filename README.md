# Swegram

## Introduction

Swegram is a tool that offers the ability to annotate and analyse Swedish and English texts. You can upload one or more texts and have them linguistically analysed with morphological and syntactic features. These linguistically annotated texts can then be used to perform quantitative linguistic text analysis; for example, the tool provides statistics about sentence lengths, total number of words, various readability metrics, part-of-speech (PoS) distribution, as well as frequency of lemmas, PoS, or misspelled words. The tool also visualize the syntactic relations between words in sentences and give detailed information about the distribution of various syntactic functions and relations in the text.


## Setup ENVIRONMENT VARIABLES
```bash
export SWEGRAM_WORKSPACE=$(pwd)
```


## Install swegram command line interface

Before installation, it is strongly recommended to use a virtual environment
```bash
# Create virtual environment (Highly recommended)
python3 -m venv venv
source venv/bin/activate
# Install swegram package
pip install swegram --upgrade
# Build dependencies
swegram-build
# Export pythonpath
export PYTHONPATH="$PYTHONPATH:$(pwd):$(pwd)/tools/efselab"
```

Check the usage of swegram cli

* swegram -h

```console
usage: SWGRAM 1.0 [-h] -l {en,sv} -i INPUT_PATH [-o OUTPUT_DIR] [--output-format {txt,xlsx,json,csv}] {annotate,statistic} ...
Swegram command line interface description
positional arguments:
{annotate,statistic}  Swegram subparser
annotate              Annotation parser help
statistic             Statistic parser help
```

```
optional arguments:
-h, --help            show this help message and exit
-l {en,sv}, --language {en,sv}          choose the language for annotation
-i INPUT_PATH, --input-path INPUT_PATH  The input path to files/directory where working files are stored
-o OUTPUT_DIR, --output-dir OUTPUT_DIR  The output directory where working files are stored
--save-as {txt,xlsx,json}               The output format
```

swegram annotate -h
```
--normalize  Process spelling checker after tokenization and normalized tokens will be used for upcoming annotation actions.
--tokenize   Process sentence segmentation and tokenization.
--tag        Process part-of-speech tagging.
--parse      Process syntactic dependency parsing.
--aggregate  Aggregate all annotated texts into one file.
```

swegram statistic -h
```console
--include-metadata    Include certain texts by selecting metadata. For instance, "--include-metadata key1 key2:value2" only selects the texts that contain key1 or key2:value2 in the metadata
-- exclude-metadata   Exclude certain texts by deselecting metadata
-u --units            Checking statistics of features given certain linguistic unit(s). The following units are valid to be chosen: corpus, text, paragraph, sentence
--aspects             Checking statistics on the basis of selection of certain aspect(s). The following aspects are valid to be chosen: general, readability, morph, lexical, syntactic
--include-features    Only certain features will be included
--exclude-features    Certain features will be excluded
--print               Flag to print the result on console
```

## Run annotate and statistic actions with swegram

* For example, if you want to annotate one text file called "10-sv.txt" in the existing Resource folder named "resources/corpus/raw", the final conll file will be generated in a folder called output-folder, type the following command

```bash
swegram --language sv --input-path resources/corpus/raw/10-sv.txt --output-dir output-folder annotate
```

* If you have executed the command above and have the annotated file in the folder named output-folder, you can use the following command to analyze the annotated text(s) and get statistics.

```tips
Please remove all metafiles in the output folder, namely all files do not end up with ".conll".
rm output/*.tok output/*.tag output/*.txt
```

Now, type the following command:
```bash
swegram --language sv --input-path output statistic
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


## Run swegram desktop version

Tested with following requirements on ubuntu:20.04

* docker (Docker version 20.10.22)


Run desktop under the root of repository locally:
```bash
bash run.sh
```

## Run swegram with Docker Desktop on macOS

Preparation:

* Docker Desktop is installed. If not, please check [here](https://docs.docker.com/desktop/install/mac-install/) for installation. Only recent macOS versions are supported. It may be reuqired to update macOS. For our use case, please install according to the recommended setting.

* These ports are supposed to be available for Swegram desktop.

    * 80 (nginx proxy to serve frontend)
    * 8000 (fastapi app as backend to handle requests)
    * 3306 (mysql database)

* [Docker hub](https://hub.docker.com/) account

    This is used due to backend image is stored in docker hub.




You can follow the guideline below to start swegram desktop on your mac.

1. Generate static files to serve frontend pages:

```bash
cd frontend
docker build -t vue-builder -f Dockerfile.build .
docker run --rm -v $(pwd)/dist:/root/dist vue-bulder
```

2. Go to the repository root path, and run the following command to spin up the container

```bash
docker compose --profile client up -d
```

When the containers are up, go to the following [link](http://localhost/#/en)


```tips
1. It is not able to build the docker image locally on macOS due to limitation of udpipe binary. The image will be pulled from [docker hub](https://hub.docker.com/)

2. It takes a while before database is ready. Therefore, backend server will be up after 30 seconds sleep.

3. To exit swegram desktop. You can do

docker compose --profile client down
```
