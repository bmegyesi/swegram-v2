#!/bin/bash

WORKINGDIR=$1
INPUTTRAIN=$2
INPUTDEV=$3
WEIGHTS=$4
THRESHOLD=$5

WORKINGDIR=`echo $WORKINGDIR|perl -e 'my $line=<>;$line=~s/\/$//;print $line;'`

# extract edits performed in the training corpus
echo 'Extract edits from training data...'
perl -CSAD $WORKINGDIR/findEdits.perl $INPUTTRAIN > temp

# calculate weights based on the exracted edits
echo 'Calculate weights from edits...'
perl -CSAD $WORKINGDIR/extractWeights.perl temp > $WEIGHTS
rm -f temp

# run the weights on the development set, and set an appropriate threshold
echo 'Compute edit distances on development data...'
perl -CSAD $WORKINGDIR/compute_editdistance.perl $INPUTDEV $WEIGHTS > temp
perl -CSAD $WORKINGDIR/set_threshold.perl temp > $THRESHOLD
rm -f temp

