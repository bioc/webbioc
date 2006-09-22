\name{installReps}
\alias{installReps}
\title{Install all repository packages}
\description{
  Using reposTools, install/update all packages from given repositories.
}

\usage{
installReps(repNames = "aData", lib = .libPaths()[1], 
            type = getOption("pkgType"))
}
\arguments{
  \item{repNames}{A character vector containing repository names. A listing
    of known repository names can be found with the getReposOption() function.
  }
  \item{lib}{A path to install/update the packages. If this directory does not
    exist, it will be created (if possible).
  }
  \item{type}{type of package do download}
}

\author{Colin A. Smith \email{webbioc@colinsmith.org}}
\keyword{ file }
