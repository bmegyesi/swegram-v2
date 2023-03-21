# Swegram

## Introduction

Swegram is a tool that offers the ability to annotate and analyse Swedish and English texts. You can upload one or more texts and have them linguistically analysed with morphological and syntactic features. These linguistically annotated texts can then be used to perform quantitative linguistic text analysis; for example, the tool provides statistics about sentence lengths, total number of words, various readability metrics, part-of-speech (PoS) distribution, as well as frequency of lemmas, PoS, or misspelled words. The tool also visualize the syntactic relations between words in sentences and give detailed information about the distribution of various syntactic functions and relations in the text.


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

## Setup PYTHONPATH
```
export PYTHONPATH="$PYTHONPATH:$(pwd)"

#export EFSELABPATH in PYTHONPATH
EFSELABPATH=$REPO_PATH/tools/efselab
export PYTHONPATH="$PYTHONPATH:$(EFSELABPATH)"
```