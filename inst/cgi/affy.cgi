#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Pretty;
$CGI::Pretty::INDENT = "";
use FileManager;
use Batch;
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

if (! $cgi->param('step')) {
    step1();
} elsif ($cgi->param('step') == 1) {
    step2();
} elsif ($cgi->param('step') == 2) {
    step3();
} else {
    error('There was an error in form input.');
}

#### Subroutine: step1
# Make step 1 form
####
sub step1 {

	print $cgi->header;    
	site_header('Affymetrix Expression Analysis: affy');
	
	print h1('Affymetrix Expression Analysis: affy'),
	      h2('Step 1:'),
	      start_form,
	      hidden('step', 1),
	      p('Enter upload manager token:', textfield('token', $fm->token, 30)),
	      p('Enter number of CEL files:', textfield('numfiles', '', 10)),
	      submit("Next Step"),
	      end_form,
	      p(a({-href=>"upload.cgi"}, "Go to Upload Manager"));

    print <<'END';
<h2>Quick Help</h2>

<p>
affy performs low-level analysis of Affymetrix data and calculates
expression summaries for each of the probe sets. It processes the
data in three main stages: background correction, normalization,
and summarization. There are a number of different methods that
can be used for each of those stages. affy can also be configured
to handle PM-MM correction in several different ways.
</p>

<p>
To get started with affy, first upload all of your CEL files with
the upload manager. Make sure to note your upload manager token.
Next you must specify the number of CEL files to process. Generally,
you should process all the CEL files for an experiment at once, to
take maximum advantage of cross-chip normalization.
</p>
END
	
	site_footer();
}

#### Subroutine: step2
# Handle step 1, make step 2 form
####
sub step2 {
	my @filenames = $fm->filenames;
	my $numfiles = $cgi->param('numfiles');
	my %labels;
	
	if (grep(/[^0-9]|^$/, $numfiles) || !($numfiles > 0)) {
	    error('Please enter an integer greater than 0.');
	}

	print $cgi->header;    
	site_header('Affymetrix Expression Analysis: affy');
	
	print h1('Affymetrix Expression Analysis: affy'),
	      h2('Step 2:'),
	      start_form, 
	      hidden('token', $fm->token),
	      hidden(-name=>'step', -default=>2, -override=>1),
	      hidden('numfiles', $cgi->param('numfiles')),
	      p("Select files for expression analysis:");
	      
	print '<table>',
	      Tr(th('#'), th('File'), th('Sample Name'));
	
	
	for (my $i = 0; $i < $numfiles; $i++) {
	    print Tr(td($i+1),
	             td(popup_menu(-name=>"file$i", -values=>[$fm->filenames], -default=>$filenames[$i],
	                           -onChange=>"this.form.sampleNames[$i].value = this.value")),
	             td(textfield('sampleNames', $cgi->param("file$i") ? $cgi->param("file$i") : $filenames[$i], 20)));
	}
	
	print '</table>',
		  p("Choose the processing method:"),
		  p($cgi->radio_group('process', ['RMA'], 'RMA')),
		  p($cgi->radio_group('process', ['Custom'], '-')),
		  '<ul><table>',
		  Tr(td({-style=>"text-align: right"}, "Background Correction:"), 
		     td(popup_menu('custom', ['none', 'rma', 'rma2', 'mas', 'gcrma-eb', 'gcrma-mle'], 'rma'))),
		  Tr(td({-style=>"text-align: right"}, "Normalization:"),
		     td(popup_menu('custom', ['quantiles', 'quantiles.robust', 'loess', 'contrasts', 'constant', 'invariantset', 'qspline', 'vsn'], 'quantiles'))),
		  Tr(td({-style=>"text-align: right"}, "PM Correction:"),
		     td(popup_menu('custom', ['mas', 'pmonly', 'subtractmm'], 'pmonly'))),
		  Tr(td({-style=>"text-align: right"}, "Summarization:"),
		     td(popup_menu('custom', ['avgdiff', 'liwong', 'mas', 'medianpolish', 'playerout', 'rlm'], 'medianpolish'))),
		  '</table></ul>',
		  p($cgi->checkbox('log2trans','checked','YES','Log base 2 transform the results (required for multtest)')),
		  p($cgi->checkbox('fmcopy','checked','YES','Copy exprSet back to the upload manager for further analysis')),
		  p("E-mail address where you would like your job status sent: (optional)", br(), textfield('email', '', 40)),
	      p(submit("Submit Job")),
	      end_form;
	
    print <<'END';
<h2>Quick Help</h2>

<p>
For information about each of the processing methods, see Ben
Bolstad's PDF vignette, <a
href="http://www.bioconductor.org/repository/devel/vignette/builtinMethods.pdf">affy:
Built-in Processing Methods</a>. Not all of the methods work with
one another so consult that document first.
</p>

<p>
Variance Stabilization (vsn) is a background correction and
normalization method written as an add-on to affy. If you use it,
make sure to set background correction to "none" as vsn already
does this. For more information, see Wolfgang Huber's PDF vignette,
<a
href="http://www.bioconductor.org/repository/devel/vignette/vsn.pdf">Robust
calibration and variance stabilization with VSN</a>.
</p>

<p>
GCRMA is an expression measure developed by Zhijin Wu and Rafael
A. Irizarry.  It pools MM probes with similar GC content to form
a pseudo-MM suitable for background correction of those probe pairs.
To use GCRMA, select either gcrma-eb or gcrma-mle for Background
Correction and rlm for Summarization. For further information,
please see their paper currently under preparation, <a
href="http://www.biostat.jhsph.edu/~ririzarr/papers/gcpaper.pdf">A
Model Based Background Adjustement for Oligonucleotide Expression
Arrays</a>.  Also, please note that the gcrma R package is currenly
a developmental version.
</p>
END
	
	site_footer();
}

#### Subroutine: step3
# Handle step 2, redirect web browser to results
####
sub step3 {
	my $jobname = "affy-" . rand_token();
	my (@filenames, $script, $output, $jobsummary, $custom, $error, $args, $job);
	my @custom = $cgi->param('custom');
	
	for (my $i = 0; $i < $cgi->param('numfiles'); $i++) {
		error("File does not exist.") if !$fm->file_exists($cgi->param("file$i"));
		$filenames[$i] = $cgi->param("file$i");
	}
	
	if ($cgi->param('email') && !check_email($cgi->param('email'))) {
		error("Invalid e-mail address.");
	}
	
	if ($cgi->param('process') eq "Custom" && !expresso_safe(@custom)) {
	    error("Invalid custom processing method combination");
	}
	
	$output = <<END;
<h3>Output Files:</h3>
<a href="$jobname.txt">$jobname.txt</a><br>
<a href="$jobname.exprSet">$jobname.exprSet</a><br>
END
	
	$args = "";
	if ($cgi->param('process') eq "Custom") {
	    $args = ": " . join(' -> ', $cgi->param('custom'));
	}
	if ($cgi->param('process') eq "GCRMA") {
	    $args = ": " . join(', ', $cgi->param('gcrma'));
	}
	$jobsummary = jobsummary('Files',  join(', ', @filenames),
                             'Sample&nbsp;Names', join(', ', $cgi->param('sampleNames')),
                             'Processing', scalar($cgi->param('process')) . $args,
                             'Copy&nbsp;back', $cgi->param('fmcopy') ? "Yes" : "No",
                             'E-Mail', scalar($cgi->param('email')));
	
	$script = generate_r($jobname, [@filenames]);
	
	$error = create_files($jobname, $script, $output, $jobsummary, 15, 
	                      "Affymetrix Expression Analysis", $cgi->param('email'));
	error($error) if $error;
    
    $job = new Batch;
    $job->type($BATCH_SYSTEM);
    $job->script("$RESULT_DIR/$jobname/$jobname.sh");
    $job->name($jobname);
    $job->out("$RESULT_DIR/$jobname/$jobname.out");
    $job->submit ||
    	error("Couldn't start job");
    open(ID, ">$RESULT_DIR/$jobname/id") || error("Couldn't write job id file");
    print ID $job->id;
    close(ID);
    log_job($jobname, "Affymetrix Expression Analysis", $fm);
    
    print $cgi->redirect("job.cgi?name=$jobname");
}

#### Subroutine: generate_r
# Generate an R script to process the data
####
sub generate_r {
	my ($jobname, $celfiles) = @_;
	my $celpath = $fm->path;
	my @sampleNames = $cgi->param('sampleNames');
	my $process = $cgi->param('process');
	my @custom = $cgi->param('custom');
	my $fmcopy = $cgi->param('fmcopy');
	my $script;
	
	# Escape double quotes to prevent nasty hacking
	for (@$celfiles) { s/\"/\\\"/g }
	for (@sampleNames) { s/\"/\\\"/g }
	$process =~ s/\"/\\\"/g;
	for (@custom) { s/\"/\\\"/g }
	
	# Make R variables out of the perl variables
	$script = <<END;
filenames <- c("@{[join('", "', @$celfiles)]}")
filepath <- "$celpath"
samples <- c("@{[join('", "', @sampleNames)]}")
process <- "$process"
custom <- c("@{[join('", "', @custom)]}")
log2trans <- @{[$cgi->param('log2trans') ? "TRUE" : "FALSE"]}
END

	# Main data processing, entirely R
	$script .= <<'END';
library(affy)
library(gcrma)
library(vsn)
bgcorrect.methods <- c(bgcorrect.methods, "gcrma")
normalize.AffyBatch.methods <- c(normalize.AffyBatch.methods, "vsn")
express.summary.stat.methods <- c(express.summary.stat.methods, "rlm")
setwd(filepath)
if (process == "RMA")
    exprset <- rma(ReadAffy(filenames = filenames))
# This is causing an error on Linux but not Mac OS X
# More investigation needed
#    exprset <- just.rma(filenames = filenames)
if (process == "Custom") {
    affybatch <- ReadAffy(filenames = filenames)
    bgcorrect.param <- list()
    if (custom[1] == "gcrma-eb") {
        custom[1] <- "gcrma"
        gcgroup <- getGroupInfo(affybatch)
        bgcorrect.param <- list(gcgroup, estimate = "eb", rho = 0.8, step = 60, 
                                lower.bound = 1, triple.goal = TRUE)
    }
    if (custom[1] == "gcrma-mle") {
        custom[1] <- "gcrma"
        gcgroup <- getGroupInfo(affybatch)
        bgcorrect.param <- list(gcgroup, estimate = "mle", rho = 0.8, 
                                baseline = 0.25, triple.goal = TRUE)
    }
    exprset <- expresso(affybatch, bgcorrect.method = custom[1],
                        bgcorrect.param = bgcorrect.param,
                        normalize.method = custom[2],
                        pmcorrect.method = custom[3],
                        summary.method = custom[4])
}
colnames(exprset@exprs) <- samples
log2methods <- c("medianpolish", "mas", "rlm")
if (log2trans) {
    if (process == "Custom" && !(custom[4] %in% log2methods)) {
        exprset@exprs <- log2(exprset@exprs)
        exprset@se.exprs <- log2(exprset@se.exprs)
    }
} else {
    if (process == "RMA" || process == "Custom" && custom[4] %in% log2methods) {
        exprset@exprs <- 2^exprset@exprs
        exprset@se.exprs <- 2^exprset@se.exprs
    }
}
END

    # Output results
	$script .= <<END;
save(exprset, file = "$RESULT_DIR/$jobname/$jobname.exprSet")
write.table(exprs(exprset), "$RESULT_DIR/$jobname/$jobname.txt", quote = FALSE, 
            sep = "\t", col.names = sampleNames(exprset))
END

	$script .= $fmcopy ? <<END : "";
save(exprset, file = "$celpath/$jobname.exprSet")
END

	return $script;
}

#### Subroutine: expresso_safe
# Check to see if the expresso call is valid and methods will work together
# Returns 1 if valid and 0 if not
####
sub expresso_safe {
	my ($bgcorrect, $normalize, $pmcorrect, $summary) = @_;

	if ($bgcorrect eq "rma" && $pmcorrect ne "pmonly") {
		return 0;
	}

	if (($summary eq "mas" || $summary eq "medianpolish") &&
		$pmcorrect eq "subtractmm") {
		return 0;
	}

	if ($normalize eq "vsn" && $bgcorrect ne "none") {
		return 0;
	}

	return 1;
}

#### Subroutine: error
# Print out an error message and exit
####
sub error {
    my ($error) = @_;

	print $cgi->header;    
	site_header("Affymetrix Expression Analysis: affy");
	
	print h1("Affymetrix Expression Analysis: affy"),
	      h2("Error:"),
	      p($error);
	
	site_footer();
	
	exit(1);
}
