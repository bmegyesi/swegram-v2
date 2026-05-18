#!/usr/bin/perl

#######################################################
#
# This script performs Levenshtein-based spelling normalisation
#
# Example syntax:
#
# perl -CSAD scripts/normalise_levenshtein.perl resources/german/german.de-hs.test.hs resources/german/parole.mono.de.uniq resources/german/german.de-hs.train.hsde resources/german/parole.mono.de resources/german/training-weights.german.txt resources/german/threshold.german.txt > results/german.de-hs.test.hs.normalised
#
# Arguments:
# 1) Input file with unnormalised words, one token per line.
# 2) Modern language dictionary for Levenshtein comparisons,
#    one token per line.
# 3) Token pairs with historical word forms mapped to manually
#    normalised spellings. If no such file is available, just
#    print the string "nostop" as the third argument
# 4) Corpus of modern language for choosing the most frequent
#    normalisation candidate in case of a tie, one token per line.
# 5) File with weights lower than 1 for frequently occurring
#    edits observed in the training data. If no such file is
#    available, just print the string "noweights" as the
#    fifth argument.
# 6) File containing the desired edit distance threshold.
#
#######################################################




use strict;

# Input file in the form of a list of tokens, one token on each line
my $unknown = shift @ARGV;
unless(open(UNKNOWN,"<$unknown")){
    die "Inputfile missing: $unknown\n";
}

# Modern language dictionary
my $dict = shift @ARGV;
unless(open(DICT,"<$dict")){
    die "Dictionary file missing: $dict\n";
}
my %trie=();
my %dicentries=();


# Token pairs with historical word forms mapped to
# manually normalised spellings
my $stopname = shift @ARGV;
my %stop=();

# Modern language corpus for frequency-based candidate selection
my $moderncorpus=shift @ARGV;
unless(open(FREQS,"<$moderncorpus")){
    die "Modern corpus missing: $moderncorpus\n";
}
my %freqs=();

# Weights lower than 1 for frequently occurring edits
my $weightsname = shift @ARGV;

# Hash of cached words, i.e. words that have previously been normalised
my  %cache=();

# Edit distance threshold
my $threshold=shift @ARGV;
unless(open(THRESHOLD,"<$threshold")){
    die "Threshold file missing: $threshold\n";
}

my $bestcandidates="";
my $currentbest=0;
my $maxdistance=$currentbest;

my $endmarker="#";
my $wordforms=0; # count wordforms
my $endofword="#";
my %processed=();

# Weight hashes for different edit operations
my %singledeletion;
my %doubledeletion;
my %singlesubst;
my %double2singlesubst;
my %single2doublesubst;
my %singleinsertion;
my %doubleinsertion;

print STDERR "Setting threshold...\n";
&setThreshold;
print STDERR "Creating dictionary in trie format...\n";
&makeTrie;
&printStatistics;
unless($stopname eq "nostop"){ # Hash of stopwords, with information on how to normalise them
    print STDERR "creating validated cache...\n";
    &makeStopHash;
}
print STDERR "extracting frequency information...\n";
&extractFrequencies;
unless($weightsname eq "noweights"){
    print STDERR "Make weight arrays\n";
    &makeWeightArrays;
}
print STDERR "selecting candidates...\n";
&selectcandidates;

sub setThreshold{
    my $check=0;
    while(<THRESHOLD>){
	chomp;
	my $line=$_;
	if($line=~/^\s*([\d\.]+)\s*$/){
	    $currentbest=$1;
	    $maxdistance=$currentbest;
	    $check=1;
	}
    }
    unless($check==1){
	die "Threshold value incorrect\n";
    }
    close THRESHOLD;
}

sub makeTrie{
    my $wordform="";
    while(<DICT>){
	chomp;
	my $line=$_;
### we have found a token to store
	if($line=~/^\s*([^\t]+)\s*$/){
	    $wordform=$1;
	    $wordforms++;
	    my $lcwordform=lc($wordform); # lowercase form of the word
	    unless(defined($processed{$lcwordform})){
		my @chars = split(//, $lcwordform); # split the word into its separate chars
		&add(\%trie, @chars); # add the split token to the trie structure
	    }
	    $processed{$lcwordform}=$lcwordform;
	    unless(defined($dicentries{$lcwordform}) && $dicentries{$lcwordform} eq $lcwordform){
	      $dicentries{$lcwordform}=$wordform;
	    }
	  }
### blank lines are ignored without warning
	elsif($line=~/^\s*$/){
	}
### multi-word units are ignored, with a warning
	elsif($line=~/\s/){
	    print STDERR "Ignoring multi-word unit: $line\n";
	}
	else{
	    print STDERR "Unexpected format in dict: $line\n";
	}
    }
    close DICT;
}


sub add{
    my $newhash=shift @_;
    my @chars= @_;
    while(my $char = shift @chars){
	unless(defined($newhash->{$char})){
	    $newhash->{$char} = {};
	}
	$newhash=$newhash->{$char};
    }
    $newhash->{$endofword} = {}; # end-of-word sign
}

sub printStatistics{
    print STDERR "Total number of wordforms stored in the trie: $wordforms\n";
}


sub makeStopHash{
    my $tokens=0;
    my $types=0;
    unless(open(STOPFILE,"<$stopname")){
	die "Stopfile missing: $stopname\n";
    }
    while(<STOPFILE>){
	chomp;
	my $line=$_;
### we have found a token to store
	if($line=~/^\s*([^\t]+)\t([^\t]+)\s*$/){
	    my $src=$1;
	    my $trg=$2;
	    $tokens++;
	    my $lcsrc=lc($src); # lowercase form of the source word
	    my $lctrg=lc($trg); # lowercase form of the target word
	    my $quotedtrg=quotemeta($lctrg);
	    if(defined($stop{$lcsrc})){
		unless($stop{$lcsrc}=~/\|$quotedtrg\|/){
		    $stop{$lcsrc}.="\|$lctrg\|";
		}
	    }
	    else{
		$types++;
		$stop{$lcsrc}.="\|$lctrg\|";
	    }
	}
### blank lines are ignored without warning
	elsif($line=~/^\s*$/){
	}
### multi-word units are ignored, with a warning
	elsif($line=~/\ /){
	    print STDERR "Ignoring multi-word unit: $line\n";
	}
	else{
	    print STDERR "Unexpected format: $line\n";
	}
    }
    close STOPFILE;
    print STDERR "Total number of types extracted from the corpus (validated cache): $types\n";
    print STDERR "Total number of tokens extracted from the corpus (validated cache): $tokens\n";
}


sub extractFrequencies{
    my $wordform="";
    my $tokens=0;
    my $types=0;
    while(<FREQS>){
	chomp;
	my $line=$_;
### we have found a token to store
	if($line=~/^\s*([^\t]+)\s*$/){
	    $wordform=$1;
	    $tokens++;
	    my $lcwordform=lc($wordform); # lowercase form of the word
	    if(defined($freqs{$lcwordform})){
		my $count=$freqs{$lcwordform};
		$count++;
		$freqs{$lcwordform}=$count;
	    }
	    else{
		$types++;
		$freqs{$lcwordform}=1;
	    }
	}
### blank lines are ignored without warning
	elsif($line=~/^\s*$/){
	}
### multi-word units are ignored, with a warning
	elsif($line=~/\s/){
	    print STDERR "Ignoring multi-word unit: $line\n";
	}
	else{
	    print STDERR "Unexpected format: $line\n";
	}
    }
    close FREQS;
    print STDERR "Total number of types extracted from the corpus (freqs): $types\n";
    print STDERR "Total number of tokens extracted from the corpus (freqs): $tokens\n";
}

sub makeWeightArrays{
    unless(open(WEIGHTS,"<$weightsname")){
	die "Infil saknas: $weightsname\n";
    }
    while(<WEIGHTS>){
	chomp;
	my $line = $_;
# single deletion
	if($line=~/^\-(.)\t([0-9\.]+)$/){
	    my $letter=$1;
	    my $weight=$2;
	    $singledeletion{$letter}=$weight;
	}
# double deletion
	elsif($line=~/^\-(..+?)\t([0-9\.]+)$/){
	    my $letter=$1;
	    my $weight=$2;
	    $doubledeletion{$letter}=$weight;
	}
# single substitution
	elsif($line=~/^(.\/.)\t([0-9\.]+)$/){
	    my $letter=$1;
	    my $weight=$2;
	    $singlesubst{$letter}=$weight;
	}
# double2single substitution
	elsif($line=~/^(..\/.)\t([0-9\.]+)$/){
	    my $letter=$1;
	    my $weight=$2;
	    $double2singlesubst{$letter}=$weight;
	}
# single2double substitution
	elsif($line=~/^(.\/..)\t([0-9\.]+)$/){
	    my $letter=$1;
	    my $weight=$2;
	    $single2doublesubst{$letter}=$weight;
	}
# single insertion
	elsif($line=~/^\+(.)\t([0-9\.]+)$/){
	    my $letter=$1;
	    my $weight=$2;
	    $singleinsertion{$letter}=$weight;
	}
# double insertion
	elsif($line=~/^\+(..+?)\t([0-9\.]+)$/){
	    my $letter=$1;
	    my $weight=$2;
	    $doubleinsertion{$letter}=$weight;
	}
	else{
	    print STDERR "Wrong format in yhe weights file: $line\n";
	}
    }
}


sub lookupDistance{
    my $currenttrie=shift @_;
    my $wordform=shift @_;
    my $distance=shift @_;
    my $wordcount=shift @_; # keep track of what letter in the word to normalise we are processing at the moment
    my $candidatecount=shift @_; # keep track of what letter in the normalisation candidate we are processing at the moment
    my $candidate=shift @_;
    my $prevweight=shift @_;
    my @word = split(//, $wordform); # split the word into its separate characters
    my $letter="#";
    my $quotedletter=quotemeta($letter);
    if(defined($word[$wordcount])){
	$letter = @word[$wordcount];
    }

# we have reached the maximum edit distance
    return if $distance>$currentbest;

# deletion weights
    my $doubleletter="";
    if(defined($word[$wordcount+1])){
	my $nextletter=$word[$wordcount+1];
	$doubleletter=$letter.$nextletter;
    }
    if($doubleletter ne "" && defined($doubledeletion{$doubleletter})){
	my $weight=$doubledeletion{$doubleletter};
	&lookupDistance($currenttrie,$wordform,$distance+$weight,$wordcount+2,$candidatecount,$candidate,$weight);
    }
    if(defined($singledeletion{$letter})){
	my $weight=$singledeletion{$letter};
	&lookupDistance($currenttrie,$wordform,$distance+$weight,$wordcount+1,$candidatecount,$candidate,$weight);
    }
    else{
	&lookupDistance($currenttrie,$wordform,$distance+1,$wordcount+1,$candidatecount,$candidate,1);
    }
    for (keys %$currenttrie){
	my $key=$_;
	my $keydistance=0;
# end-of-word sign
# edit distance is below the given threshold, and the whole word to be normalised has been processed
	if($distance<$currentbest && $letter eq "#" && $key eq "#"){
	    $currentbest=$distance;
	    $bestcandidates="\|$candidate\|";
	}
	elsif($distance==$currentbest && $letter eq "#" && $key eq "#"){
	    my $quotedcandidate=quotemeta($candidate);
	    unless($bestcandidates=~/\|$quotedcandidate\|/){ # undvik dubbletter
		$bestcandidates.="\|$candidate\|";
	    }
	}
# end-of-word sign
# the whole word to be normalised has not yet been processed
	elsif($letter ne "#" && $key eq "#"){
	    if(defined($currenttrie->{$key})){
		my $newtrie=$currenttrie->{$key};
		&lookupDistance($newtrie,$wordform,$distance,$wordcount,$candidatecount,$candidate.$key,$prevweight);
	    }
	}
	if($key eq $letter){
	    if(defined($currenttrie->{$key})){
		my $newtrie=$currenttrie->{$key};
		&lookupDistance($newtrie,$wordform,$distance,$wordcount+1,$candidatecount+1,$candidate.$key,0);
	    }
	}
	else{
	    my $quotedkey=quotemeta($key);
# insertion weights
	    my $prevkey=$candidate;
	    $prevkey=~s/^.*(.)$/$1/;
	    my $doublekey=$prevkey.$key;
	    if(defined($doubleinsertion{$doublekey})){
		$keydistance=$doubleinsertion{$doublekey};
		if(defined($currenttrie->{$key})){
		    my $newtrie=$currenttrie->{$key};
		    &lookupDistance($newtrie,$wordform,$distance+$keydistance-$prevweight,$wordcount,$candidatecount+1,$candidate.$key,$keydistance);
		}
	    }
	    if(defined($singleinsertion{$key})){
		$keydistance=$singleinsertion{$key};
		if(defined($currenttrie->{$key})){
		    my $newtrie=$currenttrie->{$key};
		    &lookupDistance($newtrie,$wordform,$distance+$keydistance,$wordcount,$candidatecount+1,$candidate.$key,$keydistance);
		}
	    }
	    else{
	      if(defined($currenttrie->{$key})){
		my $newtrie=$currenttrie->{$key};
		    &lookupDistance($newtrie,$wordform,$distance+1,$wordcount,$candidatecount+1,$candidate.$key,$keydistance);
	      }
	    }
# substitution weights
	    my $prevkey=$candidate;
	    $prevkey=~s/^.*(.)$/$1/;
	    my $singlesubstcandidate=$letter."/".$key;
	    my $double2singlesubstcandidate=$doubleletter."/".$key;
	    my $single2doublesubstcandidate=$letter."/".$prevkey.$key;

	    if(defined($single2doublesubst{$single2doublesubstcandidate})){
		$keydistance=$single2doublesubst{$single2doublesubstcandidate};
		$distance=$distance-$prevweight;
		if(defined($currenttrie->{$key})){
		    my $newtrie=$currenttrie->{$key};
		    &lookupDistance($newtrie,$wordform,$distance+$keydistance,$wordcount+1,$candidatecount+1,$candidate.$key,$keydistance);
		}
	    }
	    if(defined($double2singlesubst{$double2singlesubstcandidate})){
		$keydistance=$double2singlesubst{$double2singlesubstcandidate};
		$wordcount++;
		if(defined($currenttrie->{$key})){
		    my $newtrie=$currenttrie->{$key};
		    &lookupDistance($newtrie,$wordform,$distance+$keydistance,$wordcount+1,$candidatecount+1,$candidate.$key,$keydistance);
		}
	    }
	    if(defined($singlesubst{$singlesubstcandidate})){
		$keydistance=$singlesubst{$singlesubstcandidate};
		if(defined($currenttrie->{$key})){
		    my $newtrie=$currenttrie->{$key};
		    &lookupDistance($newtrie,$wordform,$distance+$keydistance,$wordcount+1,$candidatecount+1,$candidate.$key,$keydistance);
		}

	    }
	    else{
		$keydistance=1;
		if(defined($currenttrie->{$key})){
		    my $newtrie=$currenttrie->{$key};
		    &lookupDistance($newtrie,$wordform,$distance+$keydistance,$wordcount+1,$candidatecount+1,$candidate.$key,$keydistance);
		}

	    }
	}
    }
}


sub selectcandidates{
    my $check=0; # check whether we are in sentence-initial position or not
    while(<UNKNOWN>){
	chomp;
	my $line=$_;
	my $capitals = "lower"; # elevtexter, check uppercase vs lowercase
	if($line=~/^\s*$/ || $line=~/^[\)\.\?\!\—\{\}\']$/){ # Empty lines and punctuations are not normalised
	    print "$line\n";
	    $check=0;
	}
# Input should be one token on each line
	elsif($line=~/^([^\s]+)\s*$/){
	    my $wordform=$1;
	    my $lcwordform=lc($wordform); # lowercase form of the word
	    if($wordform=~/^[[:upper:]][[:lower:]]*\-[[:upper:]][[:lower:]]+/){ # Sven-Bertil
	      $capitals = "upperfirsthyphen";
	    }
	    elsif($wordform=~/^[[:upper:]][[:upper:]][[:lower:]]/){ # elevtexter
	      if($check==1){
		$capitals = "uppersecondfirst";
	      }
	      else{
		$capitals = "upperfirst";
	      }
	    }
	    elsif($wordform=~/^[[:upper:]][[:upper:]]\-[[:lower:]]/){ # TV-spel
	      $capitals = "upperupperhyphen";
	    }
	    elsif($wordform=~/^[[:upper:]][[:lower:]\.\-]/){ # elevtexter
	      $capitals = "upperfirst";
	    }
	    elsif($wordform=~/^[[:upper:]]+[\:\-][[:lower:]]+/){ # DN:s
	      $capitals = "uppercolon";
	    }
	    elsif($wordform=~/^[[:upper:]]/){
	      $capitals = "upper";
	    }
	    my @chars = split(//, $wordform); # split the word into its separate characters
	    my $wordlength=@chars; # count the number of characters in the word
# Some trivial normalisation is performed without cost
	    $lcwordform=~s/æ/e/g;
	    $lcwordform=~s/ß/s/g;
	    $wordform=~s/æ/e/g;
	    $wordform=~s/ß/s/g;
#	    if($lcwordform=~/[a-zåäö]/){
#	      $lcwordform=~s/\.\d+$//;
#	      $wordform=~s/\.\d+$//;
#	      #		$lcwordform=~s/[\d\(\)\[\]\—\'\{\}]+//g;
#	      #		$wordform=~s/[\d\(\)\[\]\—\'\{\}]+//g;
#	    }
# If the word is in the stoplist, choose the normalised version present in the stoplist
	    if($stopname ne "nostop" && defined($stop{$lcwordform})){
	      my $candidate=$stop{$lcwordform};
	      my $bestcandidate=$candidate;
	      if($candidate=~/^\|/){ # several candidates - choose the most frequent one
		$bestcandidate=selectBestCandidate($candidate,$capitals); # elevtexter
	      }
	      if($bestcandidate=~/^[[:lower:]]/ && defined($dicentries{$bestcandidate})){ # elevtexter
		print "$dicentries{$bestcandidate}\n";
	      }
	      else{
		print "$bestcandidate\n";
	      }
	      print STDERR "stopword: $lcwordform = $bestcandidate\n";
	    }
# Else if the word has been normalised before, choose the same normalisation as previously
	    elsif(defined($cache{$lcwordform})){
	      my $bestcandidate = $cache{$lcwordform};
	      if($capitals eq "upper"){                      # elevtexter
		$bestcandidate = uc($bestcandidate);
	      }
	      elsif($capitals eq "uppersecondfirst"){                      # elevtexter
		$bestcandidate=~s/([[:upper:]]+)([[:upper:]]+)/\L$1\L$2/;
	      }
	      elsif($capitals eq "upperupperhyphen"){                      # elevtexter
		$bestcandidate=~s/^(..)\-/\U$1\-/;
	      }
	      elsif($capitals eq "upperfirst"){                      # elevtexter
		$bestcandidate = ucfirst($bestcandidate);
	      }
	      elsif($capitals eq "upperfirsthyphen"){                      # elevtexter
		$bestcandidate = ucfirst($bestcandidate);
		$bestcandidate=~s/\-([[:lower:]])/\-\U$1/;
	      }
	      elsif($capitals eq "uppercolon"){                      # elevtexter
		$bestcandidate=~s/([\:\-])([[:upper:]]+)/\1\L$2/;
	      }
	      print "$bestcandidate\n";
	      print STDERR "cache: $lcwordform = $bestcandidate\n";
	    }
# Do not normalise if there is an uppercase character at the beginning of the word,
# and the word is not in sentence-initial position
# specifically for "elevtexter"
	    elsif(($check==1 && $wordform=~/^[[:upper:]]/)){
	      print "$wordform\n";
	      print STDERR "do not normalise (proper name): $wordform\n";
	    }
# Do not normalise if the word is present in the dictionary, or if the word is of the length of one character only, or if it
# contains punctuations or digits
	    elsif(&lookupWordForm($lcwordform) eq $lcwordform || $wordlength<2 || $lcwordform=~/[\d\:\.\;\,\?\!]/){
	      if($wordform=~/^[[:lower:]]/ && defined($dicentries{$wordform})){ # elevtexter
		print "$dicentries{$wordform}\n";
	      }
	      else{
		print "$wordform\n";
	      }
	      print STDERR "do not normalise (in dic): $wordform\n";
	    }
	    else{
	      print STDERR "normalise: $wordform\n";
	      $currentbest=$maxdistance;
	      &lookupDistance(\%trie,$lcwordform,0,0,0,"");
	      print STDERR "Select best candidate for wordform: $wordform ($bestcandidates)\n"; # elevtexter
	      my $bestcandidate="";
	      if($bestcandidates eq ""){
		$bestcandidate=$wordform;
		$cache{$lcwordform} = lc($bestcandidate);
	      }
	      elsif($bestcandidates=~/^\|([^\|]+)\|$/){ # one candidate only
		$bestcandidate=$1;
		$cache{$lcwordform} = lc($bestcandidate);
		if($capitals eq "upper"){                      # elevtexter
		  $bestcandidate = uc($bestcandidate);
		}
		elsif($capitals eq "uppersecondfirst"){                      # elevtexter
		  $bestcandidate=~s/([[:upper:]]+)([[:upper:]]+)/\L$1\L$2/;
		}
		elsif($capitals eq "upperupperhyphen"){                      # elevtexter
		  $bestcandidate=~s/^(..)\-/\U$1\-/;
		}
		elsif($capitals eq "upperfirst"){                      # elevtexter
		  $bestcandidate = ucfirst($bestcandidate);
		}
		elsif($capitals eq "upperfirsthyphen"){                      # elevtexter
		  $bestcandidate = ucfirst($bestcandidate);
		  $bestcandidate=~s/\-([[:lower:]])/\-\U$1/;
		}
		elsif($capitals eq "uppercolon"){                      # elevtexter
		  $bestcandidate=~s/([\:\-])([[:upper:]]+)/\1\L$2/;
		}

	      }
	      else{ # several candidates - choose the most frequent one
		$bestcandidate=selectBestCandidate($bestcandidates,$wordform); # elevtexter
		$cache{$lcwordform} = lc($bestcandidate);
	      }
	      if($bestcandidate=~/^[[:lower:]]/ && defined($dicentries{$bestcandidate})){ # elevtexter
		print "$dicentries{$bestcandidate}\n";
	      }
	      else{
		print "$bestcandidate\n";
	      }
	      print STDERR "bestcandidates: $bestcandidates\n";
	      print STDERR "bestcandidate: $bestcandidate\n";
	      $bestcandidates="";
	    }
	    $check=1;
	  }
	else{
	    print STDERR "Wrong input format in token file: $line\n";
	}
    }
    close UNKNOWN;
}


sub selectBestCandidate{
    my $candidates = shift @_; # list of possible candidates, separated by slash
    my $capitals = shift @_; # elevtexter: needed for getting the right form of upper-case vs lower-case letters
    my $bestcandidate="";
    if($candidates=~/^\|(.+?)\|.*$/){
	$bestcandidate=$1;
	my $freq=0;
	while($candidates=~/^\|(.+?)\|(.*)$/){
	    my $currentcandidate=$1;
	    $candidates=$2;
	    if(defined($freqs{$currentcandidate}) && $freqs{$currentcandidate}>$freq){
		$bestcandidate=$currentcandidate;
		$freq=$freqs{$currentcandidate};
	    }
	}
    }
    else{
	print STDERR "Wrong candidate format: $candidates\n";
    }
    if($capitals eq "upperfirst"){                    # elevtexter
      $bestcandidate = ucfirst($bestcandidate);
    }
    elsif($capitals eq "upperupperhyphen"){                      # elevtexter
      $bestcandidate=~s/^(..)\-/\U$1\-/;
    }
    elsif($capitals eq "uppersecondfirst"){                      # elevtexter
      $bestcandidate=~s/([[:upper:]]+)([[:upper:]]+)/\L$1\L$2/;
    }
    elsif($capitals eq "upperfirsthyphen"){                      # elevtexter
      $bestcandidate = ucfirst($bestcandidate);
      $bestcandidate=~s/\-([[:lower:]])/\-\U$1/;
    }
    elsif($capitals eq "uppercolon"){                      # elevtexter
      $bestcandidate=~s/([\:\-])([[:upper:]]+)/\1\L$2/;
    }
    elsif($capitals eq "upper"){
      $bestcandidate = uc($bestcandidate);
    }
    return $bestcandidate;
}

sub lookupWordForm{
    my $wordform = shift @_;
    my $currenttrie = \%trie;
    my @chars = split(//, $wordform); # split the word into its separate characters
    my $check=0;
    while(@chars && $check==0){
	my $char = shift @chars;
	if(defined($currenttrie->{$char})){
	    $currenttrie=$currenttrie->{$char};
	}
	else{
	    $check=1;
	}
    }
    if($check==0){
	if(defined($currenttrie->{"#"})){
	    return $wordform;
	}
    }
}
