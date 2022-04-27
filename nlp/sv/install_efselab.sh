#!/bin/sh

if [ ! -e swe-pipeline-ud2.tar.gz ]; then
    echo 'Lack of swedish pipeline'
    exit 1
fi

# Intialize virtual environemnt (temporarily setting)
python3.6 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Git clone efselab repo
git clone git@github.com:robertostling/efselab.git

cp swe-pipeline-ud2.tar.gz efselab/
cd ./efselab/

# Build lemmatizer
make

# Build models
tar xvzf swe-pipeline-ud2.tar.gz
python3.6 build_suc.py --skip-generate --python --n-train-fields 2
python3.6 build_suc_ne.py --skip-generate --python --n-train-fields 4

# Build and train the SUC-to-UD conversion model
python3.6 build_udt_suc_sv.py --python --beam-size 1 --n-train-fields 4
./udt_suc_sv train \
    data/sv-ud-train.tab data/sv-ud-dev.tab swe-pipeline/suc-ud.bin
