#!/usr/bin/perl -I/home/phil/perl/cpan/DataTableText/lib/ -I/home/phil/perl/cpan/GitHubCrud/lib/
#-------------------------------------------------------------------------------
# Generate documentation from Python modules
# Philip R Brenan at gmail dot com, Appa Apps Ltd Inc., 2020
#-------------------------------------------------------------------------------
use warnings FATAL => qw(all);
use strict;
use Carp;
use Data::Dump qw(dump);
use Data::Table::Text qw(:all);
use GitHub::Crud;

my $local   = !$ENV{CI};                                                        # Local run not on GitHub
my $home    = $local ? q(/home/phil/vita/core/) : q(.);                         # Home folder
my $modules = fpd($home, qw(vita modules));                                     # Modules folder
my $docs    = fpd($home, q(docs));                                              # Output documentation

my $user =  q(philiprbrenan);                                                   # Owner of web page repository
my $repo = qq($user.github.io);                                                 # Web page repository
my $docg = fpd(qw(vita));                                                       # Documentation folder in web page repository

my @errors;                                                                     # Record missing documentation and tests

makePath($docs);                                                                # Create and clear the output folder
clearFolder($docs, 999);

my @files =                                                                     # Files to extract documentation from
  sort {fn($a) cmp fn($b)}                                                      # Sort by file name
  grep {!m/__init__/}                                                           # Ignore init files
  searchDirectoryTreesForMatchingFiles($modules, qw(.py));                      # Modules to document

for my $source(@files)                                                          # Document each module
 {say STDERR $source;
  my $target = fpe($docs, fn($source), q(html));
  my $r = extractPythonDocumentation($source, $target);
  push @errors, $r->errors->@*;
 }

if (1)                                                                          # Create an index file
 {my @h;
  for my $source(@files)                                                        # Link to the documentation for each module
   {my $f = fpe(fn($source), q(html));
    push @h, qq(<p><a href="$f">$f</a></p>)
   }

  my $h = join "\n", @h, map {qq(<p>$_</p>)} @errors;                           # Add error listing

  owf(fpe($docs, qw(index html)), <<END);
<html>
<meta charset="utf-8"/>
<style></style>
<body>
$h
</body>
</html>
END
 }

if ($local)                                                                     # Upload documentation to philiprbrenan.github.io/vita/index.html
 {my @f = searchDirectoryTreesForMatchingFiles($docs, q(.html));                # Files we want to upload
  for my $s(@f)
   {my $t = swapFilePrefix($s, $docs, $docg);
    lll $t;
    GitHub::Crud::writeFileFromFileUsingSavedToken($user, $repo, $t, $s);
   }
 }


=pod

cd /home/phil/vita/core/github/; pp -I /home/phil/perl/cpan/DataTableText/lib -I /home/phil/perl/cpan/GitHubCrud/lib generateDocumentation.pl; mv a.out generateDocumentation.perl

=cut

