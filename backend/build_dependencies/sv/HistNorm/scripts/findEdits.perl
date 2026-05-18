#!/usr/bin/perl 

#################################
#
# Script for finding frequently occurring edits based on observed manual normalisations.
#
# Syntax: perl findEdits.perl <INPUTFILE>
#
# Created by Eva Pettersson, eva.pettersson@lingfil.uu.se
# Latest version: 2012-10-30
#
# See usersguide-histnorm.pdf for details on how to run the script.
#
#################################


use strict;
use Storable;
use utf8;

# Input file in the form of a list of tokens, unnormalised and normalised on each line
my $unknown = shift @ARGV;
unless(open(UNKNOWN,"<$unknown")){
    die "Infil saknas: $unknown\n";
}


# Weight hashes for different edit operations
my %singledeletion;
my %doubledeletion;
my %singlesubst;
my %double2singlesubst;
my %single2doublesubst;
my %singleinsertion;
my %doubleinsertion;

my $bestcandidates="";
my $bestedits="";
my $currentbest=10;

binmode(UNKNOWN, ":utf8"); # Needed to handle each character in a unicode string as one character only
binmode(STDOUT, ":utf8"); # Needed to handle each character in a unicode string as one character only

&compareTokens;


sub lookupDistance{
    my $orig=shift @_;
    my $norm=shift @_;
    my $distance=shift @_;
    my $origcount=shift @_;
    my $normcount=shift @_;
    my $edits=shift @_;
    my @origword = split(//, $orig); # split the original word into its separate characters
    my @normword = split(//, $norm); # split the normalised word into its separate characters
    my $letter="#";
    my $key="#";
    if(defined($origword[$origcount])){
	$letter = @origword[$origcount];
    }
    if(defined($normword[$normcount])){
	$key = @normword[$normcount];
    }
    return if $distance>$currentbest;

    my $origdoubleletter="";
    my $normdoublekey="";
    if(defined($origword[$origcount+1])){
	my $nextletter=$origword[$origcount+1];
	$origdoubleletter=$letter.$nextletter;
    }
    if(defined($normword[$normcount+1])){
	my $nextkey=$normword[$normcount+1];
	$normdoublekey=$key.$nextkey;
    }

##### end-of-word
    if($distance<$currentbest && $letter eq "#" && $key eq "#"){
	$currentbest=$distance;
	$bestedits=$edits;
    }
    elsif($distance==$currentbest && $letter eq "#" && $key eq "#"){
	$bestedits=$edits;
    }

##### end-of-original-word (insertion)
    elsif($letter eq "#" && $key ne "#"){
# single
	my $edit="+".$key;
	my $newedits=$edits."\|$edit\|";
	&lookupDistance($orig,$norm,$distance+1,$origcount,$normcount+1,$newedits);
    }

##### end-of-normalised-word (deletion)
    elsif($letter ne "#" && $key eq "#"){
# single
	my $edit="-".$letter;
	my $newedits=$edits."\|$edit\|";
	&lookupDistance($orig,$norm,$distance+1,$origcount+1,$normcount,$newedits);
    }

##### equality = no edit
    elsif($key eq $letter){
	my $newedits=$edits."\|$key\|";
	&lookupDistance($orig,$norm,$distance,$origcount+1,$normcount+1,$newedits);
    }
    else{
##### deletion
# single (& double2single substitution)
	my $edit="-".$letter;
	my $newedits=$edits."\|$edit\|";
	if(defined($origword[$origcount-1]) && defined($normword[$normcount-1])){
	    $newedits.="\|$origword[$origcount-1]$letter\/$normword[$normcount-1]\|";
	}
	&lookupDistance($orig,$norm,$distance+1,$origcount+1,$normcount,$newedits);
# double
	if($origdoubleletter ne ""){
	    my $firstedit="-".$letter;
	    my $secondedit="-".$origword[$origcount+1];
	    my $doubleedit="-".$origdoubleletter;
	    my $newedits=$edits."\|$firstedit\|\|$secondedit\|\|$doubleedit\|";
	    &lookupDistance($orig,$norm,$distance+1,$origcount+2,$normcount,$newedits);
	}
##### insertion
# single (& single2double substitution)
	my $edit="+".$key;
	my $newedits=$edits."\|$edit\|";
	if(defined($origword[$origcount-1]) && defined($normword[$normcount-1])){
	    $newedits.="\|$origword[$origcount-1]\/$normword[$normcount-1]$key\|";
	}
	&lookupDistance($orig,$norm,$distance+1,$origcount,$normcount+1,$newedits);
# double
	if($normdoublekey ne ""){
	    my $firstedit="+".$key;
	    my $secondedit="+".$normword[$normcount+1];
	    my $doubleedit="+".$normdoublekey;
	    my $newedits=$edits."\|$firstedit\|\|$secondedit\|\|$doubleedit\|";
	    &lookupDistance($orig,$norm,$distance+1,$origcount,$normcount+2,$newedits);
	}
##### substitution
# single-to-single
	$edit="$letter/$key";
	$newedits=$edits."\|$edit\|";
	&lookupDistance($orig,$norm,$distance+1,$origcount+1,$normcount+1,$newedits);
    }
}

sub compareTokens{
    while(<UNKNOWN>){
	chomp;
	my $line=$_;
	$line=~tr/A-ZÅÄÖ/a-zåäö/;
	if($line=~/^\s*$/ || $line=~/^[\(\)\[\]\;\:\t\)\,\.\?\!\—\{\}\'0-9]+\s*$/){ # Empty lines and punctuations are not normalised
	}
	elsif($line=~/^([^\t]+)\t([^\t]+)\s*$/){
	    my $orig=$1;
	    my $norm=$2;
	    $currentbest=10;
	    &lookupDistance($orig,$norm,0,0,0,""),
	    print "$orig\t$norm\t$bestedits\n";
	}
	else{
	    print STDERR "Wrong input format in token file: $line\n";
	}
    }
    close UNKNOWN;
}
