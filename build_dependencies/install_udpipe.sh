#! /bin/bash

set -e

# set workspace
workspace=$(pwd)/build_dependencies

if [ -f "$workspace/en/udpipe" ]
then
    echo "File udpipe exists"
else
    echo "Start compiling udpipe"

    # set temp
    temp_dir=$(mktemp -d -p $workspace)
    echo $temp_dir

    git clone git@github.com:ufal/udpipe.git $temp_dir

    # enter into the src folder
    cd $temp_dir/src

    # make
    make

    cd $workspace
    cp $temp_dir/src/udpipe en
    rm -rf $temp_dir
fi
