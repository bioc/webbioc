require("reposTools")

installReps <- function(repNames = c("BIOCData", "BIOCcdf", "BIOCprobes"), 
                        lib = reposToolsLibPaths()[1]) {

    cat("Using library path: ", lib, "\n", sep = "")
    
    for (repName in repNames) {
        url <- getReposOption()[repName]
        repos <- getReposEntry(url)
        cat(paste("Installing/updating all packages from repository ", repName, 
            ":\n", sep = ""))
        print(repObjects(repos)[,1])
        install.packages2(repObjects(repos)[,1], repos, lib, type="Source")
    }
}
