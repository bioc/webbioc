\name{installReps}
\alias{installReps}
\title{Install all repository packages}
\description{
  Using reposTools, install/update all packages from given repositories.
}

\usage{
installReps(repNames = c("BIOCData", "BIOCcdf", "BIOCprobes"),
            lib = reposToolsLibPaths()[1])
}
\arguments{
  \item{repNames}{A character vector containing repository names. A listing
    of known repository names can be found with the getReposOption() function.
  }
  \item{lib}{A path to install/update the packages. If this directory does not
    exist, it will be created (if possible).
  }
}

\author{Colin A. Smith \email{webbioc@colinsmith.org}}
\keyword{ file }
