# Before installing efselab

It is not comptible with python 3.7|3.8. Tested with python 3.6. 

# How to run efselab

```
Usage: swe_pipeline.py --output-dir=DIR [options] FILENAME [...]

Options:
  -h, --help            show this help message and exit
  -o DIR, --output-dir=DIR
                        set target directory for output (Required.)
  --skip-tokenization   Assume tokenized input
  --skip-segmentation   Assume one sentence per line
  --tokenized           Generate tokenized output file(s) (*.tok)
  --tagged              Generate tagged output file(s) (*.tag)
  --lemmatized          Also lemmatize the tagged output file(s) (*.tag)
  --parsed              Generate parsed output file(s) (*.conll)
  --ner                 Generate named entity file(s) (*.ne)
  --all                 Equivalent to --tokenized --tagged --lemmatized --ner
                        --parsed
  --non-capitalized     The input is not properly capitalized (important for
                        sentence segmentation)
  -m FILENAME, --tagging-model=FILENAME
                        Model for PoS tagging
  -u FILENAME, --ud-tagging-model=FILENAME
                        Model for PoS tagging (UD wrapper)
  -l MODEL, --lemmatization-model=MODEL
                        MaltParser model file for parsing
  -n FILENAME, --ner-model=FILENAME
                        Model for named entity recognizer
  -p MODEL, --parsing-model=MODEL
                        MaltParser model file for parsing
  --malt=JAR            .jar file of MaltParser
  --no-delete           Don't delete temporary working directory.
```

## Tokenization


## 