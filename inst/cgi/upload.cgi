#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Pretty;
$CGI::Pretty::INDENT = "";
use File::stat;
use POSIX;
use FileManager;
use Site;
use strict;

# Create the global CGI instance
our $cgi = new CGI;

# Create the global FileManager instance
our $fm = new FileManager;

my $submit = $cgi->param('submit');
my $token = $cgi->param('token') ? $cgi->param('token') : $cgi->cookie('bioctoken');
my ($status, $cookie);

# Handle initializing the FileManager session

if ($token) {

	if (! $fm->init_with_token($UPLOAD_DIR, $token)) {
		undef $fm;
		$status = "Couldn't load session from token: $token";
		$cookie = $cgi->cookie(-name=>'bioctoken', -value=>'', 
                               -expires=>'now', -path=>'/');
	}

} elsif (defined($submit) && $submit eq "Start New Session") {

	$fm->create($UPLOAD_DIR) || error("Couldn't create new session");
	
} else {
	
	undef $fm;
}

# Handle File Listing actions

if (defined($submit) && $submit eq "Delete Checked Files") {

	my @filenames = $cgi->param('files');
	if (@filenames) {
		$fm->remove(@filenames) || ($status = "Error while deleting files.");
	}
	
} elsif (defined($submit) && $submit eq "Upload File") {

	my $filename = $cgi->param('file');
	$filename =~ s/^.*[\\\/]//;
	my $fh = $cgi->upload('file');
	if (!$fh && $cgi->cgi_error) {
		$status = "Error while uploading file";
	} else {
		$fm->savefh($fh, $filename) ||
		    ($status = "Error while uploading file");
	}
} elsif (defined($submit) && $submit eq "Save Cookie") {
    $cookie = $cgi->cookie(-name=>'bioctoken', -value=>$fm->token, 
                           -expires=>'+7d', -path=>'/');
} elsif (defined($submit) && $submit eq "Forget Cookie") {
    $cookie = $cgi->cookie(-name=>'bioctoken', -value=>'', 
                           -expires=>'now', -path=>'/');
} elsif (defined($submit) && $submit eq "Show Job") {
    showjob();
} elsif (defined($submit) && $submit eq "affy") {
	affy();
} elsif (defined($submit) && $submit eq "multtest") {
	multtest();
} elsif (defined($submit) && $submit eq "annaffy") {
	annaffy();
}

if ($fm) {
    filelist($status, $cookie);
} else {
	start($status, $cookie);
}

#### Subroutine: start
# Session start screen
####
sub start {
	my ($status, $cookie) = @_;

	print $cgi->header(-cookie=>$cookie);    
	site_header("Upload Manager");
	
	print h1("Upload Manager"),
	      h2("No Current Session"),
	      $status ? p($status) : "",
	      start_form,
	      hidden('step', 1),
	      p("Enter token from a previous session:"),
	      p(textfield("token", "", 30)),
	      submit("submit", "Load Session"), ' ', submit("submit", "Start New Session"),
	      end_form;

    print <<'END';
<h2>Quick Help</h2>

<p>
The upload manager is used to input files for processing by
Bioconductor. When you start a new session, you are given a token
which allows you to return to that session and access the files
from Bioconductor tools. Once in a session, you may optionally save
that token in a web-browser cookie. The cookie will last for one
week.
</p>

<p>
You should consider the upload manager, as well as any results you
create, to be temporary storage. Files will be periodically removed
to prevent the disk from filling up. You can generally count on
files lasting for at least a week, although we do not back them up
so that may not be the case should an unexpected disk failure occur.
Please download and save any results you wish to keep for an extended
period of time. You may always re-upload exprSets or aafTables for
further processing at a later date.
</p>
END
	
	site_footer();
}

#### Subroutine: filelist
# Primary file listing screen
####
sub filelist {
	my ($status, $cookie) = @_;
	my @filenames = $fm->filenames;
	my $basepath = $fm->path;
	my ($filestat, $size, $date);

	print $cgi->header(-cookie=>$cookie);    
	site_header("Upload Manager");
	
	print h1("Upload Manager"),
	      h2("File Listing"),
	      $status ? p($status) : "",
	      start_multipart_form,
	      hidden(-name=>'token', -default=>$fm->token, -override=>1),
	      table({-cellspacing=>2, -cellpadding=>1, -style=>"background-color: #CCC"},
	            Tr(td(filefield(-name=>"file", -default=>"", -override=>1)),
	               td(submit("submit", "Upload File")))),
	      br;
	
	if (@filenames != 0) {
		
		print '<table>',
			  Tr(th(), th('File Name'), th({-colspan=>2}, 'Size (bytes)'), th({-colspan=>2}, 'Date'));
		
		for (my $i = 0; $i < @filenames; $i++) {
			$filestat = stat("$basepath/$filenames[$i]");
			$size = $filestat->size;
			$date = strftime("%a %b %e %H:%M:%S %Y", localtime($filestat->mtime));
			print Tr(td('<input type="checkbox" name="files" value="' . $filenames[$i] . '">'), 
					 td($filenames[$i]), td({-width=>25}),
					 td({-style=>"text-align: right"}, $size), td({-width=>25}),
					 td({-style=>"text-align: right"}, $date));
		}
				
		print '</table>';
	}
	
	print p(@filenames . " files");
	
	if (@filenames != 0) {
	
		print table({-cellspacing=>2, -cellpadding=>1, -style=>"background-color: #CCC"}, 
					Tr(td(submit("submit", "Refresh Listing")), 
					   td(submit(-name=>"submit", -value=>"Delete Checked Files", -onClick=>'return confirm("Really delete checked files?")')),
					   td(submit("submit", "Show Job")))),
			  br,
			  table({-cellspacing=>2, -cellpadding=>1, -style=>"background-color: #CCC"}, 
					Tr(td("Use checked files with:"), 
					   td(submit("submit", "affy")), 
					   td(submit("submit", "multtest")),
					   td(submit("submit", "annaffy")))),
			  br;
	}    
	      
	print table({-cellspacing=>2, -cellpadding=>1, -style=>"background-color: #CCC"}, 
	            Tr(td("Session Token:", $fm->token),
	               td(submit("submit", ($cookie xor $cgi->cookie(-name=>'bioctoken')) ? "Forget Cookie" : "Save Cookie")))),
	      end_form;
	
	site_footer();
}

#### Subroutine: showjob
# Show the results from the job that produced the specified file
####
sub showjob {
	my @filenames = $cgi->param('files');
	my $jobname;
	
	error("You must select a single file to show its job") if (@filenames != 1);
	
	if ($filenames[0] =~ /([a-z]{1,6}-[a-zA-Z0-9]{8})\..+/) {
		$jobname = $1;
	} else {
	    error("That file name does not have an associated job");
	}
	
	opendir(DIR, "$RESULT_DIR/$jobname") ||
	    error("The job results associated with that file no longer exist");
	closedir(DIR);
	
	print $cgi->redirect("job.cgi?name=$jobname");
}

#### Subroutine: affy
# Use checked files with affy
####
sub affy {
	my @filenames = $cgi->param('files');
	my $url = 'affy.cgi?step=1&token=' . $fm->token . '&numfiles=' . @filenames;
	
	error("You must select at least one file for affy") if (!@filenames);
	
	for (my $i = 0; $i < @filenames; $i++) {
		$url .= '&file' . $i . '=' . $filenames[$i];
	}
	
	print $cgi->redirect($url);
}

#### Subroutine: multtest
# Use checked file with multtest
####
sub multtest {
	my @filenames = $cgi->param('files');
	my $url = 'multtest.cgi?step=1&token=' . $fm->token;
	
	error("You must select only one file for multtest") if (@filenames != 1);
	
	$url .= '&file=' . $filenames[0];
	
	print $cgi->redirect($url);
}

#### Subroutine: annaffy
# Use checked file with annaffy
####
sub annaffy {
	my @filenames = $cgi->param('files');
	my $url = 'annaffy.cgi?token=' . $fm->token;
	
	error("You must select only one file for annaffy") if (@filenames != 1);
	
	$url .= '&file=' . $filenames[0];
	
	print $cgi->redirect($url);
}

#### Subroutine: error
# Print out an error message and exit
####
sub error {
    my ($error) = @_;

	print $cgi->header;    
	site_header("Upload Manager");
	
	print h1("Upload Manager"),
	      h2("Error:"),
	      p($error);
	
	site_footer();
	
	exit(1);
}
