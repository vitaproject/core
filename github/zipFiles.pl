#!/usr/bin/perl -I/home/phil/perl/cpan/DataTableText/lib/
#-------------------------------------------------------------------------------
# Zip vita files
# Philip R Brenan at gmail dot com, Appa Apps Ltd Inc., 2020
#-------------------------------------------------------------------------------
use warnings FATAL => qw(all);
use strict;
use Carp;
use Data::Dump qw(dump);
use Data::Table::Text qw(:all);

my $home = q(/home/phil/vita/minimum/);
my $zip  = q(minimalVita.zip);

say STDERR qx(cd $home; rm $zip; zip -r $zip * --exclude ".git*"; ls -la *.zip)
