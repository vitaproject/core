#!/usr/bin/perl -I/home/phil/perl/cpan/GitHubCrud/lib
#-------------------------------------------------------------------------------
# Upload the out folder to GitHub
# Philip R Brenan at gmail dot com, Appa Apps Ltd, 2020
#-------------------------------------------------------------------------------
use v5.16;
use warnings FATAL => qw(all);
use strict;
use Data::Dump qw(dump);
use Data::Table::Text qw(:all);
use GitHub::Crud;

my $controlFile = q(.github/control/prepareForPullRequest.txt);                 # The file whose presence triggers this action

my ($userRepo, $user, $repo, $token);

if (@ARGV == 2)                                                                 # Called from GitHub
 {($userRepo, $token) = map {$_ // ''} @ARGV;
  ($user, $repo)      = split m(/), $userRepo, 2;
 }
else                                                                            # Called locally
 {$user = 'philiprbrenan';
  $repo = 'core';
 }

say STDERR "Delete generated files in $user/$repo";                             # The title of the piece

my $g = GitHub::Crud::new                                                       # GitHub object
 (userid=>$user, repository=>$repo, personalAccessToken=>$token);

my @files = $g->list;                                                           # Get the names of all the files in the repository

for my $file(@files)                                                            # Delete generated files
 {if ($file =~ m((docs/.*html|out/.*svg)\Z)i)                                   # Generated files
   {lll "Delete $file";
    $g->gitFile = $file;
    $g->delete;
   }
 }

for my $file(@files)                                                            # Delete the control file so that normal operations resume on the next user push
 {if (index($file, $controlFile) >= 0)                                          # Control file
   {lll "Delete $file";
    $g->gitFile = $file;
    $g->delete;
   }
 }

=pod

cd /home/phil/vita/core/github/; pp -I /home/phil/perl/cpan/GitHubCrud/lib deleteGeneratedFiles.pl; mv a.out deleteGeneratedFiles.perl

=cut
