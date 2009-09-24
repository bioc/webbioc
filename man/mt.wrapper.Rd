\name{mt.wrapper}
\alias{mt.wrapper}
\title{Multiple Testing Wrapper Function}
\description{
  A wrapper for some of the functionality for the \code{multtest}
  package. It also includes hooks to calculate q-values with John
  D. Storey's \file{q-value.R} code.
}

\usage{
mt.wrapper(proc, X, classlabel, test="t", rawpcalc="Parametric", side="abs", ...)
}
\arguments{
  \item{proc}{A character string containing the name of the multiple
    testing procedure for which adjusted \eqn{p}-values are to be
    computed. This vector should include any of the following:
    \code{"Bonferroni"}, \code{"Holm"}, \code{"Hochberg"},
    \code{"SidakSS"}, \code{"SidakSD"}, \code{"BH"}, \code{"BY"},
    \code{"maxT"}, \code{"minP"}, \code{"q"}.
  }
  \item{X}{A data frame or matrix, with \eqn{m} rows corresponding to variables
    (hypotheses) and
    \eqn{n} columns to observations. In the case of gene expression data, rows
    correspond to genes and columns to mRNA samples. The data can
    be read using \code{\link{read.table}}.
  }
  \item{classlabel}{
    A vector of integers corresponding to observation (column)
    class labels. For \eqn{k} classes, the labels must be integers
    between 0 and \eqn{k-1}. For the \code{blockf} test option,
    observations may be divided into
    \eqn{n/k} blocks of \eqn{k} observations each. The observations are
    ordered by block, and within each block, they are labeled using the
    integers 0 to \eqn{k-1}.
  }	
  \item{test}{A character string specifying the statistic to be
    used to test the null hypothesis of no association between the
    variables and the class labels.\cr
    If \code{test="t"}, the tests are based on two-sample Welch t-statistics
    (unequal variances).  \cr
    If \code{test="t.equalvar"}, the tests are based on two-sample
    t-statistics with equal variance for the two samples. The
    square of the t-statistic is equal to an F-statistic for \eqn{k=2}. \cr
    If \code{test="wilcoxon"}, the tests are based on standardized rank sum Wilcoxon statistics.\cr
    If \code{test="f"}, the tests are based on F-statistics.\cr
    If \code{test="pairt"}, the tests are based on paired t-statistics. The
    square of the paired t-statistic is equal to a block F-statistic for \eqn{k=2}. \cr
    If \code{test="blockf"}, the tests are based on F-statistics which
    adjust for block differences
    (cf. two-way analysis of variance).
  }
  \item{rawpcalc}{A character string specifying how to calculate
    nominal/raw p-values. The possible choices are \code{"Parametric"}
    or \code{"Permutation"}.
  }
  \item{side}{A character string specifying the type of rejection region.\cr
    If \code{side="abs"}, two-tailed tests, the null hypothesis is rejected for large absolute values of the test statistic.\cr
    If \code{side="upper"}, one-tailed tests, the null hypothesis is rejected for large values of the test statistic.\cr
    If \code{side="lower"}, one-tailed tests,  the null hypothesis is rejected for small values of the test statistic.
  }
  \item{...}{Further arguments for \code{mt.maxT}, \code{mt.minP}, \code{qvalue}.}
}

\value{
  A data frame with components
  \item{index}{Vector of row indices, between 1 and \code{nrow(X)},
    where rows are sorted first according to their adjusted
    \eqn{p}-values, next their unadjusted \eqn{p}-values, and
    finally their test statistics. }
  \item{teststat}{Vector of test statistics, ordered according to
    \code{index}.  To get the test statistics in the original data
    order, use \code{teststat[order(index)]}.}
  \item{rawp}{Vector of raw (unadjusted) \eqn{p}-values, ordered
  according to \code{index}.} 
  \item{adjp}{Vector of adjusted \eqn{p}-values, ordered according to
  \code{index}.} 
  \item{plower}{For \code{\link[multtest:mt.maxT]{mt.minP}} function
     only, vector of "adjusted \eqn{p}-values", where ties in the permutation
    distribution of the successive minima of raw \eqn{p}-values
    with the observed \eqn{p}-values are counted only once. Note
    that procedures based on \code{plower} do not control the FWER.
    Comparison of \code{plower} and \code{adjp} gives an idea of
    the discreteness of the permutation distribution. Values in
    \code{plower} are ordered according to \code{index}.}
  }


\author{Colin A. Smith \email{webbioc@colinsmith.org}}
\keyword{ file }
