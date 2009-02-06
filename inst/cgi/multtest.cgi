#!/usr/bin/perl -w

use CGI qw/:standard/;
use CGI::Pretty;
$CGI::Pretty::INDENT = "";
use POSIX;
use FileManager;
use Batch;
use BioC;
use Site;
use strict;

# Test statistic descriptions
our %tests = ('t'=>'two-sample Welch t-test (unequal variances)',
			  't.equalvar'=>'two-sample t-test (equal variances)',
			  'wilcoxon'=>'standardized rank sum Wilcoxon test',
			  'f'=>'F-test',
			  'pairt'=>'paired t-test',
			  'blockf'=>'block F-test');

# Multiple testing procedure descriptions
our %procs = ('Bonferroni'=>'Bonferroni single-step FWER',
              'Holm'=>'Holm step-down FWER',
              'Hochberg'=>'Hochberg step-up FWER',
              'SidakSS'=>'Sidak single-step FWER',
              'SidakSD'=>'Sidak step-down FWER',
              'BH'=>'Benjamini & Hochberg step-up FDR',
              'BY'=>'Benjamini & Yekutieli step-up FDR',
              'q'=>'Storey q-value single-step pFDR',
              'maxT'=>'Westfall & Young maxT permutation FWER',
              'minP'=>'Westfall & Young minP permutation FWER');

# Limit descriptions
our %limits = ('total'=>'a total number of', 
	           'teststat'=>'absolute test statistics greater than',
	           'rawp'=>'raw p-values less than', 
	           'adjp'=>'adjusted p-values less than');

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
} elsif ($cgi->param('step') == 3) {
    step4();
} else {
    error('There was an error in form input.');
}

#### Subroutine: step1
# Make step 1 form
####
sub step1 {

	print $cgi->header;    
	site_header('Multiple Testing: multtest');
	
	print h1('Multiple Testing: multtest'),
	      h2('Step 1:'),
	      start_form,
	      hidden('step', 1),
	      p('Enter upload manager token:', textfield('token', $fm->token, 30)),
	      submit("Next Step"),
	      end_form,
	      p(a({-href=>"upload.cgi"}, "Go to Upload Manager"));

    print <<'END';
<h2>Quick Help</h2>

<p>
multtest includes several tests for differences in means (t-test,
F-test, etc.) as well as a number of procedures for controlling
the error rate for many simultaneous hypotheses. Such control is
very important in the context of microarray experiments. Additionally,
multtest provides the ability to make specific hypotheses about
groups of genes within a microarray experiment and can select genes
that meet certain testing criteria. Finally, muttest produces three
diagnostic plots, an MA plot, a quantile-quantile plot, and a
multiple testing procedure selectivity plot.
</p>

<p>
To get started with multtest, you must have a pre-existing ExpressionSet
in the upload manager. affy will create one and will place it back
into the upload manager for you. Additionally, you may upload an
ExpressionSet of your own creation. It must be saved in an R data file
and be the only object in that file. It may have any name you wish.
</p>
END
	
	site_footer();
}

#### Subroutine: step2
# Handle step 1, make step 2 form
####
sub step2 {
	my @filenames = $fm->filenames;

	print $cgi->header;    
	site_header('Multiple Testing: multtest');
	
	print h1('Multiple Testing: multtest'),
	      h2('Step 2:'),
	      start_form, 
	      hidden('token', $fm->token),
	      hidden(-name=>'step', -default=>2, -override=>1),
	      p("Select an ExpressionSet for analysis:"),
	      p(scrolling_list('file', \@filenames)),
	      p('Enter number of experimental classes:', textfield('numclasses', 2, 10)),
	      p(submit("Next Step")),
	      end_form;
	
	print <<'END';
<h2>Quick Help</h2>

<p>
For t-tests and Wilcoxon tests, there must only be 2 experimental
classes (generally a control and experimental class). However, for
the ANOVA F-test, you may have more than two classes.
</p>
END
	
	site_footer();
}

#### Subroutine: step3
# Handle step 2, make step 3 form
####
sub step3 {
	my $filename = $cgi->param('file');
	my $numclasses = $cgi->param('numclasses');
	my @filenames = $fm->filenames;
	my ($name, @sampleNames, $annotation, $err);
	
	error('Please select an ExpressionSet.') if !$filename;
	error('File not found.') if !$fm->file_exists($filename);
	if (grep(/[^0-9]|^$/, $numclasses) || !($numclasses > 0)) {
	    error('Please enter an integer greater than 0.');
	}
	
	$err = parse_ExpressionSet($fm->path . "/$filename", \$name, \@sampleNames, 0, \$annotation);
	error($err) if $err;

	print $cgi->header;    
	site_header('Multiple Testing: multtest');
	
	print h1('Multiple Testing: multtest'),
	      h2('Step 3:'),
	      start_form, 
	      hidden('token', $fm->token),
	      hidden(-name=>'step', -default=>3, -override=>1),
	      hidden('file', $filename),
	      hidden('name', $name),
	      hidden('numsamples', scalar @sampleNames),
	      p("Select the experimental class for each sample:");
	      
	print '<table>',
	      Tr(th('Sample Name'), th('Class Label'));
	
	my @classes = (0 .. $numclasses-1, "Ignore");
	for (my $i = 0; $i < @sampleNames; $i++) {
	    print Tr(td($sampleNames[$i]),
	             td(radio_group("class$i", \@classes, floor($i/(@sampleNames)*$numclasses))));
	}
	
	print '</table>',
	      '<table><tr><td>',
	      p("Differential Expression/Null Hypothesis Test:"),
		  p(scrolling_list('test', ['t', 't.equalvar', 'wilcoxon', 'f', 'pairt', 'blockf'], 
		                   ['t'], 6, '', \%tests)),
		  p("Raw/Nominal p-value calculation:"),
	      p(radio_group('rawpcalc', ['Parametric', 'Permutation'], 'Parametric')),
	      p("Side/Rejection Region:"),
	      p(radio_group('side', ['abs', 'upper', 'lower'], 'abs')),
	      '</td><td style="width: 25px"></td><td style="vertical-align: top">',
	      p("Multiple testing procedure:"),
	      p(scrolling_list('proc', ['Bonferroni', 'Holm', 'Hochberg', 'SidakSS', 'SidakSD', 
	                                'BY', 'BH', 'q', 'maxT', 'minP'], ['Bonferroni'], 10, '', \%procs)),
	      '</td></tr></table>',
	      p(checkbox('limit', 'checked', 'YES', ''),
	        "Limit results to",
	        popup_menu('limittype', ['total', 'adjp', 'rawp', 'teststat'], 'total', \%limits),
	        textfield('limitnum', 100, 10)),
	      p("Test only these gene names: (optional)", br, textarea('genenames', '', 5, 80)),
	      p(checkbox('exprs','','YES','Include expression values in results')),
		  p(checkbox('fmcopy','','YES','Copy aafTable back to the upload manager for further annotation')),
		  p("Web Page Title:", br, textfield('title', 'Multiple Testing Results', 40)),
	      p("E-mail address where you would like your job status sent: (optional)", br,
            textfield('email', '', 40)),
          p(submit("Submit Job")),
	      end_form;
	
    print <<'END';
<h2>Quick Help</h2>

<p>
The control group should almost always be in a lower class than
the experimental group so that positive test statistics indicate
increased expression and vice versa. Results are sorted first by
adjusted p-value, then raw p-value, and finally test statistic.
</p>

<p>
For more information about multiple testing, see these two papers:
</p>

<p>
Y. Ge, S. Dudoit, and T. P. Speed (2003). Resampling-based multiple
testing for microarray data analysis. <em>TEST</em>, Vol. 12, No.
1, p.  1-44 (plus discussion p. 44-77) <a
href="http://www.stat.berkeley.edu/tech-reports/633.pdf">[PDF]</a>
</p>

<p>
S. Dudoit, J. P. Shaffer, and J. C. Boldrick (2003). Multiple
hypothesis testing in microarray experiments. <em>Statistical
Science</em>, Vol. 18, No. 1, p. 71-103. <a
href="http://www.bepress.com/cgi/viewcontent.cgi?article=1014&context=ucbbiostat">[PDF]</a>
</p>
END
	
	site_footer();
}

#### Subroutine: step4
# Handle step 3, redirect web browser to results
####
sub step4 {
	my $jobname = "mt-" . rand_token();
	my $genenames = $cgi->param('genenames');
	$genenames =~ s/[,;"']/ /g;
	my @genenames = split(' ', $genenames);
	my ($script, $output, $jobsummary, $limit, @classlabel, $error, $job);
	
	if (grep(/[^0-9\.]|^$/, $cgi->param('limitnum')) || !($cgi->param('limitnum') > 0)) {
	    error('Please enter an number greater than 0.');
	}
	if ($cgi->param('email') && !check_email($cgi->param('email'))) {
		error("Invalid e-mail address.");
	}
	if (! $fm->file_exists($cgi->param('file'))) {
		error("File does not exist.");
	}
	
	for (my $i = 0; $i < $cgi->param('numsamples'); $i++) {
		$classlabel[$i] = $cgi->param("class$i");
	}
	
	$script = generate_r($jobname, [@classlabel], [@genenames]);
	
	my $maqq = (grep(/t/, $cgi->param('test'))) ? '<img src="ma.png"><img src="qq.png">' : "";
	$output = <<END;
<h3>Output Files:</h3>
<a href="$jobname.html">$jobname.html</a><br>
<a href="$jobname.txt">$jobname.txt</a><br>
<a href="$jobname.aafTable">$jobname.aafTable</a><br>
<p>$maqq<img src="rvsa.png"></p>
END
	
	$limit = $cgi->param('limit') ? $limits{$cgi->param('limittype')} . " " . 
	         $cgi->param('limitnum') : "None";
	$jobsummary = jobsummary('File', scalar($cgi->param('file')),
	                         'Class&nbsp;labels', join(', ', @classlabel),
	                         'Test', $tests{$cgi->param('test')},
	                         'Raw&nbsp;p-values', scalar($cgi->param('rawpcalc')),
	                         'Side', scalar($cgi->param('side')),
	                         'Procedure', $procs{$cgi->param('proc')},
	                         'Limit', $limit,
	                         'Gene&nbsp;names', join(', ', @genenames),
	                         'Expression', $cgi->param('exprs') ? "Yes" : "No",
	                         'Copy&nbsp;back', $cgi->param('fmcopy') ? "Yes" : "No",
	                         'Title', scalar($cgi->param('title')),
	                         'E-Mail', scalar($cgi->param('email')));
	
	$error = create_files($jobname, $script, $output, $jobsummary, 5, 
	                      $cgi->param('title'), $cgi->param('email'));
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
    log_job($jobname, $cgi->param('title'), $fm);
    
    print $cgi->redirect("job.cgi?name=$jobname");
}

#### Subroutine: generate_r
# Generate an R script to process the data
####
sub generate_r {
	my ($jobname, $classlabel, $genenames) = @_;
	my $fmpath = $fm->path;
	my $filename = $cgi->param('file');
	my $name = $cgi->param('name');
	my $proc = $cgi->param('proc');
	my $test = $cgi->param('test');
	my $rawpcalc = $cgi->param('rawpcalc');
	my $side = $cgi->param('side');
	my $limit = $cgi->param('limit');
	my $limittype = $cgi->param('limittype');
	my $limitnum = $cgi->param('limitnum');
	my $exprs = $cgi->param('exprs');
	my $title = $cgi->param('title');
	my $fmcopy = $cgi->param('fmcopy');
	my $script;
	
	# Escape double quotes to prevent nasty hacking
	$filename =~ s/\"/\\\"/g;
	$name =~ s/\"/\\\"/g;
	for (@$classlabel) { s/\"/\\\"/g }
	$proc =~ s/\"/\\\"/g;
	$test =~ s/\"/\\\"/g;
	$rawpcalc =~ s/\"/\\\"/g;
	$side =~ s/\"/\\\"/g;
	$limittype =~ s/\"/\\\"/g;
	$limitnum =~ s/\"/\\\"/g;
	$title =~ s/\"/\\\"/g;
	
	# Make R variables out of the perl variables
	$script = <<END;
load("$fmpath/$filename")
exprset <- get("$name")
classlabel <- c("@{[join('", "', @$classlabel)]}")
proc <- "$proc"
test <- "$test"
rawpcalc <- "$rawpcalc"
side <- "$side"
limit <- @{[$limit ? "TRUE" : "FALSE"]}
limittype <- "$limittype"
limitnum <- as.numeric("$limitnum")
genenames <- c("@{[join('", "', @$genenames)]}")
if (!nchar(genenames[1]))
    genenames <- NULL
exprs <- @{[$exprs ? "TRUE" : "FALSE"]}
title <- "$title"
END

	# Main data processing, entirely R
	$script .= <<'END';
library(Biobase)
library(multtest)
library(annaffy)
library(webbioc)
library(qvalue)

cols <- which(classlabel != "Ignore")
classlabel <- as.integer(classlabel[cols])
X <- exprs(exprset)[,cols]
selected <- featureNames(exprset) %in% genenames
if (!sum(selected) && !is.null(genenames))
    stop("None of the entered gene names were found in the ExpressionSet.")
if (!sum(selected))
    selected <- !selected
mtdata <- mt.wrapper(proc, X[selected,,drop=F], classlabel, test, rawpcalc, side)
index <- mtdata$index
teststat <- mt.teststat(X, classlabel, test)
adjp <- mtdata$adjp
lim <- ! logical(dim(mtdata)[1])
if (limit) {
	if (limittype == "total" && limitnum < length(lim))
	    lim[(limitnum+1):length(lim)] <- FALSE
	if (limittype == "teststat")
	    lim <- (abs(mtdata$teststat) > limitnum)
	if (limittype == "rawp")
	    lim <- (mtdata$rawp < limitnum)
	if (limittype == "adjp")
	    lim <- (mtdata$adjp < limitnum)
	if (!sum(lim))
	    stop("Specified limit produces no results.")
}
mtdata <- mtdata[lim,,drop=F]
row.names(mtdata) <- featureNames(exprset)[which(selected)[index[lim]]]
mtdata <- mtdata[2:4]
colnames(mtdata) <- c(paste(test, "statistic"), "raw p-value", 
                      paste(proc, "-value", sep = ""))
aaftable <- merge(aafTableFrame(mtdata[1], signed = (side == "abs")),
                  aafTableFrame(mtdata[2:3]));
if (max(classlabel) == 1) {
    x <- as.numeric(mean(as.data.frame(2^t(X[,(classlabel == 0)]))))
    y <- as.numeric(mean(as.data.frame(2^t(X[,(classlabel == 1)]))))
    fold <- y/x
    mtdata <- cbind(fold[index[lim]], mtdata)
    colnames(mtdata)[1] <- "Fold Change"
    aaftable <- merge(aafTable("Fold Change" = fold[index[lim]]), aaftable)
}
if (exprs) {
	mtdata <- cbind(mtdata, exprs(exprset)[index[lim],cols])
    aaftable <- merge(aaftable, aafTableInt(exprset[which(selected)[index[lim]],cols]))
}
if (!limit)
    lim <- !lim
limall <- logical(dim(X)[1])
limall[which(selected)[lim[order(index)]]] <- TRUE;
END

	# Output results
	$script .= <<END;
write.table(mtdata, "$RESULT_DIR/$jobname/$jobname.txt", quote = FALSE, 
            sep = "\t", col.names = colnames(mtdata))
saveHTML(merge(aafTable("Gene Name" = probeids(aaftable)), aaftable), 
         "$RESULT_DIR/$jobname/$jobname.html", title)
save(aaftable, file = "$RESULT_DIR/$jobname/$jobname.aafTable")
END

	$script .= $fmcopy ? <<END : "";
save(aaftable, file = "$fmpath/$jobname.aafTable")
END

    # MA plot
    $script .= (grep(/t/, $test)) ? <<END : "";
bitmap("$RESULT_DIR/$jobname/ma.png", res = 72*4, pointsize = 12)
macoords <- matrix(c(log2(sqrt(x*y)), log2(y/x)), ncol = 2)
plot(macoords, main="M vs. A Plot", xlab="A", ylab="M", type="n")
points(macoords[!selected,,drop=F], pch=20, col=grey(.5))
points(macoords[selected & !limall,,drop=F], pch=20)
points(macoords[selected & limall,,drop=F], pch=20, col="red")
dev.off()
END

    # Normal QQ plot
    $script .= (grep(/t/, $test)) ? <<END : "";
bitmap("$RESULT_DIR/$jobname/qq.png", res = 72*4, pointsize = 12)
qqcoords <- qqnorm(teststat, type="n")
qqcoords <- matrix(c(qqcoords[[1]], qqcoords[[2]]), ncol = 2)
points(qqcoords[!selected,,drop=F], pch=20, col=grey(.5))
points(qqcoords[selected & !limall,,drop=F], pch=20)
points(qqcoords[selected & limall,,drop=F], pch=20, col="red")
qqline(teststat)
dev.off()
END

    # Selectivity plot
    $script .= <<END;
bitmap("$RESULT_DIR/$jobname/rvsa.png", res = 72*4, pointsize = 12)
alpha <- seq(0, 0.99, length = 100)
r <- mt.reject(adjp[!is.na(adjp)], alpha)[["r"]]
plot(alpha, r, main = "Multiple Testing Procedure Selectivity", 
     xlab = "Error rate", ylab = "Number of rejected hypotheses", 
     type = "l")
if (limit)
    points(alpha[r<=sum(lim)], r[r<=sum(lim)], type = "l", col = "red")
dev.off()
END
}

#### Subroutine: error
# Print out an error message and exit
####
sub error {
    my ($error) = @_;

	print $cgi->header;    
	site_header("Multiple Testing: multtest");
	
	print h1("Multiple Testing: multtest"),
	      h2("Error:"),
	      p($error);
	
	site_footer();
	
	exit(1);
}
