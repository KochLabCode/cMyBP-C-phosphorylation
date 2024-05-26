# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 17:17:10 2022


This code contains essential functions required to reproduce the analyses
and simulation results of the paper:

Thomas Kampourakis, Saraswathi Ponnam, Daniel Koch (2023):
The cardiac myosin binding protein-C phosphorylation state 
as a function of multiple protein kinase and phosphatase activities 
Preprint available under: https://doi.org/10.1101/2023.02.24.529959 


Code by Daniel Koch, 2021-2023
"""

import numpy as np 
import pandas as pd
import random as rnd


def odeRK4(fun,ICs,p,t_0,t_end,stepsize,naFun=None,naFunParams=None):
    
        # numerical integration of model using the 4th order Runge-Kutta scheme
        # args: ODE system, parameters, initial conditions, 
        # starting time t0, stepsize, number of steps 
        
        steps = int(t_end/stepsize)   
        x = np.zeros([steps,len(ICs)])
        t = np.zeros(steps)
        x[0,:] = ICs
        t[0] = t_0
        
        if naFun == None and naFunParams == None: # autonomous system
            for i in range(1,steps):
                t[i] = t_0 + i*stepsize
                k1 = fun(t[i-1],x[i-1,:],p)*stepsize
                k2 = fun(t[i-1],x[i-1,:]+k1/2,p)*stepsize
                k3 = fun(t[i-1],x[i-1,:]+k2/2,p)*stepsize
                k4 = fun(t[i-1],x[i-1,:]+k3,p)*stepsize
                x_next = x[i-1,:] + (k1+2*k2+2*k3+k4)/6
                x[i,:] = x_next
        elif naFun != None: # non-autonomous system
            for i in range(1,steps): 
                t[i] = t_0 + i*stepsize
                k1 = fun(t[i-1],x[i-1,:],p,naFun,naFunParams)*stepsize
                k2 = fun(t[i-1],x[i-1,:]+k1/2,p,naFun,naFunParams)*stepsize
                k3 = fun(t[i-1],x[i-1,:]+k2/2,p,naFun,naFunParams)*stepsize
                k4 = fun(t[i-1],x[i-1,:]+k3,p,naFun,naFunParams)*stepsize
                x_next = x[i-1,:] + (k1+2*k2+2*k3+k4)/6
                x[i,:] = x_next
                
        return x.T 
    
  
def fraction(x,species,model=1): 
    # returns relative fractions of n-times phosphorylated cMyBP-C
    # for model version < 4, input x is array containing 
    # species P0,A,AB,ABG,D,AD,ABD,ABGD. For model version >= 4,
    # input x is array containing species P0,A,At,AB,ABG,D,AD,ABD,ABGD.
    
    if model < 4:
        if species == '0P':
            f = (x[0,:])/(np.sum(x,0))
        elif species == '1P':
            f = (x[1,:]+x[4,:])/(np.sum(x,0))
        elif species == '2P':
            f = (x[2,:]+x[5,:])/(np.sum(x,0))
        elif species == '3P':
            f = (x[3,:]+x[6,:])/(np.sum(x,0)) 
        elif species == '4P':
             f = (x[7,:])/(np.sum(x,0)) 
        
    if model >= 4 : 
        if species == '0P':
            f = (x[0,:])/(np.sum(x,0))
        elif species == '1P':
            f = (x[1,:]+x[2,:]+x[5,:])/(np.sum(x,0))
        elif species == '2P':
            f = (x[3,:]+x[6,:])/(np.sum(x,0))
        elif species == '3P':
            f = (x[4,:]+x[7,:])/(np.sum(x,0)) 
        elif species == '4P':
             f = (x[8,:])/(np.sum(x,0)) 
             
    return f

#%% analysis and processing of fitted parameter sets

def meanSqrtErr(expDat,simDat,exp_ids):
    mse = []
    for p in range(simDat.shape[0]):
        mse_paramset = []
        for n in exp_ids:
            mse_species = []
            for ii in range(5):
                if len(exp_ids) > 1:
                    errors = ((simDat[p,n,ii,:] - expDat[n][ii,:])**2)
                    mse_species.append(errors.mean(axis=None))
                else:
                    errors = ((simDat[p,0,ii,:] - expDat[n][ii,:])**2)
                    mse_species.append(errors.mean(axis=None))         
            mse_paramset.append(np.asarray(mse_species).mean(axis=None))
        mse.append(np.asarray(mse_paramset))
    mse = np.asarray(mse)
    return mse

def filterParamSets(error, xSD_cutoff, expDat = np.array([]), simDat = np.array([]), expIds = [], up_bnd = 0):
    
    idx_excl = np.array([])
    idx_incl = np.array([])
    
    if error.ndim > 1:

        for n in range(error.shape[1]):
            error_norm = error[:,n]/error[:,n].mean(axis=None)
            cutoff = error_norm.mean(axis=None)+xSD_cutoff[n]*np.std(error_norm)
            idx_excl = np.hstack((idx_excl,np.where(error_norm > cutoff)[0][:]))   
        
        idx_excl = np.unique(idx_excl)
        idx_excl = idx_excl.astype(int)   
        idx_incl = np.asarray(range(error.shape[0]))
        idx_incl = np.setdiff1d(idx_incl,idx_excl)
        
    else:
        
        error_norm = error[:]/error[:].mean(axis=None)
        cutoff = error_norm.mean(axis=None)+xSD_cutoff*np.std(error_norm)
        idx_excl = np.where(error_norm > cutoff)[0][:]
        idx_excl = idx_excl.astype(int)   
        idx_incl = np.asarray(range(error.shape[0]))
        idx_incl = np.setdiff1d(idx_incl,idx_excl)
       
    maxValsSim = []
    maxValsExp = []
    idx_excl_max = []
    
    if expDat.shape[0] > 0 and simDat.shape[0] > 0:
                
        for i in range(simDat.shape[0]):
            for ii in range(simDat.shape[1]):
                for iii in range(simDat.shape[2]):
                    maxValsSim.append(np.max(simDat[i,ii,iii,:]))
        
        maxValsSim = np.reshape(maxValsSim,[simDat.shape[0],simDat.shape[1],simDat.shape[2]])   
        
        for i in range(expDat.shape[0]):
            for ii in range(expDat.shape[1]):
                maxValsExp.append(np.max(expDat[i,ii,:]))       
        maxValsExp = np.reshape(maxValsExp,[expDat.shape[0],expDat.shape[1]])

        for i in range(maxValsSim.shape[0]):
            for ii in range(len(expIds)):
                for iii in range(maxValsSim.shape[2]):
                    if maxValsSim[i,expIds[ii],iii] <= maxValsExp[expIds[ii],iii]+up_bnd[ii] and maxValsSim[i,expIds[ii],iii] >= maxValsExp[expIds[ii],iii]-up_bnd[ii]:
                        pass
                    else:
                        idx_excl_max.append(i)
        
        idx_excl_max = np.unique(idx_excl_max)
        
        idx_excl = np.union1d(idx_excl,idx_excl_max)
        idx_incl = np.setdiff1d(np.asarray(range(simDat.shape[0])),idx_excl)
        
    return idx_incl, idx_excl

def reconkK2225(params):
    params[:,23] = np.multiply(params[:,23],params[:,2]) #calculate k22 by multiplying k1 with scaling factor
    params[:,26] = np.multiply(params[:,26],params[:,5]) #calculate k25 by multiplying k4 with scaling factor
    params[:,53] = np.multiply(params[:,53],params[:,32]) #calculate K22 by multiplying K1 with scaling factor
    params[:,56] = np.multiply(params[:,56],params[:,35]) #calculate K25 by multiplying K4 with scaling factor
    return params   


def AIC(error,k,n): 
    r = 2*k + n*(np.log(error/n) + 1 ) + 2*k*(k+1)/(n-k-1)
    return r

#%% data analysis

def numDerivative(x,y):
    nd = []
    if len(x) == len(y) and len(x) > 1:
        for i in range(len(x)-1):
            nd.append((y[i+1]-y[i])/(x[i+1]-x[i]))
        return nd
    else:
        print("Invalid input for function numDerivative")
        
def akimaIntp(x,y,xnew):
    ynew = []
    for i in xnew:
        if i in x:
            idx = np.where(x == i)[0][0]
            ynew.append(y[idx])
        else:
            ynew.append(None)
    df = pd.DataFrame({'X': xnew,'Y': ynew})
    dfIntp = df.interpolate(method='akima')
    return np.array(dfIntp['Y'])


def intpExpDat(x, y, xnew, nReps):
    z = []
    imax = int(y.shape[1]/nReps)
    for i in range(imax):
        ymean = np.mean(y[:,i*nReps:i*nReps+nReps],axis=1)
        yintp = akimaIntp(x,ymean,xnew)
        z.append(yintp)
    z = np.asarray(z)   
    z[z<0]=0
    return z

def hillEQ(x, n, K): # for fitting steady state dose response data
    y = x**n/(x**n + K**n)
    return y

def mmEQ(S, Vmax, Km): # for fitting Michaelis Menten assay data
    y = Vmax*S/(S+Km)
    return y

def bindingEQ(x,targetConc,unbound,bound,Kd): # for fitting MST binding data
    y = unbound + ((bound-unbound)*(x+targetConc+Kd-np.sqrt((x+targetConc+Kd)**2-4*x*targetConc)))/(2*targetConc)
    return y
        
        
#%% Functions for non-autonomous systems and generating time-varying signals        
        
def sig2array(sig,t,sz):
    length = int(t/sz)
    a = np.array([])
    for i in range(length):
        s = 0
        for ii in range(0,len(sig),2):
            if i*sz >= sig[ii] and i*sz <= sig[ii+1]:
                s = 1
        a = np.append(a,s)
    return a

def sigArray(x,f,p):
    a = []
    for i in x: a.append(f(i,p))
    return np.asarray(a)

def sigGenFun(nr_of_pulses, pulse_dur, pause_dur, p_shuffle, t_first, t_end):
    s = []
    for i in range(1,nr_of_pulses+1):
        dice = rnd.random()
        if dice < p_shuffle:
            s_start = t_first+(i-1)*(pulse_dur+pause_dur)
            s_stop = t_first+(i-1)*(pulse_dur+pause_dur)+pulse_dur
            s.append(s_start)
            s.append(s_stop)
        else:
            new_pos = rnd.randint(0, t_end)
            s_start = new_pos 
            s_stop = new_pos+pulse_dur
            s.append(s_start)
            s.append(s_stop)           
    s.sort()
    return np.array(s)

def fromIntv(t,intv):
    for i in range(0,len(intv),2):
        if t>=intv[i] and t<=intv[i+1]:
            return 1
    return 0

def timeGaussian(time,m,s,f):
    x = []
    m0 = m
    for t in range(len(time)):
        if t>0 and t%f == 0:
            m_next = np.random.normal(m,s)
            x.append(m_next)
            m0 = m_next
        else:
            x.append(m0)   
    return np.asarray(x)

def fromArray(t,p):
    x,a = p
    i = np.where(x==t)[0][0]
    return a[i]

def pulses_decaying(t,p):
    intv, k = p
    x = 0
    for i in range(0,len(intv),2):
        if t>=intv[i]:
            if t<intv[i+1]:
                x = 1
            else:
                x = np.exp(k*(t-intv[i+1]))
    return x