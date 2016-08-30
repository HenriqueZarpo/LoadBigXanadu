import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import poisson


def comptecols(filename, delimiter=","):
    with open(filename,"r") as f:
        a=f.readline()
        a=a.split(delimiter)
        return len(a) if a is not None else 0

def concatenatecsv(addressesin, addressout,SkipOneLineButForFirstFile= False,verbose=False,constantcolnumber=False):
    nbcsv=0
    nbl=0
    of=open(addressout,"w")
    if constantcolnumber and len(addressesin)>0:
        nbcolref=comptecols(addressesin[0])
    for fname in addressesin:
        if constantcolnumber:
            nbcols=comptecols(fname)
            if nbcols>nbcolref:
                print "Mec t'as plus de colonnes dnas les fichiers du bas. Trie bien {}".format(fname)
                raise
            else:
                toadd=',""'*(nbcolref-nbcols)
        else:
            toadd=""
        nblines=0
        shouldiwrite=nbcsv==0 if SkipOneLineButForFirstFile else True
        with open(fname) as infile:
            for line in infile:
                if shouldiwrite:
                    of.write(''.join([line.strip("\r\n"), toadd, '\n']))
                    nblines+=1
                else:
                    shouldiwrite=True
        if verbose:
            print "textfilenumber " + str(nbcsv) + " nb lines written = " + str(nblines) 
        nbcsv+=1 if nblines>0 else 0
        nbl+=nblines
    print "total csv concatenated : {}, total number of lines : {}".format(nbcsv,nbl)

def removefirstline(inf,outf):
    with open(inf,'rb') as f:
        with open(outf,'wb') as f1:
            f.next() # skip header line
            for line in f:
                f1.write(line)


version=0.241


class BLS:
#Usage: 
    def __init__(self, df, keyproj1table, success="Product List Clicks", trial = "Product List Views", keyf2proj2=None,verbose=True):
        self.keyproj1=keyproj1table
        self.succol=success
        self.tricol=trial
        self.verbose=verbose
        self.keyf2proj2=keyf2proj2
        self.df=df
        self.HasAdjustment= keyf2proj2 is not None
        #cth only used in estimators, to give the rough 
        self.df["BLScth"]=df[self.tricol]*(1.0 if keyf2proj2 is None else df[keyf2proj2])
        
        self.df["BLSw"]=df[self.tricol]*(1.0 if keyf2proj2 is None else df[keyf2proj2]**2)
        self.df["BLSy"]=df[self.succol]/(df[self.tricol]*(1.0 if keyf2proj2 is None else df[keyf2proj2]))
        self.df["BLSwy"]=self.df["BLSy"]*self.df["BLSw"]
        self.df["BLSwy2"]=self.df["BLSy"]*self.df["BLSwy"]
        self.dfgpsum= self.df.groupby(keyproj1table).sum()
        self.dfsum=self.dfgpsum.sum()
        self.df["VarNonMesurable"]= self.df["BLSwy"] - self.df["BLSwy2"]
        self.VarNonMesurable=self.df["VarNonMesurable"].sum()
        self.dfgpsum["BLSY"]=self.dfgpsum["BLSwy"]/self.dfgpsum["BLSw"]
        self.dfgpsum["BLSsigma"]=1/np.sqrt(self.dfgpsum["BLSw"])
        self.dfsum["BLSY"]=self.dfsum["BLSwy"]/self.dfsum["BLSw"]
        self.dfsum["BLSsigma"]=1/np.sqrt(self.dfsum["BLSw"])
        #~ self.VarMesurable = self.dfsum["BLSwy2"] - (self.dfsum["BLSwy"]**2/ self.dfsum["BLSw"])
        #~ self.dfgpsum["VarMesuree"]=(self.dfgpsum["BLSw"]*(self.dfgpsum["BLSY"]-self.dfsum["BLSY"])**2)
        
        #~ #(df["BLSw"]*(df["BLSy"]-avg)**2).sum()
        #~ self.Vartotale = self.dfsum["BLSwy"] - (self.dfsum["BLSwy"]**2/ self.dfsum["BLSw"])
        #~ self.dfgpsum["VarNonMesuree"] = self.dfgpsum["BLSwy2"] - (self.dfgpsum["BLSwy"]**2/ self.dfgpsum["BLSw"])
        #~ #self.dfgpsum["VarIrred"] = self.dfgpsum["BLSwy"] - self.dfgpsum["BLSwy2"]
        #~ self.VarNonMesuree = self.dfgpsum["VarNonMesuree"].sum()
        #~ self.VarMesuree= self.dfgpsum["VarMesuree"].sum()
        #~ #self.VarIrred = self.dfgpsum["VarIrred"].sum()
        #~ print "Var Totale = " + "{0:.2f}".format(self.Vartotale)
        #~ print "Var Non Mesurable = " + "{0:.2f}".format(self.VarNonMesurable)+ "\t {0:.2f}%".format(100*self.VarNonMesurable/(self.Vartotale))
        #~ print "Var Mesurable = " + "{0:.2f}".format(self.VarMesurable)+ "\t {0:.2f}%".format(100*self.VarMesurable/(self.Vartotale))
        #~ print "VarNonMesuree = " + "{0:.2f}".format(self.VarNonMesuree)+ "\t {0:.2f}%".format(100*self.VarNonMesuree/self.VarMesurable)
        #~ print "VarMesuree = " + "{0:.2f}".format(self.VarMesuree)+ "\t {0:.2f}%".format(100*self.VarMesuree/self.VarMesurable)
        #~ #print "Var Irred = " + str(self.VarIrred)
        #~ #Var Total
        sumn=self.dfsum[self.succol]
        sumN=self.dfsum[self.tricol]
        self.VT2= sumn-(sumn**2)/float(sumN)
        if verbose:
            print "Total Var {}: {:.2f}".format("before preadj" if  self.HasAdjustment else "",self.VT2)
        #Variance Non measurable
        self.df["VNM2"]=self.df[self.succol]-(self.df[self.succol]**2)/(self.df[self.tricol])
        self.VNM2= self.df["VNM2"].sum()
        if verbose and not self.HasAdjustment:
            print "Non measurable Var : {0:.2f}".format(self.VNM2)
        self.VM2 = self.VT2-self.VNM2
        if verbose and not self.HasAdjustment:
            print "Measurable Var : {0:.2f}".format(self.VM2)
        #TotVarWitha : Total variance taking into account a :
        sumna=self.dfsum["BLSwy"]
        sumNa2=self.dfsum["BLSw"]
        self.VTWa=sumn-sumna**2/sumNa2
        if verbose and self.HasAdjustment:
            print "Total Var preadjusted : {0:.2f}".format(self.VTWa)
        #VarExplainedBya (can be negative in some extreme cases). VEa < VM2 obviously
        self.VEa=self.VT2-self.VTWa
        if verbose and self.HasAdjustment:
            print "Var Explained by adjustment : {0:.2f}".format(self.VEa)
        #Var Non measurable witha/Non measured with a
        self.df["VNMbWa"]=self.df[self.succol]-self.df["BLSwy"]**2/self.df["BLSw"]
        self.VNMbWa=self.df["VNMbWa"].sum()
        if verbose and self.HasAdjustment:
            print "Non measurable Var (adjusted) : {0:.2f}".format(self.VNMbWa)
        self.dfgpsum["VNMdWa"]=self.dfgpsum[self.succol]-self.dfgpsum["BLSwy"]**2/self.dfgpsum["BLSw"]
        self.VNMdWa=self.dfgpsum["VNMdWa"].sum()
        #Erreur mesurable /Measured :
        self.VMbWa=self.VTWa-self.VNMbWa
        if verbose and self.HasAdjustment:
            print "Measurable Var (Adjusted) : {0:.2f}".format(self.VMbWa)
        if verbose:
            print "Non Measured Var : {0:.2f}".format(self.VNMdWa)
        self.VMdWa=self.VTWa-self.VNMdWa
        if verbose:
            print "Measured Var : {0:.2f}".format(self.VMdWa)
    def estimators(self,astype="dict"):
        if astype=="dict":
            dicoe={}        
            for i in self.dfgpsum.index:
                dicoe[i]=(self.dfgpsum["BLSwy"][i]/self.dfgpsum["BLSw"][i],self.dfgpsum["BLScth"][i])
            return dicoe
        elif astype=="series":
            s=self.dfgpsum["BLSwy"]/self.dfgpsum["BLSw"]
            return s
        else:
            print "i'm out, not a good type : {}".format(astype)
            return 1/0
    
    
    def minimizesquareerr(self,approxfunction,guessparams=None):
        outputbls = curve_fit(approxfunction,self.dfgpsum.index,self.dfgpsum["BLSY"],p0=guessparams,sigma=self.dfgpsum["BLSsigma"],full_output=True)
        #print outputbls[0]
        self.residualbias= sum([err**2 for err in outputbls[2]["fvec"]])
        self.explainedvar= self.VMdWa-self.residualbias
        self.dfgpsum["prediction"]=approxfunction(self.dfgpsum.index, *outputbls[0])
        self.dfgpsum["errsq"]=self.dfgpsum["BLSw"]*(self.dfgpsum["prediction"]-self.dfgpsum["BLSY"])**2
        if self.verbose:
            print "Err sq Residuelle (biais) = " + "{0:.2f}".format(self.residualbias)+ "\t {0:.2f}%".format(100*self.residualbias/self.VMdWa)
            #print "Err sq Residuelle also = " + "{0:.2f}".format(self.dfgpsum["errsq"].sum())
            print "var expliquee = " + "{0:.2f}".format(self.explainedvar)+ "\t {0:.2f}%".format(100*self.explainedvar/self.VMdWa)
        self.outcurvefit = outputbls
        return outputbls + (self.VMdWa,self.explainedvar)
    def totvarmeasured(self):
        return self.VEa+self.VMdWa

class IdioEstimator:
    def __init__(self, df, IdioKey, Xcol, Ycol,GroupByKey=None,nameoutput=None):
       #GroupByKey must be hierarchically greater than IdioKey
       #Xcol and Ycol must be real numbers (Xcol is mainly suppposed to be weight so it should not be far from an integer)
       self.df = df.ix[:,[IdioKey,Xcol,Ycol] + ([GroupByKey] if GroupByKey!=None else [])]
       
       if GroupByKey==None:
           self.df["NoSubCategory"]="All"
           self.GroupByKey="NoSubCategory"
       else:
           self.GroupByKey=GroupByKey
       self.IdioKey=IdioKey
       self.coloutput=nameoutput if nameoutput!= None else ("IdioEst_"+self.IdioKey+"_"+self.GroupByKey)
       self.Xcol=Xcol
       self.Ycol=Ycol
       self.dfgpsum = self.df.groupby([self.GroupByKey,IdioKey], as_index=False)[Xcol,Ycol].sum()
       self.dfgpsum["PersonalEst"]=0.0
       self.dfgpsum.ix[self.dfgpsum[Xcol]>0,["PersonalEst"]]=self.dfgpsum[Ycol]/self.dfgpsum[Xcol]

       self.dfsum = self.df.groupby([self.GroupByKey], as_index=False)[Xcol,Ycol].sum()
       self.dfsum["CategoryEst"]=self.dfsum[Ycol]/self.dfsum[Xcol]
       self.dfsum.ix["CategoryEst"]=self.dfsum[Ycol]/self.dfsum[Xcol]
       self.dfsum["FullEst"]=self.dfsum.sum()[Ycol]/self.dfsum.sum()[Xcol]
       
       
    def ExtractScoresPoisson(self,fulloutput=False,facteuradjmoy=1.0):   #,capmult=2.0
       #facteuradjmoy is a way to adjust downward products with no significant.
    #Scores continually using the pvalue of lambda(omega)=lambda(p) as a weight of lambda(omega) yes we're like that refer to the paper that doesn't yet exist about idiosyncratic but it's not that muych of a paper in the sense it's not maths
       #Adjustment to diminish the impact of taking into account the estimator rather than a confidence interval. It adjusts pretty nice for a 95% conf int 
       #4.6 would be roughly a 99% CI 
       self.dfgpsum["PersonalEstAdj"]=np.maximum(self.dfgpsum[self.Ycol],3.0)/self.dfgpsum[self.Xcol]
       self.dfgpsum=pd.merge(self.dfgpsum, self.dfsum, on=[self.GroupByKey])
       #print self.dfgpsum.columns
       self.dfgpsum["pvaluepoiss"]=pvaluepoisson(self.dfgpsum[self.Ycol+"_x"],self.dfgpsum[self.Xcol+"_x"]*self.dfgpsum["CategoryEst"])
       KeyScore = self.coloutput
       self.dfgpsum["AdjFact"+KeyScore]=facteuradjmoy
       self.dfgpsum[KeyScore]=self.dfgpsum["CategoryEst"]*facteuradjmoy
       # New method : instead of personalising the estimator of all  self.dfgpsum[self.Xcol+"_x"]>0
       # we now want to have  self.dfgpsum[self.Xcol+"_x"]*self.dfgpsum["CategoryEst"]>1  or  self.dfgpsum[self.Ycol+"_x"] > 3
       # i.e. we use this method only if we expect 1 success or more, or if we have actually more than 3 successes.
       self.dfgpsum.ix[(self.dfgpsum[self.Xcol+"_x"]*self.dfgpsum["CategoryEst"]>1)  |  (self.dfgpsum[self.Ycol+"_x"] > 3),["AdjFact"+KeyScore]]=facteuradjmoy*(np.sqrt(self.dfgpsum[self.Ycol+"_x"])/self.dfgpsum[self.Xcol+"_x"])+(1.0-(np.sqrt(self.dfgpsum[self.Ycol+"_x"])/self.dfgpsum[self.Xcol+"_x"]))
       self.dfgpsum.ix[(self.dfgpsum[self.Xcol+"_x"]*self.dfgpsum["CategoryEst"]>1)  |  (self.dfgpsum[self.Ycol+"_x"] > 3),[KeyScore]]=(self.dfgpsum["PersonalEstAdj"] + (np.minimum(1.0,self.dfgpsum["pvaluepoiss"]*4.0))*(self.dfgpsum["CategoryEst"]-self.dfgpsum["PersonalEstAdj"]))*self.dfgpsum["AdjFact"+KeyScore]
       #self.dfgpsum[KeyScore]=np.maximum(np.minimum(self.dfgpsum["CategoryEst"]*capmult,self.dfgpsum[KeyScore]),self.dfgpsum["CategoryEst"]/capmult)
       if fulloutput:
           return self.dfgpsum
       else:
           return self.dfgpsum.ix[:,[self.IdioKey,self.coloutput]]
    def ExtractScoresSimpleAverageMethod(self,fulloutput=False):
        self.dfgpsum=pd.merge(self.dfgpsum, self.dfsum, on=[self.GroupByKey])
        self.dfgpsum[self.coloutput]=self.dfgpsum["PersonalEst"] + (1.0-np.minimum(1.0,self.dfgpsum[self.Xcol+"_x"]/10.0))*(self.dfgpsum["CategoryEst"]-self.dfgpsum["PersonalEst"])
        self.dfgpsum.ix[self.dfgpsum[self.coloutput].isnull(),[self.coloutput]]=self.dfgpsum["CategoryEst"]
        self.dfgpsum.ix[self.dfgpsum[self.coloutput].isnull(),[self.coloutput]]=self.dfgpsum["FullEst"]
        if fulloutput:
           return self.dfgpsum
        else:
           return self.dfgpsum.ix[:,[self.IdioKey,self.coloutput]]     
            
def pvaluepoisson(x,mu):
    #returns the pvalue of x, i.e. min(P(Y<=x),P(Y>=x) where Y is a poisson distribution of parameter lambda)
    return np.minimum(poisson.cdf(x,mu),1.0-poisson.cdf(x-1,mu))
              


#Returns the interpolation/extrapolation of the position of x in tablo assuming linear by parts function
def matchdouble(x,tablo):
    taille = len(tablo)
    #print "la longueur du x est {}".format(len(x))
    for i in range(taille-1):
        if np.logical_or(x<tablo[i+1],i==taille-2):
            return (x-tablo[i])/float(tablo[i+1]-tablo[i])+i


#indexdouble est l'unique prolongement lineaire par morceau sur la tribu definie par les intervalles [k,k+1] pour k dans [1;taille-1] de la fonction de N dans R qui a n associe tablo[n]
def indexdouble(x,tablo):
    taille=len(tablo)
    xint = np.maximum(0,np.minimum(int(x),taille-2))
    xfrac = x-xint
    return tablo[xint]+xfrac*(tablo[xint+1]-tablo[xint])


from googlesearch import GoogleSearch
import stackexchange
import re

def argmax(lst):
  return lst.index(max(lst))

def so2s(search):
    print "so2s is deprecated since google search API has been decommissionned :("
    return 0
##    site = stackexchange.Site(stackexchange.StackOverflow)
##    site.be_inclusive()
##    res="" #string to return
##    soq=None
##    stringsearch=search
##    toadd="site:stackoverflow.com "
##    stringsearch=toadd+stringsearch
##    gs=GoogleSearch(stringsearch)
##    topres=gs.top_url()
##    surl=topres.split()
##    qids=re.findall("/([0-9]+)/",topres)
##    if len(qids)==0:
##        res="sorry no question id found in google top res : {}".format(topres)
##    else:
##        qid=qids[0]
##        soq=site.question(qid)
##        reps=soq.answers
##        best=argmax([k.score for k in reps])
##        snipets=re.findall(u'<code>([\S\s\n]*?)<\/code>',reps[best].body)
##        res="\n".join(snipets)
##        #print reps[best].body
##    return res


import unicodedata

#

def remove_accents(mystr,original_coding='utf-8'):
    fh=mystr.decode(original_coding)
    fhm=unicodedata.normalize('NFKD',fh).encode('ASCII','ignore')
    return fhm


              
              
#Version notes:
#2015-10-06 : 0.0 : Created library. One function : concatenatecsv
#2015-11-24 : 0.1 : Added BLS Class for Bernouilli Least square Regression
#2015-11-26 : 0.11: "Clarification" of BLS Class that is now much much clearer.
#2015-12-08 : 0.12 : Introduction of IdioEstimator : (Continuous) Categorial Correction of Volumetry
#2016-01-13 : 0.2 :  Ajout d'un facteur d'ajustement dans l'IdioEstimator Poisson
#                    Creation de indexdouble et matchdouble
#2016-01-28 : my darling sister birthday, and also I added the "verbose" option to concatenatecsv
#2016-03-07 : 0.22 :  - add of functions : removefirtline, argmax, so2s
#2016-03-08 : 0.23 : add of function "fixednbcols" to concatcsv
#2016-04-18 : 0.24 : Tweaked the best estimator to go to category estimator if it has less than 1 expected success
#2016-08-24 : 0.241 : added the astype option to BLS.estimators
#2016-08-30 : 0.25 :  Added remove_accents + commented so2s

#Exercises
#0-Improve BLS to display likelihood of modelisation found w.r.t likelihood of natural estimators. 
#Use it to iterate regression and check if/how it improves model precision
