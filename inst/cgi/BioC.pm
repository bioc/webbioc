package BioC;

use FileManager;
use POSIX;
use Digest::MD5 qw/md5_base64/;
use IPC::Open3;
use Site;
use strict;

our @ISA = qw/Exporter/; 
our @EXPORT = qw/rand_token check_email jobsummary create_files start_job 
                 log_job parse_exprSet parse_aafTable/;

#### Subroutine: rand_token
# Generate a random token 8 characters long
####
sub rand_token {
	my $token = md5_base64(time * $$);
	$token =~ s/[+\/=]//g;
	return substr($token, 0, 8);
}

#### Subroutine: check_email
# Checks if e-mail address of user is a valid one. Returns 1 if valid.
####
sub check_email {
    my ($address) = @_;
    my $host;

	# More strict test, doesn't allow whitespace
	grep(/^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*\@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*$/, $address) ||
		return 0;
	
	# check that host in email address is ok
	$address =~ /([^\@]*)\@(.*)/;               # extract user and host names
	$host = $2;
	
	return 1;
}

#### Subroutine: jobsummary
# Creates the job summary table using pairs of arguments
####
sub jobsummary {
	my @args = @_;
	my $jobsummary = <<END;
<h3>Job Summary:</h3>
<table border="0" cellpadding="3" cellspacing="3">	
END
	
	for (my $i = 0; $i < @args; $i += 2) {
		$jobsummary .= '<tr><td align="right" valign="top">';
		$jobsummary .= $args[$i];
		$jobsummary .= '</td><td bgcolor="#CCCCCC">';
		$jobsummary .= defined($args[$i+1]) ? $args[$i+1] : "";
		$jobsummary .= "</td></tr>\n";
	}
	
	$jobsummary .= <<END;
</table>
END
	
}

#### Subroutine: create_files
# Creates the directory and files for running the job
####
sub create_files {
    my ($jobname, $script, $output, $jobsummary, $refresh, $title, $email) = @_;
    my $pbs;
    
    # Create job directory
    mkdir("$RESULT_DIR/$jobname", 0700) || 
		return("Couldn't create result directory.");
	
	# Create R script file
	open(SCRIPT, ">$RESULT_DIR/$jobname/$jobname.R") ||
		return("Couldn't create R script file.");
	print SCRIPT $script;
	close(SCRIPT);
	
	# Create PBS file
	$pbs = generate_pbs($jobname, $email);
	open(PBS, ">$RESULT_DIR/$jobname/$jobname.pbs") ||
		return("Couldn't create PBS file.");
	print PBS $pbs;
	close(PBS);
	
    # Create processing index file
	open(INDEX, ">$RESULT_DIR/$jobname/index.html") ||
		return("Couldn't create HTML file.");
	print INDEX <<END;
<html>
<head>
<title>$title - Processing</title>
<meta http-equiv="refresh" content="$refresh">
<meta http-equiv="pragma" content="no-cache">
<meta http-equiv="expires" content="-1">
</head>
<body bgcolor="#FFFFFF">
<h3>Processing...</h3>
<p><a href="$RESULT_URL/$jobname/">Click here</a> to manually refresh.</p>
$jobsummary
</body>
</html>
END
	close(INDEX);
	
	# Create results index file
	open(INDEXRESULT, ">$RESULT_DIR/$jobname/indexresult.html") ||
		return("Couldn't create HTML file.");
	print INDEXRESULT <<END;
<html>
<head>
<title>$title</title>
</head>
<body bgcolor="#FFFFFF">
$output
<h3>Output Archive:</h3>
<a href="$jobname.tar.gz">$jobname.tar.gz</a><br>
$jobsummary
</body>
</html>
END
	close(INDEXRESULT);
	
	# Create error index file
	open(INDEXERROR, ">$RESULT_DIR/$jobname/indexerror.html") ||
		return("Couldn't create HTML file.");
	print INDEXERROR <<END;
<html>
<head>
<title>$title - Error</title>
</head>
<body bgcolor="#FFFFFF">
<h3>Error:</h3>
<p>An error occured while processing the job. Please check the
input and try again. If the problem persists, please contact the
site administrator.</p>
<p><a href="$RESULT_URL/$jobname/$jobname.err">Click here</a> to see the error.</p>
$jobsummary
</body>
</html>
END
	close(INDEXERROR);
    
	return undef;
}

#### Subroutine: generate_pbs
# Generate the PBS script to run R
####
sub generate_pbs {
	my ($jobname, $email) = @_;
	my $pbs;
	
	$pbs = <<END;
#!/bin/sh

$PBS_OPTIONS
#PBS  -N $jobname
#PBS  -S /bin/sh
#PBS  -j oe
END

	$pbs .= $email ? <<END : "";
#PBS  -m e
#PBS  -M $email
END
	
	$pbs .= $DEBUG ? <<END1 : <<END2;
#PBS  -o $RESULT_DIR/$jobname/$jobname.out
END1
#PBS  -k n
END2

	$pbs .= <<END;
$SH_HEADER
R_LIBS=$R_LIBS
export R_LIBS
$R_BINARY --no-save < $RESULT_DIR/$jobname/$jobname.R 2> $RESULT_DIR/$jobname/$jobname.err
STATUS=\$?
if ([[ \$STATUS == 0 ]]) then
  if ([[ -n `find $RESULT_DIR/$jobname -name '*.png'` ]]) then
    for i in $RESULT_DIR/$jobname/*.png; do
      pngtopnm \$i | pnmscale -r 4 | pnmtopng > \$i.tmp
      mv \$i.tmp \$i
    done
  fi
  mv $RESULT_DIR/$jobname/indexresult.html $RESULT_DIR/$jobname/index.html
  touch $RESULT_DIR/$jobname/index.html
END

    $pbs .= $DEBUG ? "" : <<END;
  rm $RESULT_DIR/$jobname/$jobname.R
  rm $RESULT_DIR/$jobname/$jobname.err
  rm $RESULT_DIR/$jobname/indexerror.html
END

    $pbs .= <<END;
  tar -czf /tmp/$jobname.tar.gz -C $RESULT_DIR $jobname
  mv /tmp/$jobname.tar.gz $RESULT_DIR/$jobname/ 
else 
  mv $RESULT_DIR/$jobname/indexerror.html $RESULT_DIR/$jobname/index.html
  touch $RESULT_DIR/$jobname/index.html
  rm $RESULT_DIR/$jobname/indexresult.html
fi
exit \$STATUS
END
}

#### Subroutine: start_job
# Starts the job described by $jobname.pbs in $jobdir. Returns 1 on success.
####
sub start_job {
	my ($jobname, $jobdir) = @_;
	my $pid;
	
	if (!($pid = fork)) {
    	# Child process
        if (!defined $pid) {
            # Fork didn't work
		    return 0;
		}
		close STDOUT;
		
		if ($USE_PBS) {
			open(STDOUT, $DEBUG ? ">$jobdir/$jobname.job" : ">/dev/null");
			submit_pbs("$jobdir/$jobname.pbs");
		} else {
        	system("/bin/sh $jobdir/$jobname.pbs " . ($DEBUG ? "> $jobdir/$jobname.out" : "> /dev/null"));
        }
        if (!$DEBUG) {
            unlink("$jobdir/$jobname.pbs");
        }
        exit(0);
    }
    
    return 1;
}

#### Subroutine: log_job
# Log a job in a special file in the file manager. Returns a textual error
# message on failure.
####
sub log_job {
	my ($jobname, $title, $fm) = @_;
	my $path = $fm->path;
	my $time = time();
	
	return undef if (! $fm || ! $fm->path);
	
	open(LOG, ">>$path/.log") ||
	    return("Couldn't write to log file");
	print LOG "$jobname\t$title\t$time\n";
	close(LOG);
	
	return undef;
}

#### Subroutine: parse_exprSet
# Parses exprSet properties out of an R data file
####
sub parse_exprSet {
	my ($filename, $name, $sampleNames, $geneNames, $annotation) = @_;
	my ($pid, $rdrfh, $wtrfh);
	my $error = "Unexpected error during parse. R not available?";
	
	$pid = open3($wtrfh, $rdrfh, 0, $R_BINARY, '--no-save', '--quiet') ||
	    return("Couldn't start R.");
	
	print $wtrfh <<'END';
parseExprSet <- function(filename) {
	if (!file.exists(filename))
		stop("File does not exist")
	name <- load(filename)
	if (length(name) != 1)
		stop("Wrong number of objects in file")
	expr <- get(name)
	if (class(expr) != "exprSet")
		stop("Invalid object class")
	cat("\nname: ", name, "\n", sep = "")

	samples <- colnames(attributes(expr)$exprs)
	if (is.null(samples))
		stop("No sample names")
	samples <- paste(samples, collapse = "\t")
	cat("\nsampleNames: ", samples, "\n", sep = "")

	genes <- row.names(attributes(expr)$exprs)
	if (is.null(genes))
		stop("No gene names")
	genes <- paste(genes, collapse = "\t")
	cat("\ngeneNames: ", genes, "\n", sep = "")

	cat("\nannotation: ", attributes(expr)$annotation, "\n", sep = "")
	cat("Parse Done\n")
}
END
	
	print { $wtrfh } "parseExprSet(\"$filename\")\n";
	
	while (<$rdrfh>) {
		if (/^(Error.*)/) {
			$error = read_error($rdrfh, $1);
			last;
		} elsif ($name && /^name: (.*)/) {
			$$name = $1;
		} elsif ($sampleNames && /^sampleNames: (.*)/) {
			@$sampleNames = split(/\t/, $1);
		} elsif ($geneNames && /^geneNames: (.*)/) {
			@$geneNames = split(/\t/, $1);
		} elsif ($annotation && /^annotation: (.*)/) {
			$$annotation = $1;
		} elsif (/^Parse Done/) {
			undef $error;
			last;
		}
	}
	
	print { $wtrfh } "\nq()\n";
	
	close($rdrfh);
	close($wtrfh);
	
	return $error;
}



#### Subroutine: parse_aafTable
# Parses aafTable properties out of an R data file
####
sub parse_aafTable {
	my ($filename, $name, $colnames, $colclasses, $probeids, $numrows) = @_;
	my ($pid, $rdrfh, $wtrfh);
	my $error = "Unexpected error during parse. R not available?";
	
	$pid = open3($wtrfh, $rdrfh, 0, $R_BINARY, '--no-save', '--quiet') ||
	    return("Couldn't start R.");
	
	print $wtrfh <<'END';
parseAafTable <- function(filename) {
	if (!file.exists(filename))
		stop("File does not exist")
	name <- load(filename)
	if (length(name) != 1)
		stop("Wrong number of objects in file")
	aaftable <- get(name)
	if (class(aaftable) != "aafTable")
		stop("Invalid object class")
	cat("\nname: ", name, "\n", sep = "")

	colnames <- names(attributes(aaftable)$table)
	if (is.null(colnames))
		stop("No column names")
	colnames <- paste(colnames, collapse = "\t")
	cat("\ncolnames: ", colnames, "\n", sep = "")
	
	colclasses <- character(length(attributes(aaftable)$table))
	for (i in 1:length(colclasses))
	    colclasses[i] <- class(attributes(aaftable)$table[[i]][[1]])
	colclasses <- paste(colclasses, collapse = "\t")
	cat("\ncolclasses: ", colclasses, "\n", sep = "")

	probeids <- attributes(aaftable)$probeids
	probeids <- paste(probeids, collapse = "\t")
	cat("\nprobeids: ", probeids, "\n", sep = "")

	numrows <- length(attributes(aaftable)$table[[1]])
	cat("\nnumrows: ", numrows, "\n", sep = "")
	cat("Parse Done\n")
}
END
	
	print { $wtrfh } "parseAafTable(\"$filename\")\n";
	
	while (<$rdrfh>) {
		if (/^(Error.*)/) {
			$error = read_error($rdrfh, $1);
			last;
		} elsif ($name && /^name: (.*)/) {
			$$name = $1;
		} elsif ($colnames && /^colnames: (.*)/) {
			@$colnames = split(/\t/, $1);
		} elsif ($colclasses && /^colclasses: (.*)/) {
			@$colclasses = split(/\t/, $1);
		} elsif ($probeids && /^probeids: (.*)/) {
			@$probeids = split(/\t/, $1);
		} elsif ($numrows && /^numrows: (.*)/) {
			$$numrows = $1;
		} elsif (/^Parse Done/) {
		    undef $error;
			last;
		}
	}
	
	print { $wtrfh } "\nq()\n";
	
	close($rdrfh);
	close($wtrfh);
	
	undef @$probeids if ($probeids && @$probeids && $$probeids[1] eq "");
	
	return $error;
}

#### Subroutine: read_error
# Finishes reading an R error out of a filehandle
####
sub read_error {
	my ($fh, $error) = @_;
	
	while (<$fh>) {
		last if (/Execution halted/);
		$error .= $_;
	}
	
	$error =~ s/Error.*:\s*//s;
	chomp($error);
	
	return $error;
}
