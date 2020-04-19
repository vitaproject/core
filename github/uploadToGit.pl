#!/usr/bin/perl -I/home/phil/perl/cpan/DataTableText/lib/ -I/home/phil/perl/cpan/GitHubCrud/lib/
#-------------------------------------------------------------------------------
# Upload all files to GitHub from my local computer
# Philip R Brenan at gmail dot com, Appa Apps Ltd Inc., 2020
#-------------------------------------------------------------------------------
use warnings FATAL => qw(all);
use strict;
use Carp;
use Data::Dump qw(dump);
use Data::Table::Text qw(:all);
use GitHub::Crud;

my $home = q(/home/phil/vita/core);                                             # Home folder
my $out  = fpd $home, qw(out);                                                  # Documentation
my $docs = fpd $home, qw(docs);                                                 # Documentation
my $perl = fpd $home, qw(github);                                               # Perl to perform upload to github
my $fileRe      = qr((docs/.*html|out/.*svg)\s*\Z)i;                            # Select the generated files

my @html = qw(.html .css);                                                      # File types we want to upload to web page
my @code = qw(.gitignore .md .py .pl .perl .txt .yml);                          # File types we want to upload to vita

my $user =  q(philiprbrenan);                                                   # Owner of web page repository
my $repo = qq($user.github.io);                                                 # Web page repository
my $docg = fpd(qw(vita));                                                       # Documentation folder in web page repository

if (1)                                                                          # Edit config file so we use SSH
 {my $file = fpf($home, qw(.git config));
  my $edit = readFile($file);
  if ($edit =~ s(url = https://github.com/) (url = git\@github.com:)gs)
   {owf($file, $edit)
   }
 }

if (1)                                                                          # Commit to vita repository
 {for my $file(searchDirectoryTreesForMatchingFiles($out, $docs))               # Remove generated files
   {if ($file =~ m($fileRe)i)
     {unlink $file;
     }
   }

  lll qx(git pull --no-edit origin master);                                     # Retrieve latest version from repo

  if (1)
   {owf(fpe($home, qw(.github control prepareForPullRequest txt)), q(AAA));     # Request preparation for pull request
   }

  my @f = searchDirectoryTreesForMatchingFiles($home, @html, @code);            # Files we want to upload
  for my $f(@f)
   {lll qx(git add $f);
   }

  my $title = q(Vita).dateTimeStampName;                                        # Name for commit

  lll qx(git commit -q -m "$title");
  lll qx(git push -u origin master);                                            # Push to GitHub via SSH
 }

if (0)                                                                          # Generate and upload documentation
 {say STDERR qx(perl ${perl}generateDocumentation.pl);                          # Generate

  my @f = searchDirectoryTreesForMatchingFiles($docs, @html);                   # Files we want to upload

  for my $s(@f)                                                                 # Upload
   {my $t = swapFilePrefix($s, $docs, $docg);
    lll $t;
    GitHub::Crud::writeFileFromFileUsingSavedToken($user, $repo, $t, $s);
   }
 }
