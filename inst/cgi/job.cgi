#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Pretty;
$CGI::Pretty::INDENT = "";
use BioC;
use Site;
use strict;

# Create the global CGI instance
our $cgi = new CGI;

if ($cgi->param('name')) {
    showjob();
} elsif ($cgi->param('topframe')) {
    topframe();
} else {
    form();
}

#### Subroutine: form
# Print the show job results form
####
sub form {

    print $cgi->header;    
	site_header("Job Results Lookup");
	
	print h1("Job Results Lookup"),
	      start_form(-method=>'GET'),
	      p("Enter the job name:"),
	      p(textfield("name", "", 30)),
	      submit("submit", "Show Job Results"),
	      end_form;

    print <<'END';
<h2>Quick Help</h2>

<p>
Job results are only kept temporarily on the server. Results are
generally retained for at least a week before being automatically
deleted. Please download any results you wish to save for an extended
period of time.
</p>
END
	
	site_footer();
}

#### Subroutine: showjob
# Show job results
####
sub showjob {

	my $jobname = $cgi->param('name');
	$jobname =~ s/^\s|\s$//g;
	
	grep(/[a-z]{1,6}-[a-zA-Z0-9]{8}/, $jobname) ||
		error("Invalid job name");
	
	opendir(DIR, "$RESULT_DIR/$jobname") ||
	    error("The results for that job name no longer exist");
	closedir(DIR);
	
	if ($USE_FRAMES) {
	    print $cgi->header;
	    print <<END;
<html>
<head>
<title>Job Results</title>
<frameset rows="35,*" frameborder=0 framespacing=0 border=0>
<frame name="header" src="job.cgi?topframe=1" scrolling="NO" noresize>
<frame name="content" src="$RESULT_URL/$jobname/" scrolling="AUTO" noresize>
</frameset>
</head>
</html>
END
	} else {
	    print $cgi->redirect("$RESULT_URL/$jobname/");
	}
}

#### Subroutine: topframe
# Print the top frame for use in the frameset
####
sub topframe {

    print $cgi->header;    
	print <<'END';
<html>
<body>
<div style="text-align: center">
<a href="affy.cgi" target="_top">affy</a> |
<a href="multtest.cgi" target="_top">multtest</a> |
<a href="annaffy.cgi" target="_top">annaffy</a> |
<a href="annaffysearch.cgi" target="_top">annaffy search</a> |
<a href="upload.cgi" target="_top">Upload Manager</a> |
<a href="log.cgi" target="_top">Log</a>
</div>
</body>
</html> 
END
}

#### Subroutine: error
# Print out an error message and exit
####
sub error {
    my ($error) = @_;

	print $cgi->header;    
	site_header("Job Results Lookup");
	
	print h1("Job Results Lookup"),
	      h2("Error:"),
	      p($error);
	
	site_footer();
	
	exit(1);
}
