#!/usr/bin/perl -I/home/phil/perl/cpan/GitHubCrud/lib
#-------------------------------------------------------------------------------
# Prevent generated files from complicating pull requests
# Philip R Brenan at gmail dot com, Appa Apps Ltd, 2020
#-------------------------------------------------------------------------------
use v5.16;
use warnings FATAL => qw(all);
use strict;
use Data::Dump qw(dump);
use Data::Table::Text qw(:all);
use GitHub::Crud;

my $sourceUser  = q(vitaproject);                                               # The original repository from whence we were cloned
my $sourceRepo  = q(core);
my $controlFile = q(.github/control/prepareForPullRequest.txt);                 # The file whose presence triggers this action
my $fileRe      = qr(((docs/.*html|out/.*svg)\Z)i);                             # Select the generated files

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

my $g = GitHub::Crud::new                                                       # Our github repo
 (userid=>$user, repository=>$repo, personalAccessToken=>$token);

my $G = GitHub::Crud::new                                                       # The original github repo
 (userid=>$sourceUser, repository=>$sourceRepo);

my @files = $g->list;                                                           # Get the names of all the files in our repository

for my $file(@files)                                                            # Delete generated files
 {if ($file =~ m($fileRe))
   {lll "Delete $file";
    $g->gitFile = $file;
    $g->delete;
   }
 }

my @sourceFiles = $G->list;                                                     # Get the names of all the files in the source repository

for my $file(@files)                                                            # Refresh deleted files from source repository
 {if ($file =~ m($fileRe))
   {lll "Delete $file";
    $G->gitFile = $g->gitFile = $file;
    $g->write($G->read);                                                        # Copy from source repository to our repository
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
