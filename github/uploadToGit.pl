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
my @pp   = qw(uploadOut deleteGenerateFiles generateDocumentation);             # Package these files so they can be used immediately on GitHub
my @ppi  = (q(-I /home/phil/perl/cpan/DataTableText/lib/),                      # Perl modules used by packaged perl files
            q(-I /home/phil/perl/cpan/GitHubCrud/lib));

my @html = qw(.html .css);                                                      # File types we want to upload to web page
my @code = qw(.gitignore .py .pl .perl .yml);                                   # File types we want to upload to vita

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

if (1)                                                                          # Package Perl files
 {for my $pp(@pp)
   {my $p1 = fpe($perl, $pp, q(pl));
    my $pa = fpe($perl, qw(a out));
    my $p2 = fpe($perl, $pp, q(perl));
    my $pi = join ' ', @ppi;
    lll qx(pp $pi $p1; mv $pa $p2);
   }
 }

if (1)                                                                          # Commit to vita repository
 {lll qx(git pull origin master);                                               # Retrieve latest status

  my @f = searchDirectoryTreesForMatchingFiles($home, @html, @code);            # Files we want to upload
  lll "Files:\n", dump([@f]);
  for my $f(@f)
   {lll qx(git add $f);
   }

  my $title = q(Vita).dateTimeStampName;                                        # Name for commit

  lll qx(git commit -m "$title");
  lll qx(git push -u origin master);                                            # Push to GitHub via SSH
 }

if (1)                                                                          # Upload documentation
 {my @f = searchDirectoryTreesForMatchingFiles($docs, @html);                   # Files we want to upload
  for my $s(@f)
   {my $t = swapFilePrefix($s, $docs, $docg);
    lll $t;
    GitHub::Crud::writeFileFromFileUsingSavedToken($user, $repo, $t, $s);
   }
 }
