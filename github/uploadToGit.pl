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
my $docs = fpd($home, qw(docs));                                                # Documentation
my $perl = fpd($home, qw(github));                                              # Perl to perform upload to github
my @pp   = qw(uploadOut deleteGeneratedFiles generateDocumentation);            # Package these files so they can be used immediately on GitHub
my @ppi  = (q(-I /home/phil/perl/cpan/DataTableText/lib/),                      # Perl modules used by packaged perl files
            q(-I /home/phil/perl/cpan/GitHubCrud/lib));

my @html = qw(.html .css);                                                      # File types we want to upload to web page
my @code = qw(.gitignore .md .py .pl .perl .yml);                               # File types we want to upload to vita

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

if (0)                                                                          # Package Perl files
 {for my $pp(@pp)
   {my $p1 = fpe($perl, $pp, q(pl));
    -e $p1 or confess "No such file: $p1";
    my $p2 = fpe($perl, $pp, q(perl));
    unlink $p2;
    my $pi = join ' ', @ppi;
    my $c  = qq(pp $pi -o $p2 $p1);
    lll qq($c);
    lll qx($c);
    -e $p2 or confess "No such file: $p2";
   }
 }

if (1)                                                                          # Commit to vita repository
 {lll qx(git pull -q --no-edit origin master);                                  # Retrieve latest version from repo

  owf(fpe($home, qw(.github control prepareForPullRequest txt)), q(AAA));       # Request preparation for pull request

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
