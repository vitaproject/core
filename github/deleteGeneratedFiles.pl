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
my $fileRe      = qr((docs/.*html|out/.*svg)\s*\Z)i;                          # Select the generated files

my ($userRepo, $user, $repo, $token);

if (@ARGV == 2)                                                                 # Called from GitHub
 {($userRepo, $token) = map {$_ // ''} @ARGV;
  ($user, $repo)      = split m(/), $userRepo, 2;
 }
else                                                                            # Called locally
 {$user = 'philiprbrenan';
  $repo = 'core';
 }

say STDERR "Delete and refresh generated files in $user/$repo";                 # The title of the piece

my $g = GitHub::Crud::new                                                       # Our github repo
 (userid=>$user, repository=>$repo, personalAccessToken=>$token);

my $G = GitHub::Crud::new                                                       # The original github repo
 (userid=>$sourceUser, repository=>$sourceRepo, personalAccessToken=>$token);

if (1)                                                                          # Delete generated files
 {for my $file($g->list)
   {if ($file =~ m($fileRe))
     {lll "Delete $file";
      $g->gitFile = $file;
      $g->delete;
     }
   }
 }

if (1)                                                                          # Refresh deleted files from source repository
 {for my $file($G->list)
   {if ($file =~ m($fileRe))
     {lll "Refresh $file";
      $G->gitFile = $g->gitFile = $file;
      $g->write($G->read);                                                        # Copy from source repository to our repository
     }
   }
 }

$g->gitFile = q(.github/control/prepareForPullRequest.txt);                     # Remove control file
$g->delete;

=pod

cd /home/phil/vita/core/github/; pp -I /home/phil/perl/cpan/GitHubCrud/lib deleteGeneratedFiles.pl; mv a.out deleteGeneratedFiles.perl

=cut
