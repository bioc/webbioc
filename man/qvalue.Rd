\name{qvalue}
\alias{qvalue}
\title{Estimate pFDR q-values from p-values}
\description{
  Applies the q-value multiple testing procedure to a group of
  unadjusted p-values.
}

\usage{
qvalue(p, lambda=seq(0,0.95,0.05), pi0.meth="smoother", fdr.level=NULL, robust=F)
}
\arguments{
  \item{p}{a vector of p-values}
  \item{fdr.level}{a level at which to control the FDR}
  \item{lambda}{the value of the tuning parameter to estimate pi0}
  \item{pi0.meth}{either "smoother" or "bootstrap"; the method for
		  automatically choosing tuning parameter in the
		  estimation of pi0, the proportion of true null
		  hypotheses}
  \item{robust}{an indicator of whether it is desired to make the
		estimate more robust for small p-values and a direct
		finite sample estimate of pFDR}
}

\value{
  \item{call}{gives the function call}
  \item{pi0}{an estimate of the proportion of null p-values}
  \item{qvalues}{a vector of the estimated q-values (the main
                 quantity of interest)}
  \item{pvalues}{a vector of the original p-values}
  \item{significant}{if fdr.level is specified, and indicator of
		     whether the q-value fell below fdr.level
		     (taking all such q-values to be significant
		     controls FDR at level fdr.level)}
}

\references{
  Storey JD. (2002) A direct approach to false discovery rates.
  \emph{Journal of the Royal Statistical Society}, Series B, 64:
  479-498.
}
\author{John D. Storey \url{http://faculty.washington.edu/~jstorey/}}
\keyword{ file }
