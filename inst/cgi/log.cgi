#!/usr/bin/perl -w -I/sw/lib/perl5/5.6.0/darwin

use CGI qw/:standard/;
use CGI::Pretty;
$CGI::Pretty::INDENT = "";
use POSIX;
use FileManager;
use BioC;
use Site;
use strict;

# Create the global CGI instance
our $cgi = new CGI;

# Create the global FileManager instance
our $fm = new FileManager;

# Handle initializing the FileManager session
if ($cgi->param('token') || $cgi->cookie('bioctoken')) {
    my $token = $cgi->param('token') ? $cgi->param('token') : 
                                       $cgi->cookie('bioctoken');
	if ($fm->init_with_token($UPLOAD_DIR, $token)) {
	    error('Upload session has no files') if !($fm->filenames > 0);
	} else {
	    error("Couldn't load session from token: ". $cgi->param('token')) if
	        $cgi->param('token');
	}
}

if ($fm->token) {
    log_list();
} else {
    form();
}

#### Subroutine: form
# Make upload token form
####
sub form {

	print $cgi->header;    
	site_header('Job Log');
	
	print h1('Job Log'),
	      start_form,
	      p('Enter upload manager token:'),
	      p(textfield('token', $fm->token, 30)),
	      submit("Show Log"),
	      end_form;

    print <<'END';
<h2>Quick Help</h2>

<p>
If you have a valid Upload Manager token, Bioconductor will keep
a log of all the jobs you submit. Additionally, if you store your
token in a cookie (use the button at the bottom of the Upload
Manager), Bioconductor will also log any annaffy searches you do.
Jobs are listed in reverse chronological order.
</p>
END
	
	site_footer();
}

#### Subroutine: log_list
# Print out the log
####
sub log_list {
	my $path = $fm->path;
	my (@loglines, $jobname, $title, $date);
	
	if (open(LOG, "$path/.log")) {
		@loglines = <LOG>;
		close(LOG);
	}
	
	print $cgi->header;    
	site_header('Job Log');
	
	print h1('Job Log');
	
	if (@loglines) {
	    print '<table>',
			  Tr(th('Job Name'), th({-colspan=>2}, 'Title'), th({-colspan=>2}, 'Date'));
			  
	    for (my $i = @loglines - 1; $i >= 0; $i--) {
			($jobname, $title, $date) = split(/\t/, $loglines[$i]);
			$date = strftime("%a %b %e %H:%M:%S %Y", localtime($date));
			print Tr(td("<a href=\"job.cgi?name=$jobname\">$jobname</a>"), td({-width=>25}),
					 td({-style=>"text-align: right"}, $title), td({-width=>25}),
					 td({-style=>"text-align: right"}, $date));
		}
			  
	    print '</table>';
	} else {
		print "No log entries";
	}
	
	site_footer();
}

#### Subroutine: error
# Print out an error message and exit
####
sub error {
    my ($error) = @_;

	print $cgi->header;    
	site_header("Job Log");
	
	print h1("Job Log"),
	      h2("Error:"),
	      p($error);
	
	site_footer();
	
	exit(1);
}
