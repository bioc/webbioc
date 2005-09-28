\name{qwrite}
\alias{qwrite}
\title{Save q-value Results to a File}
\description{
  Saves the object created by the qvalue function to a plain text file.
}

\usage{
qwrite(qobj, filename="my-qvalue-results.txt")
}
\arguments{
  \item{qobj}{a q-value object returned by the qvalue function}
  \item{filename}{the name of the file where the results are written}
}

\value{
  A file sent to "filename" with the following:
  \item{First row}{the function call used to produce the estimates}
  \item{Second row}{the estimate of the proportion of false positives,
                    pi0}
  \item{Third row and below}{the p-values (1st column) and the
                             estimated q-values (2nd column)}
}

\references{
  Storey JD. (2002) A direct approach to false discovery rates.
  \emph{Journal of the Royal Statistical Society}, Series B, 64:
  479-498.
}
\author{John D. Storey \url{http://faculty.washington.edu/~jstorey/}}
\keyword{ file }
