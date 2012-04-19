installReps <- function(repNames = "aData", lib = .libPaths()[1], 
                        type = getOption("pkgType")) {

    cat("Using library path: ", lib, "\n", sep = "")
    
    
    for (repName in repNames) {
        packages <- available.packages(contrib.url(biocinstallRepos()[repName]), 
                                                   type)
        cat(paste("Installing/updating all packages from repository ", repName, 
            ":\n", sep = ""))
        print(packages[,"Package"])
        install.packages(packages[,"Package"], lib, biocinstallRepos()[repName], 
                         type=type)
    }
}
