# -*- coding: utf-8 -*-

"""
This code generates the comparison results between model simulations/fits and experimental 
data shown in Figures 2c and 2e, Figure 3g, Supplementary Figures 2-7, 9-10 and 13-15 
of the publication:

Thomas Kampourakis, Saraswathi Ponnam, Kenneth S. Campbell, Austin Wellette-Hunsucker, 
Daniel Koch (2024): The cardiac myosin binding protein-C phosphorylation state as a 
function of multiple protein kinase and phosphatase activities.
Nature Communcations (forthcoming)

README:
Before running this script, make sure that the files 'functions_cMyBPC.py',
'models_cMyBPC.py' and the folders "parametersets" (containing the parameter sets 
for the models) and "experimental data" (containing the experimental data
formatted for plotting) are in the same directory as this script. Additionally, if you
wish to plot results from previous simulations with fitted parameters  (i.e. if the
setting 'loadData' is set to True), the folder "simulation data" and the corresponding
data files are required.

Code by Daniel Koch, 2021-2024
"""

#%% cell 0: Import and misc settings
import os
import sys

#paths
os.chdir(os.path.dirname(os.path.abspath(__file__)))
fileDirectory = os.path.dirname(os.path.abspath(__file__))
path_simdat = os.path.join(fileDirectory, 'simulation data')   
path_figures = os.path.join(fileDirectory, 'figures')   
if not os.path.exists(path_figures):
    os.makedirs(path_figures)
path_expdat = os.path.join(fileDirectory, 'experimental data')  
path_paramsets = os.path.join(fileDirectory, 'parametersets')
 
sys.path.append(fileDirectory)


import models_cMyBPC as mod 
import functions_cMyBPC as fun
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy import stats
import warnings
warnings.filterwarnings("error")
plt.rcParams.update({'font.family':'Arial'})

saveFigs = True # save figures as files
loadData = True # load result from previous simulations if available 
saveData = True # data of simulations for comparison are saved  
plotFigures = True # plot results from simulations


# define colors for plotting
cmap = cm.get_cmap('gnuplot2',7)
colV = []
for i in [0,0.3,0.5,0.6,0.8]: colV.append(cmap(i)[:3])
c4P,c3P,c2P,c1P,c0P = colV
xPstr = ['4P','3P','2P','1P','0P']

# dictionary for storing AIC scores
AIC = {}


datFlNm = [
    os.path.join(path_expdat, 'exp1_plotting.txt'), # ABD/ABGD + PP1      0
    os.path.join(path_expdat, 'exp2_plotting.txt'), # ABD/ABGD + PP2A     1
    os.path.join(path_expdat, 'exp3_plotting.txt'), # ABG + PP1           2
    os.path.join(path_expdat, 'exp4_plotting.txt'), # ABD + PP1           3
    os.path.join(path_expdat, 'exp5_plotting.txt'), # AB + PP1            4
    os.path.join(path_expdat, 'exp6_plotting.txt'), # AD + PP1            5
    os.path.join(path_expdat, 'exp7_plotting.txt'), # ABG                 6
    os.path.join(path_expdat, 'exp8_plotting.txt'), # ABD + PP2A          7
    os.path.join(path_expdat, 'exp9_plotting.txt'), # AB + PP2A           8
    os.path.join(path_expdat, 'exp10_plotting.txt'), # AD + PP2A          9
    os.path.join(path_expdat, 'exp11_plotting.txt'), # 0P + PKA           10
    os.path.join(path_expdat, 'exp12_plotting.txt') # D + PKA             11
    ]

expNames = ['ABD-ABGD+PP1','ABD-ABGD+PP2A','ABG+PP1','ABD+PP1','AB+PP1','AD+PP1','ABG+PP2A','ABD+PP2A','AB+PP2A','AD+PP2A','0P+PKA','D+PKA']
expReps = [3,3,2,2,2,2,2,2,2,2,6,4]


exp_ICs = np.array([  #P0,A,AB,ABG,D,AD,ABD,ABGD
    [0,0,0,0,0,0,0.5*2.21038e-5,0.5*1.78962e-5],
    [0,0,0,0,0,0,0.5*2.21038e-5,0.5*1.78962e-5],
    [0,0,0,2e-5,0,0,0,0],
    [0,0,0,0,0,0,2e-5,0],
    [0,0,2e-5,0,0,0,0,0],
    [0,0,0,0,0,2e-5,0,0],
    [0,0,0,2e-5,0,0,0,0],
    [0,0,0,0,0,0,2e-5,0],
    [0,0,2e-5,0,0,0,0,0],
    [0,0,0,0,0,2e-5,0,0],
    [4e-5,0,0,0,0,0,0,0],
    [0,0,0,0,4e-5,0,0,0],
    ]) 

c_enzymes_exp = np.array([  #PKA, PKC, PP1, PP2A
    [0,0,1e-7,0],
    [0,0,0,1e-7],
    [0,0,1e-7,0],
    [0,0,1e-7,0],
    [0,0,1e-7,0],
    [0,0,1e-7,0],
    [0,0,0,1e-7],
    [0,0,0,1e-7],
    [0,0,0,1e-7],
    [0,0,0,1e-7],
    [2.46184e-9,0,0,0],
    [2.46184e-9,0,0,0],
    ])    


# Interpolation of experimental data
expDat = []
expDat_interpol = []
time_exp = []
time_intp = list(range(0,3601))

for n in range(12):
    dataRaw = np.loadtxt(datFlNm[n],delimiter='\t',dtype=str)
    dataClean = np.asarray(dataRaw[1:,1:],dtype='float')
    t_exp = np.asarray(dataRaw[1:,0],dtype='float')*60
    intpDat = fun.intpExpDat(t_exp,dataClean,time_intp,expReps[n])
    
    expDat.append(dataClean)
    expDat_interpol.append(intpDat)
    time_exp.append(t_exp)
    
# indices of reactions/experiments for dephosphorylation by PP1 only
    
rxsPP1 = [ 2,  5,  8, 11, 14, 17, 20, 23, 26, 29]
exp_ids_PP1 = [0,2,3,4,5]

#calculate nr of datapoints per experiment
n_obs = []
for i in range(len(expDat)):
    data = expDat[i].T
    data = data[~np.all(data == 0, axis=1)]
    n_obs.append(data.shape[0]*data.shape[1])

n_obs_PP1only = []
for i in exp_ids_PP1:
    data = expDat[i].T
    data = data[~np.all(data == 0, axis=1)]
    n_obs_PP1only.append(data.shape[0]*data.shape[1])
    
#%% cell 2: Plotting Functions


def plot_simNexp(expIds, idx_incl, idx_excl, model_nr = 1, plotData = 'all', plotPP1 = True, **kwargs):

    if "tQSSA" in kwargs:
        tQSSA = kwargs["tQSSA"]
    else:
        tQSSA = False
        
    # plot simulated data for each parameterset, color coded by exclusion status
    # blue = included, red = excluded

    for i in range(2):
        if i == 0:
            pcolor = 'r'
            c_alpha = 0.2
            rg = idx_excl
        else:
            pcolor = 'b'
            c_alpha = 0.33
            rg = idx_incl
        for p in rg:
            for n in expIds:                
                plt.figure(n,figsize=(22,3))
                for ii in range(5):
                    plt.subplot(1,5,ii+1)
                    plt.plot(time,fun.fraction(simDat[p,n,:,:],xPstr[ii], model_nr),color=pcolor,alpha=c_alpha,lw=1)             
                if plotPP1 == True: 
                    if n == 0:
                        if p in idx_incl:
                            plt.figure(13,figsize=(8,3.3))
                            plt.subplot(1,2,1)
                            for ii in range(5):
                                plt.plot(time,fun.fraction(simDat[p,n,:,:],xPstr[ii],model_nr),color=colV[ii], alpha=0.5, lw=1)        
                    elif n == 5:
                        if p in idx_incl:
                            plt.figure(13,figsize=(8,3.3))
                            plt.subplot(1,2,2)
                            plt.plot(time,fun.fraction(simDat[p,n,:,:],'0P',model_nr),color=c0P, alpha=0.5, lw=1)        
                            plt.plot(time,fun.fraction(simDat[p,n,:,:],'1P',model_nr),color=c1P, alpha=0.5, lw=1)   
                            plt.plot(time,fun.fraction(simDat[p,n,:,:],'2P',model_nr),color=c2P, alpha=0.5, lw=1) 
                            plt.plot(time,fun.fraction(simDat[p,n,:,:],'3P',model_nr),color=c3P, alpha=0.5, lw=1) 
                            plt.plot(time,fun.fraction(simDat[p,n,:,:],'4P',model_nr),color=c4P, alpha=0.5, lw=1)
                        
    # plot experimental data
    for i in range(1,6):
        for n in expIds: 
            plt.figure(n,figsize=(22,3))
            plt.subplot(1,5,i)
            plt.title(str(5-i)+"P cMyBPC", fontdict={'fontweight':'bold','fontsize':16})
            plt.plot(time_intp,expDat_interpol[n][i-1,:],':k',lw=5)
            means = np.mean(expDat[n][:,(i-1)*expReps[n]:(i-1)*expReps[n]+expReps[n]],1)
            SDs = np.std(expDat[n][:,(i-1)*expReps[n]:(i-1)*expReps[n]+expReps[n]],1)
            plt.errorbar(time_exp[n],means,yerr=SDs,fmt='o', mfc='w', ecolor = 'k', mec ='k', capsize = 5, ms=10)
            if i == 1:
                plt.ylabel("fraction",fontsize=16)
            plt.ylim(0,1)
            plt.yticks([0,0.5,1],fontsize=13)
            plt.xticks(fontsize=13)
            plt.xlabel("time (s)",fontsize=16)
            
            if plotPP1 == True:            
                if n == 0:
                    plt.figure(13,figsize=(7,3))
                    plt.subplot(1,2,1)
                    plt.plot(time_intp,expDat_interpol[n][i-1,:],':',color=colV[i-1],lw=5)
                    plt.errorbar(time_exp[n],means,yerr=SDs,fmt='o', mfc=colV[i-1], ecolor = 'k', mec ='k', capsize = 5, ms=10)
                    plt.ylabel("fraction",fontsize=16)
                    plt.ylim(0,1)
                    plt.yticks([0,0.5,1],fontsize=13)
                    plt.xticks(fontsize=13)
                    plt.xlabel("time (s)",fontsize=16)
                elif n == 5:
                    plt.figure(13,figsize=(7,3))
                    plt.subplot(1,2,2)
                    plt.plot(time_intp,expDat_interpol[n][i-1,:],':',color=colV[i-1],lw=5)
                    plt.errorbar(time_exp[n],means,yerr=SDs,fmt='o', mfc=colV[i-1], ecolor = 'k', mec ='k', capsize = 5, ms=10)
                    plt.ylim(0,1)
                    plt.yticks([0,0.5,1],fontsize=13)
                    plt.xticks(fontsize=13)
                    plt.xlabel("time (s)",fontsize=16)              
          
    if saveFigs == True:
        if tQSSA == False:
            for n in expIds:
                plt.figure(n)
                if plotData == 'PP1':
                    print("figure "+'model'+str(model_nr)+'_'+expNames[n]+'_PP1_only.svg'+" saved")
                    plt.savefig(os.path.join(path_figures,'model'+str(model_nr)+'_'+expNames[n]+'_PP1_only.svg'), bbox_inches = "tight")
                else:
                    print("figure "+'model'+str(model_nr)+'_'+expNames[n]+'.svg'+" saved")
                    plt.savefig(os.path.join(path_figures,'model'+str(model_nr)+'_'+expNames[n]+'.svg'), bbox_inches = "tight")
            
            if plotPP1 == True:  
                plt.figure(13)
                print("figure "+'model'+str(model_nr)+'_ABCDvsAD.svg'+" saved")
                plt.savefig(os.path.join(path_figures, 'model'+str(model_nr)+'_ABCDvsAD.svg'), bbox_inches = "tight")
        if tQSSA == True:
            for n in expIds:
                plt.figure(n)
                if plotData == 'PP1':
                    print("figure "+'model'+str(model_nr)+'_tQSSA_'+expNames[n]+'_PP1_only.svg'+" saved")
                    plt.savefig(os.path.join(path_figures,'model'+str(model_nr)+'_tQSSA_'+expNames[n]+'_PP1_only.svg'), bbox_inches = "tight")
                else:
                    print("figure "+'model'+str(model_nr)+'_tQSSA_'+expNames[n]+'.svg'+" saved")
                    plt.savefig(os.path.join(path_figures,'model'+str(model_nr)+'_tQSSA_'+expNames[n]+'.svg'), bbox_inches = "tight")
            
            if plotPP1 == True:  
                plt.figure(13)
                print("figure "+'model'+str(model_nr)+'_tQSSA_ABCDvsAD.svg'+" saved")
                plt.savefig(os.path.join(path_figures, 'model'+str(model_nr)+'_tQSSA_ABCDvsAD.svg'), bbox_inches = "tight")

    plt.show()
            
def plot_paramDistrPP1(modelStr, idx_incl):
    
    idk = np.asarray(rxsPP1)+1
    idK = np.asarray(rxsPP1)+32
    
    plt.figure(14, figsize=(5.75,8))
    plt.subplot(3,1,1)
    plt.title(modelStr + ', PP1 data only, rate constants')
    for i in idx_incl:
        plt.plot(paramsHJ[i,idk].T, 'ok',alpha=0.15,ms=5)
    plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks(np.arange(len(rxsPP1)))
    xlabs = []
    
    for i in rxsPP1:
        xlabs.append('k'+str(i))
    ax.set_xticklabels(xlabs)
    plt.ylabel("parameter value ($s^{-1}$)")
        
    plt.subplot(3,1,2)
    plt.title(modelStr + ', PP1 data only, Michaelis constants')
    for i in idx_incl:
        plt.plot(paramsHJ[i,idK].T, 'ok',alpha=0.15,ms=5)
    plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks(np.arange(len(rxsPP1)))
    xlabs = []
    for i in rxsPP1:
        xlabs.append('K'+str(i))
    ax.set_xticklabels(xlabs)  
    plt.ylabel("parameter value ($M$)")
    plt.tight_layout()
        
    plt.subplot(3,1,3)
    plt.title(modelStr + ', PP1 data only, specificty constants')
    for i in idx_incl:
        plt.plot(paramsHJ[i,idk].T/paramsHJ[i,idK].T, 'ok',alpha=0.15,ms=5)
    plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks(np.arange(len(rxsPP1)))
    xlabs = []
    for i in rxsPP1:
        xlabs.append('r'+str(i))
    ax.set_xticklabels(xlabs)  
    plt.ylabel("$k_{cat}/K_m$ ($Ms^{-1}$)")
    plt.tight_layout()
    
    if saveFigs == True:
        plt.figure(14)
        print("figure "+modelStr+'_'+'_paramDistr_PP1.svg'+" saved")
        plt.savefig(os.path.join(path_figures,modelStr+'_'+'_paramDistr_PP1.svg'), bbox_inches = "tight")
        
def plot_paramDistr(modelStr, idx_incl):
    
    plt.figure(14, figsize=(11,8))
    plt.subplot(3,1,1)
    plt.title(modelStr + ', all experiments, rate constants')
    plt.plot(paramsHJ[idx_incl,2:32].T, 'ok',alpha=0.15,ms=5)
    plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks(np.arange(30))
    xlabs = []
    
    for i in range(30):
        xlabs.append('k'+str(i+1))
    ax.set_xticklabels(xlabs)
    plt.ylabel("parameter value ($s^{-1}$)")
        
    plt.subplot(3,1,2)
    plt.title(modelStr + ', all experiments, Michaelis constants')
    plt.plot(paramsHJ[idx_incl,32:62].T, 'ok',alpha=0.15,ms=5)
    plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks(np.arange(30))
    xlabs = []
    for i in range(30):
        xlabs.append('K'+str(i+1))
    ax.set_xticklabels(xlabs)  
    plt.ylabel("parameter value ($M$)")
    plt.tight_layout()
        
    plt.subplot(3,1,3)
    plt.title(modelStr + ', all experiments, specificty constants')
    plt.plot(paramsHJ[idx_incl,2:32].T/paramsHJ[idx_incl,32:62].T, 'ok',alpha=0.15,ms=5)
    plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks(np.arange(30))
    xlabs = []
    for i in range(30):
        xlabs.append('r'+str(i+1))
    ax.set_xticklabels(xlabs)  
    plt.ylabel("$k_{cat}/K_m$ ($Ms^{-1}$)")
    plt.tight_layout()
    
    if saveFigs == True:
        plt.figure(14)
        print("figure "+modelStr+'_'+'_paramDistr.svg'+" saved")
        plt.savefig(os.path.join(path_figures, modelStr+'_'+'_paramDistr.svg'), bbox_inches = "tight")

def plot_MSEdistr(modelStr, expIDs, mse, cutoffs):
    plt.figure(333,figsize=(10,7))
    plt.figure(333).suptitle('Experimental error distributions ' + modelStr)
    for n in expIDs:
        plt.subplot(3,4,n+1)
        mse_norm = mse[:,n]/mse[:,n].mean(axis=None)
        mse_norm[np.where(mse_norm>2)] = 2
        plt.hist(mse_norm,25)
        cutoff = mse_norm.mean(axis=None)+cutoffs[n]*np.std(mse_norm)
        plt.vlines(cutoff, 0, nr_paramsets, 'r', lw=2)
        plt.title("Experiment "+str(n))
        plt.xlabel("mean squared error")
    plt.tight_layout()
    
def plot_MSEdistrPP1(modelStr, expIDs, mse, cutoffs):
    plt.figure(333,figsize=(10,7))
    plt.figure(333).suptitle('Experimental error distributions ' + modelStr)
    for i in range(len(expIDs)):
        plt.subplot(3,4,expIDs[i]+1)
        mse_norm = mse[:,expIDs[i]]/mse[:,expIDs[i]].mean(axis=None)
        plt.hist(mse_norm)
        cutoff = mse_norm.mean(axis=None)+cutoffs[i]*np.std(mse_norm)
        plt.vlines(cutoff, 0, nr_paramsets, 'r', lw=2)
        plt.title("Experiment "+str(expIDs[i]))
        plt.xlabel("mean squared error")
    plt.tight_layout()
    
#%% cell 3: Model 1 - all experiments, Figure 2c, and Supplementary Figures 3-5

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model1_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model1_HJ.npy'))

paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]

if loadData == False:   
    for p in range(nr_paramsets):
        print(p)
        for n in range(12):
        
            ICs = exp_ICs[n]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            
            params = [k,K,c_enzymes_exp[n]]
            output = fun.odeRK4(mod.cMyBPC_model1,ICs,params,t0,tend+1,h)
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P'),
                fun.fraction(output,'3P'),
                fun.fraction(output,'2P'),
                fun.fraction(output,'1P'),
                fun.fraction(output,'0P'),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,8,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat,'simDat_rel_fracs_m1.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat,'simDat_m1.npy'),simDat)
else:
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m1.npy'))
    simDat = np.load(os.path.join(path_simdat,'simDat_m1.npy'))

# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse_m1 = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 
cutoffs = [1,1.5,1.5,1.5,1.5,0.25,
            1.5,1.5,1.5,1.5,1.5,1.5]

# indices of parametersets that are to be included/ excluded
idx_incl_m1, idx_excl_m1 = fun.filterParamSets(mse_m1, cutoffs) 

# filtering included PKA parametersets only - for model 4
cutoffs_PKA = [1.5,1.5]
idx_incl_m1_PKA, idx_excl_m1_PKA = fun.filterParamSets(mse_m1[:,[10,11]], cutoffs_PKA) 

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistr('model 1, all experiments', range(12), mse_m1, cutoffs)

# calculate the AIC values for included parametersets of model 1

mse_avg = np.mean(mse_m1,axis=1)

AICs = []
for i in range(len(mse_avg)):
    AICs.append(fun.AIC(mse_avg[i], paramsHJ.shape[1], sum(n_obs)))
AICs = np.asarray(AICs)
AIC['model 1, all data'] = AICs[idx_incl_m1]

if plotFigures:
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(range(12),idx_incl_m1, idx_excl_m1, 1)
    plot_paramDistr('model 1', idx_incl_m1)
    

# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#%% cell 4: Model 1 - PP1 data only. Supplementary Figures 6 and 8

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model1_PP1_only_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model1_PP1_only_HJ.npy'))

paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

# loadData=False
# saveData=True


# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]

if loadData == False:   
    for p in range(nr_paramsets):
        print('simulations model 1 for PP1 data '+str(100*p/nr_paramsets)+'% complete.')
        for n in range(12):
        
            ICs = exp_ICs[n]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            
            params = [k,K,c_enzymes_exp[n]]
            output = fun.odeRK4(mod.cMyBPC_model1,ICs,params,t0,tend+1,h)
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P'),
                fun.fraction(output,'3P'),
                fun.fraction(output,'2P'),
                fun.fraction(output,'1P'),
                fun.fraction(output,'0P'),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,8,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat, 'simDat_rel_fracs_m1_pp1.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat, 'simDat_m1_pp1.npy'),simDat)
else:
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m1_pp1.npy'))
    simDat = np.load(os.path.join(path_simdat,'simDat_m1_pp1.npy'))

# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 
cutoffs = [1.5,1.5,1.5,1.5,0]

# indices of parametersets that are to be included/ excluded
idx_incl, idx_excl = fun.filterParamSets(mse[:,exp_ids_PP1], cutoffs) 

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistrPP1('model 1, PP1 data only', exp_ids_PP1, mse, cutoffs)

# calculate the AIC values for included parametersets of model 1

mse_avg_PP1only = np.mean(mse[:,exp_ids_PP1],axis=1)

AICs = []
for i in range(len(mse_avg_PP1only)):
    AICs.append(fun.AIC(mse_avg_PP1only[i], len(rxsPP1)*2, sum(n_obs_PP1only)))
AICs = np.asarray(AICs)
AIC['model 1, pp1 data'] = AICs[idx_incl]

if plotFigures:
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(exp_ids_PP1,idx_incl, idx_excl,1,'PP1',False)
    plot_paramDistrPP1('model 1',idx_incl)


# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#%% cell 5: Model 2 - PP1 data only, Supplementary Figures 7 and 8

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model2_PP1_only_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model2_PP1_only_HJ.npy'))

paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

loadData=True
saveData=False

# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]
if loadData == False:   
    for p in range(nr_paramsets):
        print('simulations model 2 for PP1 data '+str(100*p/nr_paramsets)+'% complete.')
        for n in range(12):
        
            ICs = exp_ICs[n]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            additionalParams = paramsHJ[p,62:]
            params = [k,K,additionalParams,c_enzymes_exp[n]]
            output = fun.odeRK4(mod.cMyBPC_model2,ICs,params,t0,tend+1,h)
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P'),
                fun.fraction(output,'3P'),
                fun.fraction(output,'2P'),
                fun.fraction(output,'1P'),
                fun.fraction(output,'0P'),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,8,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat, 'simDat_rel_fracs_m2_pp1.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat, 'simDat_m2_pp1.npy'),simDat)
else:    
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m2_pp1.npy'))
    simDat = np.load(os.path.join(path_simdat, 'simDat_m2_pp1.npy'))

# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 
cutoffs = [1.5,1.5,1.5,0,0]

# indices of parametersets that are to be included/ excluded
idx_incl, idx_excl = fun.filterParamSets(mse[:,[0,2,3,4,5]], cutoffs) 

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistrPP1('model 2, PP1 data only', exp_ids_PP1, mse, cutoffs)

# calculate the AIC values for included parametersets of model 2

mse_avg_PP1only = np.mean(mse[:,exp_ids_PP1],axis=1)

AICs = []
for i in range(len(mse_avg_PP1only)):
    AICs.append(fun.AIC(mse_avg_PP1only[i], len(rxsPP1)*2+2, sum(n_obs_PP1only)))
AICs = np.asarray(AICs)
AIC['model 2, pp1 data'] = AICs[idx_incl]


if plotFigures:
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(exp_ids_PP1,idx_incl, idx_excl,2,'PP1',False)
    plot_paramDistrPP1('model 2',idx_incl)

    # plot distribution of model specific parameters
    plt.figure(666,figsize=(3,3))
    plt.figure(666).suptitle('model 2, PP1 data only, additional parameters')
    
    plt.subplot(1,2,1)
    for i in idx_incl:
        plt.plot(paramsHJ[i,62].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$r2_{actF}$'])
    plt.ylabel("parameter value")
    
    plt.subplot(1,2,2)
    for i in idx_incl:
        plt.plot(paramsHJ[i,63].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$r2_{Ka}$'])
    plt.ylabel("parameter value")
    
    plt.tight_layout()

    if saveFigs == True:
        plt.figure(666,figsize=(3,3))
        print("figure model2_distrAdditionalParams.svg saved")
        plt.savefig(os.path.join(path_figures,'model2_distrAdditionalParams.svg'), bbox_inches = "tight")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 

#%% cell 6: Model 3 - PP1 data only, Figure 2e and Supplementary Figure 10

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model3_PP1_only_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model3_PP1_only_HJ.npy'))

paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]
if loadData == False:   
    for p in range(nr_paramsets):
        print('simulations model 3 for PP1 data '+str(100*p/nr_paramsets)+'% complete.')
        for n in range(12):
            
            ICs = exp_ICs[n]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            additionalParams = paramsHJ[p,62:]
            params = [k,K,additionalParams,c_enzymes_exp[n]]
            output = fun.odeRK4(mod.cMyBPC_model3,ICs,params,t0,tend+1,h)
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P'),
                fun.fraction(output,'3P'),
                fun.fraction(output,'2P'),
                fun.fraction(output,'1P'),
                fun.fraction(output,'0P'),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,8,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat,'simDat_rel_fracs_m3_pp1.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat,'simDat_m3_pp1.npy'),simDat)
else:    
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m3_pp1.npy'))
    simDat = np.load(os.path.join(path_simdat,'simDat_m3_pp1.npy'))

# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 
cutoffs = [1,1.5,1.5,1.5,0]
# indices of parametersets that are to be included/ excluded
idx_incl, idx_excl = fun.filterParamSets(mse[:,[0,2,3,4,5]], cutoffs) 

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistrPP1('model 3, PP1 data only', exp_ids_PP1, mse, cutoffs)

# calculate the AIC values for included parametersets of model 2

mse_avg_PP1only = np.mean(mse[:,exp_ids_PP1],axis=1)

AICs = []
for i in range(len(mse_avg_PP1only)):
    AICs.append(fun.AIC(mse_avg_PP1only[i], len(rxsPP1)*2+3, sum(n_obs_PP1only)))
AICs = np.asarray(AICs)
AIC['model 3, pp1 data'] = AICs[idx_incl]

if plotFigures:
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(exp_ids_PP1,idx_incl, idx_excl,3,'PP1')
    
    # plot_paramDistrPP1('model 3',idx_incl)
    
    # # plot distribution of model specific parameters
    # plt.figure(666,figsize=(3,4))
    # plt.figure(666).suptitle('model 3, PP1 data only, additional parameters')
    
    # plt.subplot(1,3,1)
    # for i in idx_incl:
    #     plt.plot(paramsHJ[i,62].T, 'ok',alpha=0.15,ms=5)
    # # plt.yscale('log')
    # ax = plt.gca()
    # ax.set_xticks([0])
    # ax.set_xticklabels(['$\\alpha_{r2}$'])
    # plt.ylabel("parameter value")
    
    # plt.subplot(1,3,2)
    # for i in idx_incl:
    #     plt.plot(paramsHJ[i,63].T, 'ok',alpha=0.15,ms=5)
    # # plt.yscale('log')
    # ax = plt.gca()
    # ax.set_xticks([0])
    # ax.set_xticklabels(['$k_{cat,A}$'])
    # plt.ylabel("parameter value ($s^{-1}$)")
    
    # plt.subplot(1,3,3)
    # for i in idx_incl:
    #     plt.plot(paramsHJ[i,64].T, 'ok',alpha=0.15,ms=5)
    # # plt.yscale('log')
    # ax = plt.gca()
    # ax.set_xticks([0])
    # ax.set_xticklabels(['$K_{m,A}$'])
    # plt.ylabel("parameter value ($M$)")
    
    # plt.tight_layout()
    
    # if saveFigs == True:
    #     plt.figure(666,figsize=(3,4))
    #     print("figure model3_distrAdditionalParams.svg saved")
    #     plt.savefig(os.path.join(path_figures,'model3_distrAdditionalParams.svg'), bbox_inches = "tight")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#%% cell 7: Model 4 - PP1 data only, Figure 2e and Supplementary Figures 11

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model4_PP1_only_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model4_PP1_only_HJ.npy'))

paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

paramsHJ[np.where(paramsHJ<1e-12)] = 0

# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]
if loadData == False:   
    for p in range(nr_paramsets):
        print('simulations model 4 for PP1 data '+str(100*p/nr_paramsets)+'% complete.')
        for n in range(12):
            
            #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
            ICs = [exp_ICs[n,0],exp_ICs[n,1],0,exp_ICs[n,2],exp_ICs[n,3],exp_ICs[n,4],exp_ICs[n,5],exp_ICs[n,6],exp_ICs[n,7]]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            additionalParams = paramsHJ[p,62:]
            params = [k,K,additionalParams,c_enzymes_exp[n]]
            
            output = np.array([])
            try:
                output = fun.odeRK4(mod.cMyBPC_model4,ICs,params,t0,tend+1,h)
                if output[np.where(output<0)].shape[0] > 0:
                    print("Numerical issue occured: negative values\n retrying with reduced stepsize...")
                    h2 = 0.1
                    output = fun.odeRK4(mod.cMyBPC_model4,ICs,params,t0,tend+1,h2)
                    output = output[:,::10]
                    if output[np.where(output<0)].shape[0] == 0:
                        print("succeeded!")
                    else:
                        print("failed!")                    
            except RuntimeWarning:
                print("Numerical issue occured: runtime warning\n retrying with reduced stepsize...")
                h2 = 0.1
                output = fun.odeRK4(mod.cMyBPC_model4,ICs,params,t0,tend+1,h2)
                output = output[:,::10]
                
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P',4),
                fun.fraction(output,'3P',4),
                fun.fraction(output,'2P',4),
                fun.fraction(output,'1P',4),
                fun.fraction(output,'0P',4),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,9,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat,'simDat_rel_fracs_m4_pp1.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat,'simDat_m4_pp1.npy'),simDat)
else:    
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m4_pp1.npy'))
    simDat = np.load(os.path.join(path_simdat,'simDat_m4_pp1.npy'))

# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 
cutoffs = [1,1.5,1.5,1.5,-0.5]

# indices of parametersets that are to be included/ excluded
idx_incl, idx_excl = fun.filterParamSets(mse[:,[0,2,3,4,5]], cutoffs) 

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistrPP1('model 4, PP1 data only', exp_ids_PP1, mse, cutoffs)

# calculate the AIC values for included parametersets of model 4

mse_avg_PP1only = np.mean(mse[:,exp_ids_PP1],axis=1)

AICs = []
for i in range(len(mse_avg_PP1only)):
    AICs.append(fun.AIC(mse_avg_PP1only[i], len(rxsPP1)*2+4, sum(n_obs_PP1only)))
AICs = np.asarray(AICs)
AIC['model 4, pp1 data'] = AICs[idx_incl]

if plotFigures:
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(exp_ids_PP1,idx_incl, idx_excl,4,'PP1')
    plot_paramDistrPP1('model 4',idx_incl)
    
    # plot distribution of model specific parameters
    plt.figure(666,figsize=(4.5,4))
    plt.figure(666).suptitle('model 4, PP1 data only, additional parameters')
    
    plt.subplot(1,4,1)
    for i in idx_incl:
        plt.plot(paramsHJ[i,62].T, 'ok',alpha=0.15,ms=5)
    # plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['k$_{2, fast}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,4,2)
    for i in idx_incl:
        plt.plot(paramsHJ[i,63].T, 'ok',alpha=0.15,ms=5)
    # plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['K$_{2, fast}$'])
    plt.ylabel("parameter value ($M$)")
    
    plt.subplot(1,4,3)
    for i in idx_incl:
        plt.plot(paramsHJ[i,64].T, 'ok',alpha=0.15,ms=5)
    # plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$k_{iso,F}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,4,4)
    for i in idx_incl:
        plt.plot(paramsHJ[i,65].T, 'ok',alpha=0.15,ms=5)
    # plt.yscale('log')
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$k_{iso,R}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.tight_layout()
    
    if saveFigs == True:
        plt.figure(666,figsize=(3,4))
        print("figure model4_distrAdditionalParams_PP1.svg saved")
        plt.savefig(os.path.join(path_figures,'model4_distrAdditionalParams_PP1.svg'), bbox_inches = "tight")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#%% cell 8: Model 4 - all experiments, Supplementary Figures 14, 15 and 16

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model4_PP1_PP2A_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model4_PP1_PP2A_HJ.npy'))

paramsHJ = np.delete(paramsHJ,[44,48],0)
paramsHJ[np.where(paramsHJ<1e-12)] = 0
paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

# Use PKA parameters from model 1

paramsHJm1 = np.load(os.path.join(path_paramsets,'resultsPE_model1_HJ.npy'))
paramsHJm1 = fun.reconkK2225(paramsHJm1)

rxsPKA = np.array([1,4,7,22,25,28])+1
params_PKA = np.union1d(rxsPKA,rxsPKA+30)
x = paramsHJm1[idx_incl_m1_PKA,:]
x = x[:,params_PKA]
paramsHJ[:len(idx_incl_m1_PKA),params_PKA] = x
paramsHJ[len(idx_incl_m1_PKA):2*len(idx_incl_m1_PKA),params_PKA] = x
paramsHJ[2*len(idx_incl_m1_PKA):,params_PKA] = x[:(len(paramsHJ[:,0]) - 2*len(idx_incl_m1_PKA)),:]


# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]

if loadData == False:   
    for p in range(nr_paramsets):
        print(p)
        print("paramset ", str(int(paramsHJ[p,0])))
        for n in range(12):
            
            #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
            ICs = [exp_ICs[n,0],exp_ICs[n,1],0,exp_ICs[n,2],exp_ICs[n,3],exp_ICs[n,4],exp_ICs[n,5],exp_ICs[n,6],exp_ICs[n,7]]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            additionalParams = paramsHJ[p,62:]
            params = [k,K,additionalParams,c_enzymes_exp[n]]
            
            output = np.array([])
            try:
                output = fun.odeRK4(mod.cMyBPC_model4_full,ICs,params,t0,tend+1,h)
                if output[np.where(output<0)].shape[0] > 0:
                    print("Numerical issue occured: negative values\n retrying with reduced stepsize...")
                    h2 = 0.1
                    output = fun.odeRK4(mod.cMyBPC_model4_full,ICs,params,t0,tend+1,h2)
                    output = output[:,::10]
                    if output[np.where(output<0)].shape[0] == 0:
                        print("succeeded!")
                    else:
                        print("failed!")                    
            except RuntimeWarning:
                try:
                    print("Numerical issue occured: runtime warning\n retrying with reduced stepsize: 0.1")
                    h2 = 0.1
                    output = fun.odeRK4(mod.cMyBPC_model4_full,ICs,params,t0,tend+1,h2)
                    output = output[:,::10]
                except:
                      print("Numerical issue occured: runtime warning\n retrying with reduced stepsize: 0.01")
                      h2 = 0.01
                      output = fun.odeRK4(mod.cMyBPC_model4_full,ICs,params,t0,tend+1,h2)
                      output = output[:,::100]   
                
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P',4),
                fun.fraction(output,'3P',4),
                fun.fraction(output,'2P',4),
                fun.fraction(output,'1P',4),
                fun.fraction(output,'0P',4),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,9,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat,'simDat_rel_fracs_m4_pp1,pp2a.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat,'simDat_m4_pp1,pp2a.npy'),simDat)
else:    
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m4_pp1,pp2a.npy'))
    simDat = np.load(os.path.join(path_simdat,'simDat_m4_pp1,pp2a.npy'))
    
# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 

cutoffs = [0,0.5,0, 0.5,1,-0.5, 1.5,1.5,1.5, 1.5,5,5]    


#convert interpolated experimental data into numpy array
npar_expDatInterp = np.zeros([12,5,3601])
for i in range(12):
    npar_expDatInterp[i,:,:] = expDat_interpol[i] 

idx_incl_m4, idx_excl_m4  = fun.filterParamSets(mse, cutoffs, 
                                          npar_expDatInterp, simDat_rel_fracs, 
                                          [0,1,2,5,9], [0.2,0.2,0.15,0.15,0.18]) 

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistr('model 4, all experiments', range(12), mse, cutoffs)

# calculate the AIC values for included parametersets of model 4

mse_avg = np.mean(mse,axis=1)

AICs = []
for i in range(len(mse_avg)):
    AICs.append(fun.AIC(mse_avg[i], paramsHJ.shape[1], sum(n_obs)))
AICs = np.asarray(AICs)
AIC['model 4, all data'] = AICs[idx_incl_m4]

if plotFigures:
       
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(range(12),idx_incl_m4, idx_excl_m4, 4,'all',False)
    plot_paramDistr('model 4', idx_incl_m4)
    
    # plot distribution of model specific parameters
    plt.figure(666,figsize=(7.5,4))
    plt.figure(666).suptitle('model 4, all experiments, additional parameters')
    
    plt.subplot(1,6,1)
    for i in idx_incl_m4:
        plt.plot(paramsHJ[i,62].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['k$_{2, fast}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,6,2)
    for i in idx_incl_m4:
        plt.plot(paramsHJ[i,63].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['K$_{2, fast}$'])
    plt.ylabel("parameter value ($M$)")
    
    plt.subplot(1,6,3)
    for i in idx_incl_m4:
        plt.plot(paramsHJ[i,66].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['k$_{3, fast}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,6,4)
    for i in idx_incl_m4:
        plt.plot(paramsHJ[i,67].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['K$_{3, fast}$'])
    plt.ylabel("parameter value ($M$)")
    
    plt.subplot(1,6,5)
    for i in idx_incl_m4:
        plt.plot(paramsHJ[i,64].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$k_{iso,F}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,6,6)
    for i in idx_incl_m4:
        plt.plot(paramsHJ[i,65].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$k_{iso,R}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.tight_layout()
    
    if saveFigs == True:
        plt.figure(666,figsize=(3,4))
        print("figure model4_distrAdditionalParams.svg saved")
        plt.savefig(os.path.join(path_figures,'model4_distrAdditionalParams.svg'), bbox_inches = "tight")

    
#Calculate lifetime of Atr

lifetimes = []
for i in paramsHJ[idx_incl_m4,64]:
    lifetimes.append(1/i)
    
#%% cell 9: specificity ratios PKA/PPX  (Figure 3g, run cell 3 and cell 8 first)

spec = paramsHJ[idx_incl_m4,2:32].T/paramsHJ[idx_incl_m4,32:62].T


r1 = spec[6]/spec[7]      #v7 vs v8
r2 = spec[27]/spec[28]    #v28 vs v29
r3 = spec[6]/spec[8]      #v7 vs v9
r4 = spec[27]/spec[29]    #v28 vs v30

plt.figure(figsize=(2.5,3))
plt.plot([r1,r2,r3,r4],'o',color = 'b', alpha=0.25,ms=7)
plt.plot(np.median(np.asarray([r1,r2,r3,r4]),axis = 1),'_r',ms=20)

for i in range(spec.shape[1]):
    plt.plot([0,1],[r1[i],r2[i]],'-',color = 'b', alpha=0.15,lw=0.75)
    plt.plot([2,3],[r3[i],r4[i]],'-',color = 'b', alpha=0.15,lw=0.75)

ax = plt.gca()
ax.set_xticks(np.arange(4))
xlabs = ['$\\alpha\\beta \\ \\leftrightarrows \\ \\alpha\\beta\\gamma$',
         '$\\alpha\\beta\\delta \\  \\leftrightarrows  \\ \\alpha\\beta\\gamma\\delta$',
         '$\\alpha\\beta  \\ \\leftrightarrows \\  \\alpha\\beta\\gamma$',
         '$\\alpha\\beta\\delta  \\ \\leftrightarrows  \\ \\alpha\\beta\\gamma\\delta$']
         
         
ax.set_xticklabels(xlabs,rotation = 45,size=13)  

plt.ylabel("Specificity ratio",size=14.5)

plt.ylim(0,70)
plt.xlim(-0.5,3.5)

plt.savefig(os.path.join(path_figures,'specificitiesRatios.svg'), bbox_inches = "tight")

mw_pp1 = stats.mannwhitneyu(r1,r2, alternative='two-sided')
mw_pp2a = stats.mannwhitneyu(r3,r4, alternative='two-sided')

print("Result Mann-Whitney test specificity ratios pp1: \n", mw_pp1,'\n\n',
      "Result Mann-Whitney test specificity ratios pp2a: \n", mw_pp2a,'\n\n')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#%% cell 10: Calculate statistics for AIC:  model 1-4, PP1 data. Figure 2e and Supplementary Figure 8 (run cells 4-7 first)

print ('\n \n Calculate statistics for AIC:  model 1-4, PP1 data...\n')

#plot AIC distribution for models 1 and 2
plt.figure(figsize=(3.25,2.75))

minAIC = np.min([np.min(AIC['model 1, pp1 data']),np.min(AIC['model 2, pp1 data'])])
maxAIC = np.max([np.max(AIC['model 1, pp1 data']),np.max(AIC['model 2, pp1 data'])])
bins = np.linspace(minAIC,maxAIC,25)

plt.hist(AIC['model 1, pp1 data'],bins,color='b',alpha=0.33,label='model 1')
plt.hist(AIC['model 3, pp1 data'],bins,color='m',alpha=0.33,label='model 3')
plt.ylim((0,50))
plt.yticks([0,25,50])
plt.legend(['model 1', 'model 2'])
plt.ylabel('frequency',fontsize=13.5)
plt.xlabel('AIC score',fontsize=13.5)
plt.tight_layout()

if saveFigs == True:
    print("figure AIC_m1m2_pp1.svg saved")
    plt.savefig(os.path.join(path_figures,'AIC_m1m2m4_pp1.svg'), bbox_inches = "tight")


#plot AIC distribution for models 1,3 and 4
plt.figure(figsize=(3.25,3))

minAIC = np.min([np.min(AIC['model 1, pp1 data']),np.min(AIC['model 3, pp1 data']),np.min(AIC['model 4, pp1 data'])])
maxAIC = np.max([np.max(AIC['model 1, pp1 data']),np.max(AIC['model 3, pp1 data']),np.max(AIC['model 4, pp1 data'])])
bins = np.linspace(minAIC,maxAIC,25)

plt.hist(AIC['model 1, pp1 data'],bins,color='b',alpha=0.33,label='model 1')
plt.hist(AIC['model 3, pp1 data'],bins,color='g',alpha=0.33,label='model 3')
plt.hist(AIC['model 4, pp1 data'],bins,color='r',alpha=0.33,label='model 4')
plt.ylim((0,50))
plt.yticks([0,25,50])
plt.legend(['model 1', 'model 3', 'model 4'],fontsize=13)
plt.ylabel('frequency',fontsize=13.5)
plt.xlabel('AIC score',fontsize=13.5)
plt.tight_layout()

if saveFigs == True:
    print("figure AIC_m1m3m4_pp1.svg saved")
    plt.savefig(os.path.join(path_figures,'AIC_m1m3m4_pp1.svg'),dpi=500, bbox_inches = "tight")


print('Distribution measures of AIC values')
print('Model 1:\n', 'mean: ', np.mean(AIC['model 1, pp1 data']), ' SD: ', np.std(AIC['model 1, pp1 data']))
print('Model 2:\n', 'mean: ', np.mean(AIC['model 2, pp1 data']), ' SD: ', np.std(AIC['model 2, pp1 data']))
print('Model 3:\n', 'mean: ', np.mean(AIC['model 3, pp1 data']), ' SD: ', np.std(AIC['model 3, pp1 data']))
print('Model 4:\n', 'mean: ', np.mean(AIC['model 4, pp1 data']), ' SD: ', np.std(AIC['model 4, pp1 data']))

print('Shapiro-Wilk tests') #if pvalue < 0.05, values are likely not from normal distribution
print('Model 1:', stats.shapiro(AIC['model 1, pp1 data']))
print('Model 2:', stats.shapiro(AIC['model 2, pp1 data']))
print('Model 3:', stats.shapiro(AIC['model 3, pp1 data']))
print('Model 4:', stats.shapiro(AIC['model 4, pp1 data']))

logAIC = {}
for i in AIC:
    logAIC[i] = np.log2(-AIC[i]) 
    
kw_result = stats.kruskal(AIC['model 1, pp1 data'],AIC['model 3, pp1 data'],AIC['model 4, pp1 data'])    
anova_result = stats.f_oneway(logAIC['model 1, pp1 data'],logAIC['model 3, pp1 data'],logAIC['model 4, pp1 data'])
mw_Mod1vsMod2 = stats.mannwhitneyu(AIC['model 1, pp1 data'], AIC['model 2, pp1 data'], alternative='two-sided')
mw_Mod1vsMod3 = stats.mannwhitneyu(AIC['model 1, pp1 data'], AIC['model 3, pp1 data'], alternative='two-sided')
mw_Mod1vsMod4 = stats.mannwhitneyu(AIC['model 1, pp1 data'], AIC['model 4, pp1 data'], alternative='two-sided')
mw_Mod3vsMod4 = stats.mannwhitneyu(AIC['model 3, pp1 data'], AIC['model 4, pp1 data'], alternative='two-sided')

print("\n ~~~~~~~ Statistical analysis of AIC distributions ~~~~~~~ \n")
print("Result Kruskal-Wallis test model 1,3 and 4: ", kw_result,'\n\n',
      "Result 1-way ANOVA model 1,3 and 4: \n", anova_result,'\n\n',
      "Result Mann-Whitney test model 1 vs 2: \n", mw_Mod1vsMod2,'\n\n',
      "Result Mann-Whitney test model 1 vs 3: \n", mw_Mod1vsMod3,'\n\n',
      "Result Mann-Whitney test model 1 vs 4: \n", mw_Mod1vsMod4 ,'\n\n',
      "Result Mann-Whitney test model 3 vs 4: \n", mw_Mod3vsMod4)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#%% cell 11: Calculate statistics for AIC:  model 1 and 4, all data. Supplementary Figure 16b (run cells 3 and 8 first)
print ('\n \n Calculate statistics for AIC:  model 1 and 4, all data....\n')

#plot AIC distribution for models 1 and 4
plt.figure(figsize=(3.25,2.75))
minAIC = np.min([np.min(AIC['model 1, all data']),np.min(AIC['model 4, all data'])])
maxAIC = np.max([np.max(AIC['model 1, all data']),np.max(AIC['model 4, all data'])])
bins = np.linspace(minAIC,maxAIC,25)

plt.hist(AIC['model 1, all data'],bins,color='b',alpha=0.33,label='model 1')
plt.hist(AIC['model 4, all data'],bins,color='m',alpha=0.33,label='model 4')
plt.ylim((0,50))
plt.yticks([0,25,50])
plt.legend(['model 1', 'model 4'])
plt.ylabel('frequency',fontsize=13.5)
plt.xlabel('AIC score',fontsize=13.5)
plt.tight_layout()

if saveFigs == True:
    print("figure AIC_m1m4.svg saved")
    plt.savefig(os.path.join(path_figures,'AIC_m1m4.svg'), bbox_inches = "tight")

print('Distribution measures of AIC values')
print('Model 1:\n', 'mean: ', np.mean(AIC['model 1, all data']), ' SD: ', np.std(AIC['model 1, all data']), ' variance: ', np.var(AIC['model 1, all data']))
print('Model 4:\n', 'mean: ', np.mean(AIC['model 4, all data']), ' SD: ', np.std(AIC['model 4, all data']), ' variance: ', np.var(AIC['model 4, all data']))

print('Shapiro-Wilk tests') #if pvalue < 0.05, values are likely not from normal distribution
print('Model 1:', stats.shapiro(AIC['model 1, all data']))
print('Model 4:', stats.shapiro(AIC['model 4, all data']))
  
tt_Mod1vsMod4 = stats.ttest_ind(AIC['model 1, all data'], AIC['model 4, all data'], equal_var=False)

print("\n ~~~~~~~ Statistical analysis of AIC distributions ~~~~~~~ \n")
print("Result Welch's t-test model 1 vs 4: \n", tt_Mod1vsMod4)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#%% cell 12: Model 1 tQSSA - all experiments (only for validity checks, data not shown in manuscript)

loadData = True

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model1_tQSSA_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model1_tQSSA_HJ.npy'))

paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]

if loadData == False:   
    for p in range(nr_paramsets):
        print(p)
        for n in range(12):
        
            ICs = exp_ICs[n]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            
            params = [k,K,c_enzymes_exp[n]]
            output = fun.odeRK4(mod.cMyBPC_model1_tQSSA,ICs,params,t0,tend+1,h)
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P'),
                fun.fraction(output,'3P'),
                fun.fraction(output,'2P'),
                fun.fraction(output,'1P'),
                fun.fraction(output,'0P'),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,8,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat,'simDat_rel_fracs_m1_tQSSA.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat,'simDat_m1_tQSSA.npy'),simDat)
else:
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m1_tQSSA.npy'))
    simDat = np.load(os.path.join(path_simdat,'simDat_m1_tQSSA.npy'))

# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse_m1_tQSSA = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 
cutoffs = [1,1.5,1.5,1.5,1.5,0.25,
            1.5,1.5,1.5,1.5,1.5,1.5]

# indices of parametersets that are to be included/ excluded
idx_incl_m1_tQSSA, idx_excl_m1_tQSSA = fun.filterParamSets(mse_m1_tQSSA, cutoffs) 

# filtering included PKA parametersets only - for model 4
cutoffs_PKA = [1.5,1.5]
idx_incl_m1_PKA_tQSSA, idx_excl_m1_PKA_tQSSA = fun.filterParamSets(mse_m1_tQSSA[:,[10,11]], cutoffs_PKA) 

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistr('model 1 tQSSA, all experiments', range(12), mse_m1_tQSSA, cutoffs)

# calculate the AIC values for included parametersets of model 1

mse_avg = np.mean(mse_m1_tQSSA,axis=1)

AICs = []
for i in range(len(mse_avg)):
    AICs.append(fun.AIC(mse_avg[i], paramsHJ.shape[1], sum(n_obs)))
AICs = np.asarray(AICs)
AIC['model 1 tQSSA, all data'] = AICs[idx_incl_m1_tQSSA]

if plotFigures:
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(range(12),idx_incl_m1_tQSSA, idx_excl_m1_tQSSA, 1,tQSSA = True)
    plot_paramDistr('model 1 tQSSA', idx_incl_m1_tQSSA)
    

# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#%% cell 13: Model 4 tQSSA - all experiments 

# loadData = False # load result from previous simulations if available 

paramsGA = np.load(os.path.join(path_paramsets,'resultsPE_model4_tQSSA_PP1_PP2A_GA.npy'))
paramsHJ = np.load(os.path.join(path_paramsets,'resultsPE_model4_tQSSA_PP1_PP2A_HJ.npy'))

# Use PKA parameters from model 1
paramsHJm1 = np.load(os.path.join(path_paramsets,'resultsPE_model1_tQSSA_HJ.npy'))
paramsHJm1 = fun.reconkK2225(paramsHJm1)
paramsHJ[np.where(paramsHJ<1e-12)] = 0
paramsGA = fun.reconkK2225(paramsGA)
paramsHJ = fun.reconkK2225(paramsHJ)

# Use PKA parameters from model 1
rxsPKA = np.array([1,4,7,22,25,28])+1
params_PKA = np.union1d(rxsPKA,rxsPKA+30)
x = paramsHJm1[idx_incl_m1_PKA_tQSSA,:]
x = x[:,params_PKA]
paramsHJ[:len(idx_incl_m1_PKA_tQSSA),params_PKA] = x
paramsHJ[len(idx_incl_m1_PKA_tQSSA):,params_PKA] = x[paramsHJ[len(idx_incl_m1_PKA_tQSSA):,params_PKA].shape[0],:]


# Time setting for simulations
t0 = 0
tend = 3600
h = 1
npts = int(tend/h)
time = np.linspace(t0,tend,npts+1)        

simDat = []      
simDat_rel_fracs = []
nr_paramsets = paramsHJ.shape[0]

if loadData == False:   
    for p in range(nr_paramsets):
        print(p)
        print("paramset ", str(int(paramsHJ[p,0])))
        for n in range(12):
            
            #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
            ICs = [exp_ICs[n,0],exp_ICs[n,1],0,exp_ICs[n,2],exp_ICs[n,3],exp_ICs[n,4],exp_ICs[n,5],exp_ICs[n,6],exp_ICs[n,7]]
            
            # parameters
            k = paramsHJ[p,2:32]
            K = paramsHJ[p,32:62]
            additionalParams = paramsHJ[p,62:]
            params = [k,K,additionalParams,c_enzymes_exp[n]]
            
            output = np.array([])
            try:
                output = fun.odeRK4(mod.cMyBPC_model4_full,ICs,params,t0,tend+1,h)
                if output[np.where(output<0)].shape[0] > 0:
                    print("Numerical issue occured: negative values\n retrying with reduced stepsize...")
                    h2 = 0.1
                    output = fun.odeRK4(mod.cMyBPC_model4_full_tQSSA,ICs,params,t0,tend+1,h2)
                    output = output[:,::10]
                    if output[np.where(output<0)].shape[0] == 0:
                        print("succeeded!")
                    else:
                        print("failed!")                    
            except RuntimeWarning:
                try:
                    print("Numerical issue occured: runtime warning\n retrying with reduced stepsize: 0.1")
                    h2 = 0.1
                    output = fun.odeRK4(mod.cMyBPC_model4_full_tQSSA,ICs,params,t0,tend+1,h2)
                    output = output[:,::10]
                except: 
                      print("Numerical issue occured: runtime warning\n retrying with reduced stepsize: 0.01")
                      h2 = 0.01
                      output = fun.odeRK4(mod.cMyBPC_model4_full_tQSSA,ICs,params,t0,tend+1,h2)
                      output = output[:,::100]   
                
            simDat.append(output)
            simDat_rel_fracs.append([
                fun.fraction(output,'4P',4),
                fun.fraction(output,'3P',4),
                fun.fraction(output,'2P',4),
                fun.fraction(output,'1P',4),
                fun.fraction(output,'0P',4),
                ])
            
    simDat = np.reshape(simDat, (nr_paramsets,12,9,npts+1))        
    simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,12,5,npts+1))
    
    if saveData:
        np.save(os.path.join(path_simdat,'simDat_rel_fracs_m4_tQSSA_pp1,pp2a.npy'),simDat_rel_fracs)
        np.save(os.path.join(path_simdat,'simDat_m4_tQSSA_pp1,pp2a.npy'),simDat)
else:    
    simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_rel_fracs_m4_tQSSA_pp1,pp2a.npy'))
    simDat = np.load(os.path.join(path_simdat,'simDat_m4_tQSSA_pp1,pp2a.npy'))

    
# Mean squared errors between interpolated data
# and simulations for each experiment and each parameter set

mse = fun.meanSqrtErr(expDat_interpol, simDat_rel_fracs, range(12))

# Exclude parametersets for which MSE for any of the PP1 experiments 
# exceeds the mean by more than X std devs (cutoff). 

cutoffs = [0,0.75,0.75, 0.5,1,0, 1.5,1.5,1.5, 1.5,5,5]    


#convert interpolated experimental data into numpy array
npar_expDatInterp = np.zeros([12,5,3601])
for i in range(12):
    npar_expDatInterp[i,:,:] = expDat_interpol[i] 

idx_incl_m4_tQSSA, idx_excl_m4_tQSSA  = fun.filterParamSets(mse, cutoffs, 
                                          npar_expDatInterp, simDat_rel_fracs, 
                                          [0,1,2,5,9], [0.2,0.2,0.15,0.15,0.18]) 

#save final parameter set
paramset_final_tQSSA = paramsHJ[idx_incl_m4_tQSSA,:]
np.save(os.path.join(path_paramsets,'paramset_final_tQSSA.npy'),paramset_final_tQSSA)

# Plot MSE distributions and cutoff values for parametersets

plot_MSEdistr('model 4 tQSSA, all experiments', range(12), mse, cutoffs)

# calculate the AIC values for included parametersets of model 4

mse_avg = np.mean(mse,axis=1)

AICs = []
for i in range(len(mse_avg)):
    AICs.append(fun.AIC(mse_avg[i], paramsHJ.shape[1], sum(n_obs)))
AICs = np.asarray(AICs)
AIC['model 4 tQSSA, all data'] = AICs[idx_incl_m4_tQSSA]

if plotFigures:
       
    #plot simulations, experimental data and distribution of fitted parameters
    plot_simNexp(range(12),idx_incl_m4_tQSSA, idx_excl_m4_tQSSA, 4,'all',False, tQSSA = True)
    plot_paramDistr('model 4 tQSSA', idx_incl_m4_tQSSA)
    
    # plot distribution of model specific parameters
    plt.figure(666,figsize=(7.5,4))
    plt.figure(666).suptitle('model 4 tQSSA, all experiments, additional parameters')
    
    plt.subplot(1,6,1)
    for i in idx_incl_m4_tQSSA:
        plt.plot(paramsHJ[i,62].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['k$_{2, fast}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,6,2)
    for i in idx_incl_m4_tQSSA:
        plt.plot(paramsHJ[i,63].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['K$_{2, fast}$'])
    plt.ylabel("parameter value ($M$)")
    
    plt.subplot(1,6,3)
    for i in idx_incl_m4_tQSSA:
        plt.plot(paramsHJ[i,66].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['k$_{3, fast}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,6,4)
    for i in idx_incl_m4_tQSSA:
        plt.plot(paramsHJ[i,67].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['K$_{3, fast}$'])
    plt.ylabel("parameter value ($M$)")
    
    plt.subplot(1,6,5)
    for i in idx_incl_m4_tQSSA:
        plt.plot(paramsHJ[i,64].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$k_{iso,F}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.subplot(1,6,6)
    for i in idx_incl_m4_tQSSA:
        plt.plot(paramsHJ[i,65].T, 'ok',alpha=0.15,ms=5)
    ax = plt.gca()
    ax.set_xticks([0])
    ax.set_xticklabels(['$k_{iso,R}$'])
    plt.ylabel("parameter value ($s^{-1}$)")
    
    plt.tight_layout()
    
    if saveFigs == True:
        plt.figure(666,figsize=(3,4))
        print("figure model4_tQSSA_distrAdditionalParams.svg saved")
        plt.savefig(os.path.join(path_figures,'model4_tQSSA_distrAdditionalParams.svg'), bbox_inches = "tight")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#%% cell 11: Calculate statistics for AIC:  model 1 and 4, all data.
print ('\n \n Calculate statistics for AIC:  model 1 and 4, Michaelis Menten vs tQSSA, all data....\n')

#plot AIC distribution for models 1 and 4
plt.figure(figsize=(4,3))
minAIC = np.min([np.min(AIC['model 1, all data']), np.min(AIC['model 1 tQSSA, all data']), np.min(AIC['model 4 tQSSA, all data']), np.min(AIC['model 4, all data'])])
maxAIC = np.max([np.max(AIC['model 1, all data']), np.max(AIC['model 1 tQSSA, all data']), np.max(AIC['model 4 tQSSA, all data']), np.max(AIC['model 4, all data'])])
bins = np.linspace(minAIC,maxAIC,25)

plt.hist(AIC['model 1, all data'],bins,color='b',alpha=0.33,label='model 1')
plt.hist(AIC['model 1 tQSSA, all data'],bins,color='purple',alpha=0.33,label='model 1, tQSSA')
plt.hist(AIC['model 4, all data'],bins,color='m',alpha=0.33,label='model 4')
plt.hist(AIC['model 4 tQSSA, all data'],bins,color='r',alpha=0.33,label='model 4,tQSSA')
plt.ylim((0,50))
plt.yticks([0,25,50])
plt.legend(['model 1', 'model 1, tQSSA', 'model 4', 'model 4, tQSSA'])
plt.ylabel('frequency',fontsize=13.5)
plt.xlabel('AIC score',fontsize=13.5)
plt.tight_layout()

if saveFigs == True:
    print("figure AIC_m1m4.svg saved")
    plt.savefig(os.path.join(path_figures,'AIC_m1m4.svg'), bbox_inches = "tight")

print('Distribution measures of AIC values')
print('Model 1:\n', 'mean: ', np.mean(AIC['model 1, all data']), ' SD: ', np.std(AIC['model 1, all data']), ' variance: ', np.var(AIC['model 1, all data']))
print('Model 4:\n', 'mean: ', np.mean(AIC['model 4, all data']), ' SD: ', np.std(AIC['model 4, all data']), ' variance: ', np.var(AIC['model 4, all data']))

print('Shapiro-Wilk tests') #if pvalue < 0.05, values are likely not from normal distribution
print('Model 1:', stats.shapiro(AIC['model 1, all data']))
print('Model 4:', stats.shapiro(AIC['model 4, all data']))
  
tt_Mod1vsMod4 = stats.ttest_ind(AIC['model 1, all data'], AIC['model 4, all data'], equal_var=False)

print("\n ~~~~~~~ Statistical analysis of AIC distributions ~~~~~~~ \n")
print("Result Welch's t-test model 1 vs 4: \n", tt_Mod1vsMod4)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



