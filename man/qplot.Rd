\name{qplot}
\alias{qplot}
\title{Plot q-value Result Diagnostics}
\description{
  Plots diagnostic graphs for the qvalue function.
}

\usage{
qplot(qobj, rng=0.1)
}
\arguments{
  \item{qobj}{a q-value object returned by the qvalue function}
  \item{rng}{the range of q-values to be plotted}
}

\value{
  Four plots:
  \item{Upper-left}{pi0.hat(lambda) versus lambda with a smoother}
  \item{Upper-right}{q-values versus p-values}
  \item{Lower-left}{number of significant tests per each q-value
                    cut-off}
  \item{Lower-right}{number of expected false positives versus
                     number of significant tests}
}

\references{
  Storey JD. (2002) A direct approach to false discovery rates.
  \emph{Journal of the Royal Statistical Society}, Series B, 64:
  479-498.
}
\author{John D. Storey \url{http://faculty.washington.edu/~jstorey/}}
\keyword{ file }
