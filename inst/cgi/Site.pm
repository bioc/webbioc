package Site;

use strict;

our @ISA = qw/Exporter/; 
our @EXPORT = qw/site_header site_footer submit_pbs
                 $UPLOAD_DIR $RESULT_DIR $RESULT_URL $R_BINARY $R_LIBS
                 $USE_FRAMES $DEBUG $SH_HEADER $USE_PBS $PBS_OPTIONS/;

# Upload repository directory
our $UPLOAD_DIR = "/Library/WebServer/CGI-Executables/biocuploads";

# Job results directory & web accessible URL
our $RESULT_DIR = "/Library/WebServer/Documents/bioc";
our $RESULT_URL = "/bioc";

# Location of R binary & R libraries
our $R_BINARY = "/sw/bin/R";
our $R_LIBS = "";

# Use frames for showing results
our $USE_FRAMES = 1;

# Turn on debugging output
our $DEBUG = 1;

# Append commands to the top of shell scripts (environment variables, etc.)
our $SH_HEADER = <<'END';
export PATH=$PATH:/usr/local/bin:/sw/bin
END

# PBS Settings
our $USE_PBS = 0;
our $PBS_OPTIONS = <<END;
#PBS  -q feed\@gretel
#PBS  -l cput=0:30:00,nodes=1
END

#### Subroutine: site_header
# Print out leading HTML
####
sub site_header {
    my ($title) = @_;
    
    print <<END;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">

<html>

<head>
<title>$title</title>
</head>

<body>
<div style="text-align: center">
<a href="affy.cgi" target="_top">affy</a> |
<a href="multtest.cgi" target="_top">multtest</a> |
<a href="annaffy.cgi" target="_top">annaffy</a> |
<a href="annaffysearch.cgi" target="_top">annaffy search</a> |
<a href="upload.cgi" target="_top">Upload Manager</a> |
<a href="log.cgi" target="_top">Log</a>
</div>
END
}

#### Subroutine: site_footer
# Print out lagging HTML
####
sub site_footer {
    
    print <<END;
</body>
</html>
END
}

#### Subroutine: submit_pbs
# Submit a job to PBS
####
sub submit_pbs {
	my ($pbsfile) = @_;
	
	$ENV{'PBS_HOME'} = "/PBS";
	$ENV{'PBS_EXEC'} = "/PBS";
	$ENV{'PBS_SERVER'} = "gretel";
	
	system("/PBS/bin/qsub $pbsfile");
}

1;
