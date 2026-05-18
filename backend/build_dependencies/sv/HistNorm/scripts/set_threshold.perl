#!/usr/bin/perl

use strict;
use utf8;

my $inputweights=shift @ARGV;
unless(open(INPUTWEIGHTS,"<$inputweights")){
    die "Cannot open input file: $inputweights\n";
}

my $weightsum=0;
my $numberofweights=0;
my @weights;

&readWeights;
&printStatistics;

sub readWeights{
    my $count=0;
    while(<INPUTWEIGHTS>){
	chomp;
	my $line=$_;
	if($line=~/^([\d\.]+)$/){
	    my $weight=$1;
	    unless($weight==0){
		$weightsum=$weightsum+$weight;
		$numberofweights++;
		$weights[$count]=$weight;
		$count++;
	    }
	}
	else{
	    print STDERR "Unexpected format in input file: $line\n";
	}
    }
    close INPUTWEIGHTS;
}

sub printStatistics{
    my $average=$weightsum/$numberofweights;
    print STDERR "Total weight sum: $weightsum\n";
    print STDERR "Total number of weights: $numberofweights\n";
    print STDERR "Average weight: $average\n";
    my $count=0;
    my $deviation=0;
    while($weights[$count]){
	my $currentweight=$weights[$count];
	my $currentdeviation=$currentweight-$average;
	$deviation=$deviation+($currentdeviation ** 2);
	$count++;
    }
    my $standarddeviation=sqrt($deviation/$numberofweights);
    print STDERR "Standard deviation: $standarddeviation\n";
    my $threshold=$average+(1.96*$standarddeviation);
    print "$threshold\n";
}
