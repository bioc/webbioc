package Site;

use strict;

our @ISA = qw/Exporter/;
our @EXPORT = qw/site_header site_footer
                 $UPLOAD_DIR $RESULT_DIR $RESULT_URL $BIOC_URL $SITE_URL 
                 $ADMIN_EMAIL $R_BINARY $R_LIBS $USE_FRAMES $DEBUG 
                 $SH_HEADER $BATCH_SYSTEM %BATCH_ENV $BATCH_BIN $BATCH_ARG/;

# Upload repository directory
our $UPLOAD_DIR = "/path/to/biocuploads";

# Job results directory & web accessible URL
our $RESULT_DIR = "/path/to/delivery";
our $RESULT_URL = "/delivery";

# cgi-bin URL and site URL
our $BIOC_URL = "/path/to/cgi-bin/bioconductor";
our $SITE_URL = "http://www.domain.org";

# Admin e-mail
our $ADMIN_EMAIL = 'admin@domain.org';

# Location of R binary & R libraries
our $R_BINARY = "/usr/local/bin/R";
our $R_LIBS = "/path/to/lib/bioconductor";

# Use frames for showing results
our $USE_FRAMES = 1;

# Turn on debugging output
our $DEBUG = 1;

# Append commands to the top of shell scripts (environment variables, etc.)
our $SH_HEADER = <<'END';
export PATH=$PATH:/usr/sbin:/usr/local/bin
END

# Batch system to use (fork, sge, pbs)
our $BATCH_SYSTEM = "fork";

# Batch system environment variables
our %BATCH_ENV = (SGE_ROOT => "/path/to/sge");

# Batch system binary directory
our $BATCH_BIN = "/path/to/sge/bin/architecture";

# Batch system additional job submission arguments
our $BATCH_ARG = "";

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

1;
