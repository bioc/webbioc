mt.wrapper <- function(proc, X, classlabel, test="t", rawpcalc="Parametric", side="abs", ...) {

	if (proc == "maxT")
		return(mt.maxT(X, classlabel, test, side, ...))
	if (proc == "minP")
		return(mt.minP(X, classlabel, test, side, ...))

	teststat <- mt.teststat(X, classlabel, test)
	# Workaround for the mt.teststat problem with test statistics of 0
	teststat[teststat > 3.402823e+38] <- 0
	
	if (test == "t") {
	    n1 <- sum(classlabel == 0)
	    n2 <- sum(classlabel == 1)
		A <- sd(t(X[,classlabel == 0]))^2/n1
		B <- sd(t(X[,classlabel == 1]))^2/n2
		df <- (A+B)^2/(A^2/(n1-1)+B^2/(n2-1))
	}
	if (test == "t.equalvar")
	    df <- length(classlabel) - 2
	if (test == "wilcoxon") {
		m <- sum(classlabel == 0)
		n <- sum(classlabel == 1)
	}
	if (test == "f") {
		df1 <- max(classlabel)
		df2 <- length(classlabel) - (df1+1)
	}
	if (test == "pairt")
	    df <- (length(classlabel) - 2)/2
	if (test == "blockf") {
		df1 <- max(classlabel)
		df2 <- (length(classlabel) - (df1+1))/(df1+1)
	}
	
	if (side == "abs") {
	    if (test == "t" || test == "t.equalvar" || test == "pairt")
	        rawp <- 2 * (1 - pt(abs(teststat), df))
	    if (test == "wilcoxon")
	        rawp <- 2 * (1 - pwilcox(abs(teststat), m, n))
	    if (test == "f" || test == "blockf")
	        rawp <- 1 - pf(teststat, df1, df2)
        testorder <- -abs(teststat)
	}
	if (side == "upper") {
	    if (test == "t" || test == "t.equalvar" || test == "pairt")
		    rawp <- 1 - pt(teststat, df)
	    if (test == "wilcoxon")
	        rawp <- 1 - pwilcox(teststat, m, n)
	    if (test == "f" || test == "blockf")
		    rawp <- 1 - pf(teststat, df1, df2)
        testorder <- -teststat
    }
	if (side == "lower") {
	    if (test == "t" || test == "t.equalvar" || test == "pairt")
		    rawp <- 1 - pt(teststat, df, lower.tail = FALSE)
	    if (test == "wilcoxon")
	        rawp <- 1 - pwilcox(teststat, m, n, lower.tail = FALSE)
	    if (test == "f" || test == "blockf")
		    rawp <- 1 - pf(teststat, df1, df2, lower.tail = FALSE)
        testorder <- teststat
    }
    if (rawpcalc == "Permutation") {
        maxt <- mt.maxT(X, classlabel, test, side, ...)
        rawp <- maxt$rawp[order(maxt$index)]
    }
    rawp[is.nan(rawp)] <- NA

    if (proc == "q") {
        adjp <- as.numeric(rep(NA, length(rawp)))
    	adjp[!is.na(rawp)] <- qvalue(rawp[!is.na(rawp)], ...)$qvalues
    } else {
        adjp <- mt.rawp2adjp(rawp, proc)
        adjp <- adjp$adjp[order(adjp$index), 2]
    }
    
    if (dim(X)[1] == 1)
        index <- 1
    else
        index <- order(adjp, rawp, testorder)
    
    return(data.frame(index = index, teststat = teststat[index], 
                      rawp = rawp[index], adjp = adjp[index]));
}
