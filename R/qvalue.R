#Version 1.1; Updated June 2003
#These functions estimate the q-values for a given set of p-values. The
#statistical methodology mainly comes from:
#Storey JD. (2002) A direct approach to false discovery rates. 
#Journal of the Royal Statistical Society, Series B, 64: 479-498.
#See http://faculty.washington.edu/~jstorey/qvalue/ for more info. 
#All functions were written by John D. Storey. Copyright 2002,2003 by John D. Storey.
#All rights are reserved and no responsibility is assumed for mistakes in or caused by
#the program.

qvalue <- function(p, lambda=seq(0,0.95,0.05), pi0.meth="smoother", fdr.level=NULL, robust=F) { 
#Input
#=============================================================================
#p: a vector of p-values (only necessary input)
#fdr.level: a level at which to control the FDR (optional)
#lambda: the value of the tuning parameter to estimate pi0 (optional)
#pi0.method: either "smoother" or "bootstrap"; the method for automatically
#           choosing tuning parameter in the estimation of pi0, the proportion
#           of true null hypotheses
#robust: an indicator of whether it is desired to make the estimate more robust 
#        for small p-values and a direct finite sample estimate of pFDR (optional)
#
#Output
#=============================================================================
#call: gives the function call
#pi0: an estimate of the proportion of null p-values
#qvalues: a vector of the estimated q-values (the main quantity of interest)
#pvalues: a vector of the original p-values
#significant: if fdr.level is specified, and indicator of whether the q-value 
#    fell below fdr.level (taking all such q-values to be significant controls 
#    FDR at level fdr.level)

#This is just some pre-processing
    if(min(p)<0 || max(p)>1) {
    print("ERROR: p-values not in valid range"); return(0)
    }
    if(length(lambda)>1 && length(lambda)<4) {
    print("ERROR: If length of lambda greater than 1, you need at least 4 values."); return(0)
    }
    m <- length(p)
#These next few functions are the various ways to estimate pi0
    if(length(lambda)==1) {
        pi0 <- mean(p >= lambda)/(1-lambda)
        pi0 <- min(pi0,1)
    }
    else{
        pi0 <- rep(0,length(lambda))
        for(i in 1:length(lambda)) {
            pi0[i] <- mean(p >= lambda[i])/(1-lambda[i])
        }
        if(pi0.meth=="smoother") {
            library(modreg)
            spi0 <- smooth.spline(lambda,pi0,df=3)
            pi0 <- predict(spi0,x=max(lambda))$y
            pi0 <- min(pi0,1)
        }
        if(pi0.meth=="bootstrap") {
            minpi0 <- min(pi0)
            mse <- rep(0,length(lambda))
            pi0.boot <- rep(0,length(lambda))
            for(i in 1:100) {
                p.boot <- sample(p,size=m,replace=T)
                for(i in 1:length(lambda)) {
                    pi0.boot[i] <- mean(p.boot>lambda[i])/(1-lambda[i])
                }
                mse <- mse + (pi0.boot-minpi0)^2
            }
            pi0 <- min(pi0[mse==min(mse)])
            pi0 <- min(pi0,1)
        }    
    }
    if(pi0 <= 0) {
    print("ERROR: The estimated pi0 <= 0. Check that you have valid p-values or use another lambda.meth."); return(0)
    }
#The estimated q-values calculated here
    u <- order(p)
    v <- rank(p)
    qvalue <- pi0*m*p/v
    if(robust) {
        qvalue <- pi0*m*p/(v*(1-(1-p)^m))
    }
    qvalue[u[m]] <- min(qvalue[u[m]],1)
    for(i in (m-1):1) {
    qvalue[u[i]] <- min(qvalue[u[i]],qvalue[u[i+1]],1)
    }
#The results are returned
    if(!is.null(fdr.level)) {
        retval <- list(call=match.call(), pi0=pi0, qvalues=qvalue, pvalues=p, significant=(qvalue <= fdr.level), lambda=lambda)
    }
    else {
        retval <- list(call=match.call(), pi0=pi0, qvalues=qvalue, pvalues=p, lambda=lambda)
    }
    class(retval) <- "qvalue"
    return(retval)
}

qplot <- function(qobj, rng=0.1) {
#Input
#=============================================================================
#qobj: a q-value object returned by the qvalue function
#rng: the range of q-values to be plotted (optional)
#
#Output
#=============================================================================
#Four plots: 
#Upper-left: pi0.hat(lambda) versus lambda with a smoother
#Upper-right: q-values versus p-values
#Lower-left: number of significant tests per each q-value cut-off
#Lower-right: number of expected false positives versus number of significant tests
library(modreg)
q2 <- qobj$qval[order(qobj$pval)]
if(min(q2) > rng) {rng <- quantile(q2, 0.1)}
p2 <- qobj$pval[order(qobj$pval)]
par(mfrow=c(2,2))
lambda <- qobj$lambda
if(length(lambda)==1) {lambda <- seq(0,max(0.95,lambda),0.05)}
pi0 <- rep(0,length(lambda))
for(i in 1:length(lambda)) {
    pi0[i] <- mean(p2>lambda[i])/(1-lambda[i])
    }    
spi0 <- smooth.spline(lambda,pi0,df=3)
pi00 <- round(qobj$pi0,3)
plot(lambda,pi0,xlab=expression(lambda),ylab=expression(hat(pi)[0](lambda)),pch=".")
mtext(substitute(hat(pi)[0] == that, list(that= pi00)))
lines(spi0)
plot(p2[q2<=rng],q2[q2<=rng],type="l",xlab="p-value",ylab="q-value")
plot(q2[q2<=rng],1:sum(q2<=rng),type="l",xlab="q-value cut-off",ylab="significant tests")
plot(1:sum(q2<=rng),q2[q2<=rng]*(1:sum(q2<=rng)),type="l",xlab="significant tests",ylab="expected false positives")
par(mfrow=c(1,1))
}

qwrite <- function(qobj, filename="my-qvalue-results.txt") {
#Input
#=============================================================================
#qobj: a q-value object returned by the qvalue function
#filename: the name of the file where the results are written
#
#Output
#=============================================================================
#A file sent to "filename" with the following:
#First row: the function call used to produce the estimates
#Second row: the estimate of the proportion of false positives, pi0
#Third row and below: the p-values (1st column) and the estimated q-values (2nd column) 
cat(c("Function call:", deparse(qobj$call), "\n"), file=filename, append=F)
cat(c("Estimate of the overall proportion of false positives pi0:", qobj$pi0, "\n"), file=filename, append=T)
for(i in 1:length(qobj$qval)) {
    cat(c(qobj$pval[i], qobj$qval[i], "\n"), file=filename, append=T)
    }
}
