#!/usr/bin/env perl

use strict;
use warnings;
use Data::Dumper;
use CGI;
use LWP::UserAgent;
use File::Basename;

print "Content-type: application/json;\n";
print "\n";

## UserAgent Settings
##
my $ua = LWP::UserAgent->new;
$ua -> timeout(10);
$ua -> env_proxy;

my $query = new CGI;
my $param = $query->upload('photo-path');
my $format = $query->param('output-format');
my $data = $query->Vars;


unless($param){
    print qq'{"success":false, "description":"Input file is empty!!"}';
    exit;
}

my $basename = basename $param;

unless($basename =~/.pdf$/){
    print qq'{"success":false, "description":"Available for PDF format only!!"}';
    exit;
}


my $ID = ((time % 1296000) * 10 + int(rand(10)) + 1048576);

open my $out,'>',"./data/$ID.pdf";

my $pdf;
while( <$param>){
    $pdf .= $_;
}
print $out $pdf;

system("/usr/local/bin/pdftotext ./data/$ID.pdf ./data/$ID.txt");
close $out;
sleep(1);

    
my $doi;
open my $file,'<', "./data/$ID.txt" or die $!;
while(<$file>){
    my $line = $_;
    chomp($line);

    if ($line =~ /doi\:(.*)/i or $line =~ /doi(.*)/i){
        $doi = trim($1);
        last;
    }
}

unless($doi){
    print qq'{"success":false, "description":"Not found Digital object identifier(DOI) in PDF file"}';
    exit;
    die $!;
}

## Get from Esearch
my @htmldata;
my $response = $ua->get("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=$doi");

($response->is_success)?@htmldata = split /\n/, $response->decoded_content:die $response->status_line;


my $pmid;
$, = "\n";

for my $line(@htmldata){

    if($line =~/\<Id\>([^<]+)/){
        $pmid = trim($1);
        last;
    }
}
unless ($pmid){
    print qq'{"success":false, "description":"Not found Pubmed ID(PMID) in PDF file"}';
    exit;
}


@htmldata = ();

$response = $ua->get("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=$pmid&format=xml");

($response->is_success)?@htmldata = split /\n/, $response->decoded_content:die $response->status_line;
my (@last_authors, @first_authors, $year, $title, $volume, $page, @journal);
my ($authors_f, $year_f, $title_f, $volume_f, $page_f, $journal_f) = (0, 0, 0, 0, 0, 0);

for my $line (@htmldata){

    #Year
    if($line=~/\<PubDate\>/){
        $year_f = 1;
        next;
    }
    if($year_f == 1){
        if($line=~/\<Year\>(\d+)/){
          $year = trim($1);
        }
        $year_f = 0;
        next;
    }

    #Article Title
    if($line=~/\<ArticleTitle\>([^<]+)/){
        $title =  trim($1);
        next;
    }


    #page
    if($line=~/\<Pagination\>/){
        $page_f = 1;
        next;
    }
    if($page_f == 1){
        if($line =~ /\<MedlinePgn\>([^<]+)/){
            $page =  trim($1);
            $page_f = 0;
            next;
        }
    }

    #journal
    
    if($line=~/\<Title\>([^<]+)/){
        $journal_f = 1;
        push @journal, trim($1);
        next;
    }
    if($journal_f == 1){
        if($line=~/\<ISOAbbreviation\>([^<]+)/){
            push @journal, trim($1);
            $journal_f = 0;
            next;
        }
    }

    #volume

    if($line=~/\<Volume\>([^<]+)/){
        $volume = trim($1);
        next;
    }

    #author

    if($line=~/\<Author /){
        $authors_f = 1;
        next;
    }
    if($authors_f == 1){
        if($line=~/\<LastName\>([^<]+)/){
            push @last_authors, trim($1);

        }elsif($line=~/\<Initials\>([^<]+)/){
            push @first_authors, trim($1);
            
        }
    }elsif($authors_f == 1 && $line =~/\<\/AuthorList\>/){
        $authors_f = 0;
    }
}

##
sleep(1);

my $Reference;
if($format eq 'bioinformatics'){
    if (scalar @last_authors <= 3){
        my $author;
        for(my $i=0;$i<scalar(@last_authors);$i++){
            $author .= $last_authors[$i] .', '.$first_authors[$i]. '. ';
            unless($i == (scalar(@last_authors) - 1)){
                $author .= 'and ';
            }
        }
        $Reference .= $author . '('. $year.') ' . $title .' <i>'. $journal[1].'</i>, '.'<b>'.$volume.'</b>'.', '.$page.'.';
    }else{
        $Reference .= $last_authors[0].', '.$first_authors[0].'. <i>et al</i> (' .$year.') ' . $title .' <i>'. $journal[1].'</i>, '.'<b>'.$volume.'</b>'.', '.$page.'.';
    }
    
}elsif($format eq 'nucleic_acids_research'){
    if (scalar @last_authors <= 3){
        my $author;
        for(my $i=0;$i<scalar(@last_authors);$i++){
            $author .= $last_authors[$i] .', '.$first_authors[$i]. '. ';
            unless($i == (scalar(@last_authors) - 1)){
                $author .= 'and ';
            }
        }
        $Reference .= $author . '('. $year.') ' . $title .' <i>'. $journal[1].'</i>, '.'<b>'.$volume.'</b>'.', '.$page.'.';
    }else{
        $Reference .= $last_authors[0].', '.$first_authors[0].'. <i>et al</i> (' .$year.') ' . $title .' <i>'. $journal[1].'</i>, '.'<b>'.$volume.'</b>'.', '.$page.'.';
    }
    
  
}elsif($format eq 'bibtex'){
    $Reference = '@article{'. "$last_authors[0]_$first_authors[0],<br>";
    my $author;
    for(my $i=0;$i<scalar(@last_authors);$i++){
        $author .= $last_authors[$i] .', '.$first_authors[$i]. '. ';
        unless($i == (scalar(@last_authors) - 1)){
            $author .= 'and ';
        }
    }
    $Reference .= '<br>';
    $Reference .= 'author={'.$author.'},<br>';
    $Reference .= "year={$year},<br>";
    $Reference .= "title={$title},<br>";
    $Reference .= "volume={$volume},<br>";
    $Reference .= "pages={$page},<br>";
    $Reference .= "journal={$journal[0]}<br>";
    $Reference .= "}";
    
}

print qq'{"success":true,"fileName":"$Reference", "fileSize":"hoge2", "Reference":"$Reference"}';
    
sub trim {
	my $val = shift;
	$val =~ s/^\s*(.*?)\s*$/$1/;
	return $val;
}
