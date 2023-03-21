#!/bin/bash

# Download and install pandoc
python3 build_dependencies/install_pandoc.py

# Download and install udpipe
mkdir -p tools/udpipe
touch tools/__init__.py
cp -r build_dependencies/en/* tools/udpipe
chmod +x tools/udpipe/udpipe

# Download and install efselab
python3 build_dependencies/get_efselab.py

cp -r build_dependencies/sv/HistNorm tools

mv tools/efselab-master tools/efselab
cp build_dependencies/sv/swe-pipeline-ud2.tar.gz tools/efselab
cd tools/efselab

# Build lemmatizer
make

tar -xvzf swe-pipeline-ud2.tar.gz
python3 build_suc.py --skip-generate --python --n-train-fields 2
python3 build_suc_ne.py --skip-generate --python --n-train-fields 4

# Build and train the SUC-to-UD conversion model
python3 build_udt_suc_sv.py --python --beam-size 1 --n-train-fields 4
./udt_suc_sv train data/sv-ud-train.tab data/sv-ud-dev.tab swe-pipeline/suc-ud.bin

# Export efselab to the PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$(pwd)"
