#!/bin/bash

set -x

if [ -z ${SWEGRAM_WORKSPACE} ]; then
    SWEGRAM_WORKSPACE=$(pwd)
fi

echo $SWEGRAM_WORKSPACE

# Download and install pandoc
python3 $SWEGRAM_WORKSPACE/build_dependencies/install_pandoc.py

# Download and make udpipe
python3 $SWEGRAM_WORKSPACE/build_dependencies/install_udpipe.py

mkdir -p $SWEGRAM_WORKSPACE/tools/udpipe
touch $SWEGRAM_WORKSPACE/tools/__init__.py
cp -r $SWEGRAM_WORKSPACE/build_dependencies/en/* $SWEGRAM_WORKSPACE/tools/udpipe
chmod +x $SWEGRAM_WORKSPACE/tools/udpipe/udpipe

# Download and install efselab
python3 $SWEGRAM_WORKSPACE/build_dependencies/get_efselab.py

cp -r $SWEGRAM_WORKSPACE/build_dependencies/sv/HistNorm $SWEGRAM_WORKSPACE/tools

mv $SWEGRAM_WORKSPACE/tools/efselab-master $SWEGRAM_WORKSPACE/tools/efselab
cp $SWEGRAM_WORKSPACE/build_dependencies/sv/swe-pipeline-ud2.tar.gz $SWEGRAM_WORKSPACE/tools/efselab
cd $SWEGRAM_WORKSPACE/tools/efselab

# Build lemmatizer
make

tar -xvzf swe-pipeline-ud2.tar.gz
python3 build_suc.py --skip-generate --python --n-train-fields 2
python3 build_suc_ne.py --skip-generate --python --n-train-fields 4

# Build and train the SUC-to-UD conversion model
python3 build_udt_suc_sv.py --python --beam-size 1 --n-train-fields 4
./udt_suc_sv train data/sv-ud-train.tab data/sv-ud-dev.tab swe-pipeline/suc-ud.bin
