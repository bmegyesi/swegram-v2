#!/usr/bin/perl

#################################
#
# Script for calculating Levenshtein weights based on observed edits. 
#
# Syntax: perl extractWeights.perl <INPUTFILE>
#
# Created by Eva Pettersson, eva.pettersson@lingfil.uu.se
# Latest version: 2012-10-30
#
# See usersguide-histnorm.pdf for details on how to run the script.
#
#################################

use strict;
use utf8;

# input file of tokens with the corresponding edits
my $in = shift @ARGV;
unless(open(IN,"<$in")){
    die "Infil saknas: $in\n";
}

my $threshold=50;

my %equals;
my %doubleequals;
my %singledeletions;
my %doubledeletions;
my %singleinsertions;
my %doubleinsertions;
my %singlesubsts;
my %double2singlesubsts;
my %single2doublesubsts;

my $editcount=0;


binmode(IN, ":utf8"); # Needed to handle each character in a unicode string as one character only
binmode(STDOUT, ":utf8"); # Needed to handle each character in a unicode string as one character only


##### Main program #####
&processInput;
&setWeights;

sub processInput{
    while(<IN>){
	chomp;
	my $line=$_;
	my @origs;
	my @norms;
	if($line=~/^([^\s]+)\t[^\s]+\t(\|.+\|)$/){
	    my $origword=$1;
	    my $edits=$2;
	    my $prev="";
	    while($edits=~/^\|(.+?)\|(.*)$/){
		my $current=$1;
		$edits=$2;
		    unless($current=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
# equality
			if($current=~/^.$/){
			    my $count=0;
			    if(defined($equals{$current})){
				$count=$equals{$current};
			    }
			    $count++;
			    $equals{$current}=$count;
			    if($prev=~/^(.)$/){
				my $prevchar=$1;
				my $doublecount=0;
				my $doubleletter=$prevchar.$current;
				if(defined($doubleequals{$doubleletter})){
				    $doublecount=$doubleequals{$doubleletter};
				}
				$doublecount++;
				$doubleequals{$doubleletter}=$doublecount;

			    }
			}
# deletion
			elsif($current=~/^-(.)$/){
			$current=$1;
			$editcount++;
			my $count=0;
			if(defined($singledeletions{$current})){
			    $count=$singledeletions{$current};
			}
			$count++;
			$singledeletions{$current}=$count;
		    }
		    elsif($current=~/^-(..)$/){
			$current=$1;
			$editcount++;
			my $count=0;
			if(defined($doubledeletions{$current})){
			    $count=$doubledeletions{$current};
			}
			$count++;
			$doubledeletions{$current}=$count;
		    }
# insertion
		    elsif($current=~/^\+(.)$/){
			$current=$1;
			$editcount++;
			my $count=0;
			if(defined($singleinsertions{$current})){
			    $count=$singleinsertions{$current};
			}
			$count++;
			$singleinsertions{$current}=$count;
		    }
		    elsif($current=~/^\+(..)$/){
			$current=$1;
			$editcount++;
			my $count=0;
			if(defined($doubleinsertions{$current})){
			    $count=$doubleinsertions{$current};
			}
			$count++;
			$doubleinsertions{$current}=$count;
		    }
# substitution
		    elsif($current=~/^(.\/.)$/){
			$current=$1;
			$editcount++;
			my $count=0;
			if(defined($singlesubsts{$current})){
			    $count=$singlesubsts{$current};
			}
			$count++;
			$singlesubsts{$current}=$count;
		    }
		    elsif($current=~/^(.\/..)$/){
			$current=$1;
			$editcount++;
			my $count=0;
			if(defined($single2doublesubsts{$current})){
			    $count=$single2doublesubsts{$current};
			}
			$count++;
			$single2doublesubsts{$current}=$count;
		    }
		    elsif($current=~/^(..\/.)$/){
			$current=$1;
			$editcount++;
			my $count=0;
			if(defined($double2singlesubsts{$current})){
			    $count=$double2singlesubsts{$current};
			}
			$count++;
			$double2singlesubsts{$current}=$count;
		    }
		    else{
			print STDERR "Wrong format: $current\n";
		    }
		    }
		    $prev=$current;
		}
	}
	else{
	    print STDERR "Wrong format in the input file: $line\n";
	}
    }
}

sub setWeights{
    foreach my $char (keys %singledeletions){
	    unless($char=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
		my $freq=$singledeletions{$char};
		my $editoperation="-".$char;
		if($freq>=$threshold){
		    &printWeights($char,$freq,$editoperation);
		}
	    }
    }
    foreach my $char (keys %doubledeletions){
	    unless($char=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
		my $freq=$doubledeletions{$char};
		my $editoperation="-".$char;
		if($freq>=$threshold){
		    &printWeights($char,$freq,$editoperation);
		}
	    }
    }
    foreach my $char (keys %singleinsertions){
	unless($char=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
	    my $freq=$singleinsertions{$char};
	    my $editoperation="+".$char;
	    if($freq>=$threshold){
		&printWeights($char,$freq,$editoperation);
	    }
	}
    }
    foreach my $char (keys %doubleinsertions){
	unless($char=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
	    my $freq=$doubleinsertions{$char};
	    my $editoperation="+".$char;
	    if($freq>=$threshold){
		&printWeights($char,$freq,$editoperation);
	    }
	}
    }
    foreach my $char (keys %singlesubsts){
	my $editoperation=$char;
	$char=~s/\/.+$//;
	unless($char=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
	    my $freq=$singlesubsts{$editoperation};
	    if($freq>=$threshold){
		&printWeights($char,$freq,$editoperation);
	    }
	}
    }
    foreach my $char (keys %single2doublesubsts){
	my $editoperation=$char;
	$char=~s/\/.+$//;
	unless($char=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
	    my $freq=$single2doublesubsts{$editoperation};
	    if($freq>=$threshold){
		&printWeights($char,$freq,$editoperation);
	    }
	}
    }
    foreach my $char (keys %double2singlesubsts){
	my $editoperation=$char;
	$char=~s/\/.+$//;
	unless($char=~/^[\.\,\:\;0-9\[\]\(\)\?\+\-]$/){
	    my $freq=$double2singlesubsts{$editoperation};
	    if($freq>=$threshold){
		&printWeights($char,$freq,$editoperation);
	    }
	}
    }
}


sub printWeights{
    my $char = shift @_;
    my $charfreq = shift @_;
    my $operation = shift @_;
    my $equalsfreq = 0;
    if(defined($equals{$char})){
	$equalsfreq=$equals{$char};
    }
    elsif(defined($doubleequals{$char})){
	$equalsfreq=$doubleequals{$char};
    }
    my $weight=1-($charfreq/($charfreq+$equalsfreq));
    print "$operation\t$weight\n";
}
