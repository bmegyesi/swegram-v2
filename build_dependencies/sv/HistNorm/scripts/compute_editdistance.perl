#!/usr/bin/perl -I /home/evapet/doktorand/

# Syntax: perl compute_editdistance <inputfile>

use strict;
use utf8;

# Input file in the form of a list of token pairs, 
# with the original and normalised version of the token
# on each line
my $unknown = shift @ARGV;
unless(open(UNKNOWN,"<$unknown")){
    die "Infil saknas: $unknown\n";
}

my $weights = shift @ARGV;
unless(open(WEIGHTS,"<$weights")){
    die "Infil saknas: $weights\n";
}

my $endofword="#";

# Weight hashes for different edit operations
my %singledeletion;
my %doubledeletion;
my %singlesubst;
my %double2singlesubst;
my %single2doublesubst;
my %singleinsertion;
my %doubleinsertion;

my $bestcandidates="";
my $currentbest=20;

binmode(UNKNOWN, ":utf8"); # Needed to handle each character in a unicode string as one character only

print STDERR "Make weight arrays\n";
&makeWeightArrays;
print STDERR "Select candidates\n";
&selectcandidates;

sub makeWeightArrays{
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
	    print STDERR "Wrong format in the weights file: $line\n";
	}
    }
}

sub lookupDistance{
    my $norm=shift @_;
    my $orig=shift @_;
    my $distance=shift @_;
    my $wordcount=shift @_; # håll reda på vilken bokstav i det ord vi ska normalisera vi läser just nu
    my $candidatecount=shift @_; # håll reda på vilken bokstav i vår kandidat vi läser just nu
    my $prevweight=shift @_;
    my @origchars = split(//, $orig); # split the word into its separate characters
    my @normchars = split(//, $norm);
    my $normmaxlength=length($norm);
    $normchars[$normmaxlength]="#";
    my $origmaxlength=length($orig);
    $origchars[$origmaxlength]="#";
    my $letter = $origchars[$wordcount];
    my $key = $normchars[$candidatecount];
    return if $distance>$currentbest;
# deletion weights
    my $doubleletter="";
    unless($letter eq "#"){
	if(defined($origchars[$wordcount+1])){
	    my $nextletter=$origchars[$wordcount+1];
	    $doubleletter=$letter.$nextletter;
	}
	if($doubleletter ne "" && defined($doubledeletion{$doubleletter})){
	    my $weight=$doubledeletion{$doubleletter};
	    &lookupDistance($norm,$orig,$distance+$weight,$wordcount+2,$candidatecount,$weight);
	}
	if(defined($singledeletion{$letter})){
	    my $weight=$singledeletion{$letter};
	    &lookupDistance($norm,$orig,$distance+$weight,$wordcount+1,$candidatecount,$weight);
	}
	else{
	    &lookupDistance($norm,$orig,$distance+1,$wordcount+1,$candidatecount,1);
	}
    }
    if($distance<=$currentbest && $letter eq "#" && $key eq "#"){
	$currentbest=$distance;
	$bestcandidates="$distance";
    }
# end-of-word sign
# hela ordet som ska normaliseras har ännu inte lästs in
    elsif($letter ne "#" && $key eq "#"){
	&lookupDistance($norm,$orig,$distance,$wordcount+1,$candidatecount,$prevweight);
    }
    if($key eq $letter && $key ne "#"){
	&lookupDistance($norm,$orig,$distance,$wordcount+1,$candidatecount+1,0);
    }
    else{
	my $keydistance=0;
# insertion weights
	unless($key eq "#"){
	    my $prevkey=$normchars[$candidatecount-1];
	    my $doublekey=$prevkey.$key;
	    if(defined($doubleinsertion{$doublekey})){
		$keydistance=$doubleinsertion{$doublekey};
		&lookupDistance($norm,$orig,$distance+$keydistance-$prevweight,$wordcount,$candidatecount+1,$keydistance);
	    }
	    if(defined($singleinsertion{$key})){
		$keydistance=$singleinsertion{$key};
		&lookupDistance($norm,$orig,$distance+$keydistance,$wordcount,$candidatecount+1,$keydistance);
	    }
	}
# substitution weights
	my $prevkey=$normchars[$candidatecount-1];
	my $singlesubstcandidate=$letter."/".$key;
	my $double2singlesubstcandidate=$doubleletter."/".$key;
	my $single2doublesubstcandidate=$letter."/".$prevkey.$key;
	unless($letter eq "#" || $key eq "#"){
	    if(defined($single2doublesubst{$single2doublesubstcandidate})){
		$keydistance=$single2doublesubst{$single2doublesubstcandidate};
		$distance=$distance-$prevweight;
		&lookupDistance($norm,$orig,$distance+$keydistance,$wordcount+1,$candidatecount+1,$keydistance);
	    }
	    if(defined($double2singlesubst{$double2singlesubstcandidate})){
		$keydistance=$double2singlesubst{$double2singlesubstcandidate};
		$wordcount++;
		&lookupDistance($norm,$orig,$distance+$keydistance,$wordcount+1,$candidatecount+1,$keydistance);
	    }	
	    if(defined($singlesubst{$singlesubstcandidate})){
		$keydistance=$singlesubst{$singlesubstcandidate};
		&lookupDistance($norm,$orig,$distance+$keydistance,$wordcount+1,$candidatecount+1,$keydistance);
	    }
	    else{
		$keydistance=1;
		&lookupDistance($norm,$orig,$distance+$keydistance,$wordcount+1,$candidatecount+1,$keydistance);
	    }
	}
	
    }
}



sub selectcandidates{
    while(<UNKNOWN>){
	chomp;
	my $line=$_;
	if($line=~/^\s*$/ || $line=~/^[\)\.\?\!\—\{\}\']+\t[\)\.\?\!\—\{\}\']+$/){ # Empty lines and punctuations are not normalised
	}
# Input should be one token on each line
	elsif($line=~/^([^\t]+)\t([^\t]+)$/){
	    my $orig=$1;
	    my $norm=$2;
	    my $lcorig=lc($orig); # lowercase form of the word
	    my $lcnorm=lc($norm);
	    my @origchars = split(//, $lcorig); # split the word into its separate characters
	    my @normchars = split(//, $lcnorm);
#	    print STDERR "normalise: $lcorig\n";
	    $currentbest=20;
	    $bestcandidates="";
	    &lookupDistance($lcnorm,$lcorig,0,0,0,0);
	    unless($bestcandidates eq ""){
		print "$bestcandidates\n";
	    }
	}
	else{
	    print STDERR "Unexpected format in the input file: $line\n";
	}
    }
    close UNKNOWN;
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
