#!/usr/bin/perl -I/home/phil/perl/cpan/GitHubCrud/lib
#-------------------------------------------------------------------------------
# Upload the out folder to GitHub
# Philip R Brenan at gmail dot com, Appa Apps Ltd, 2020
#-------------------------------------------------------------------------------
# pp -I /home/phil/perl/cpan/GitHubCrud/lib uploadOut.pl; mv a.out uploadOut.perl
use v5.16;
use warnings FATAL => qw(all);
use strict;
use GitHub::Crud;

my ($userRepo, $source, $target, $token) = map {$_ // ''} @ARGV;
my ($user, $repo) = split m(/), $userRepo, 2;
say STDERR "Upload source: $source, to: $target, length:", length($token);

if ($source and $target)                                                        # Upload named folder to GitHub
 {GitHub::Crud::writeFolderUsingSavedToken($user, $repo, $target, $source, $token);
 }
