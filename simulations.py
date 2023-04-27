# -*- coding: utf-8 -*-
"""
This code reproduces the simulation results of the paper:

Thomas Kampourakis, Saraswathi Ponnam, Daniel Koch (2023):
The cardiac myosin binding protein-C phosphorylation state 
as a function of multiple protein kinase and phosphatase activities 
Preprint available under: https://doi.org/10.1101/2023.02.24.529959 

----------------NOTE----------------

Executing the whole script at once can take a long time.
Alternatively, you may want to execute only individual simulations of interested:
    -> adjust settings in cell 1 as you see fit
    -> run cells 0 to 2
    -> run the cell corresponding to the simulation you are interested in
    
----------------Overview----------------
    
cell 0: Import packages and modules, define paths
cell 1: Miscellaneous settings
cell 2: Function definitions

 ==~~==~~==~~== SIMULATIONS ==~~==~~==~~==~~==~~==~~==~    
cell 3: Timecourses single pulses PKA vs PP1/PP2A (Figure S21)
cell 4: Steady state PKA vs PP1/PP2A (Figure 3A,E S19)
cell 5: Steady state RSK2 vs PP1/PP2A (Figure S18)
cell 6: Steady state PKA vs PP1/PP2A in presence of RSK2 (Figure 3C,E S19)
cell 7: Steady state PKC vs PP1/PP2A (Figure S18)
cell 8: Steady state PKA vs PP1/PP2A in presence of PKC (Figure 3C,D,E)

(For reproducing Figure 3E, cells 4, 6 and 8 need to be run subsequently)


==~~==~~==~~== DATA ANALYSIS ==~~==~~==~~==~~==~~==~~==~
(only execute after running and saving data from cells 4-8)
cell 10: Plot dose response comparisons of fitted Hill parameters (Figure 3F and 3H)
cell 11: Statistical analysis (Table S1)


Code by Daniel Koch, 2021-2023
"""

#%% cell 0: Import packages and modules, define paths
import os
import sys

#paths
fileDirectory = os.path.dirname(os.path.abspath(__file__))
path_paramsets = os.path.join(fileDirectory, 'parametersets')   
path_simdat = os.path.join(fileDirectory, 'simulation data')   
path_figures = os.path.join(fileDirectory, 'figures\\simulations')   
sys.path.append(fileDirectory)

import models_cMyBPC as mod 
import FillBetween3d as fb3d
import functions_cMyBPC as fun
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
from statsmodels.stats.multitest import fdrcorrection
import warnings
from matplotlib import cm


#%% cell 1: Miscellaneous settings

warnings.filterwarnings("error")
plt.rcParams.update({'font.family':'Arial'})

saveFigs = False # saves figures as files
loadData = False #  loads result from previous simulations if available 
saveData = False #  save result from simulations (only if loadData = True)
plotFigures = True # plot results from simulations
printSimProg = True # print simulation progress to console

#create directories if necessary
if saveData == True and os.path.exists(path_simdat) == False:
    os.makedirs(path_simdat)
    
if saveFigs == True and os.path.exists(path_figures) == False:
    os.makedirs(path_figures)


xPstr = ['4P','3P','2P','1P','0P'] # labels for different phosphospecies of cMyBP-C

# Load fitted parametersets for PKA, PP1, PP2A
paramsHJ = np.load(os.path.join(path_paramsets,'paramset_final.npy'))
nr_paramsets = paramsHJ.shape[0]

# Add experimentally measured PKC parameters to fitted parameterset
pkc_Kms = np.linspace(3.167e-6,	7.537e-6,4)
pkc_kcat = (5.053+5.262)/2
paramsHJ[:,42] = pkc_Kms[0]
paramsHJ[:,45] = pkc_Kms[1]
paramsHJ[:,48] = pkc_Kms[2]
paramsHJ[:,51] = pkc_Kms[3]
paramsHJ[:,[12,15,18,21]] = pkc_kcat

# Add experimentally measured RSK2 parameters to fitted parameterset
paramsRSK2 = np.array([1.8,1.8,1.3e-6,1.3e-6]) # kcat reaction 31 and 32, Km reaction 31 and 32


#%% cell 2: Function definitions 

# define colors for plotting
cmap = cm.get_cmap('gnuplot2',7)
colV = []
for i in [0,0.3,0.5,0.6,0.8]: colV.append(cmap(i)[:3])
c4P,c3P,c2P,c1P,c0P = colV
xPstr = ['4P','3P','2P','1P','0P']



def plot_timecourse(time):

        avg_0P = np.average(simDat_rel_fracs[:,4,:], axis = 0)
        avg_1P = np.average(simDat_rel_fracs[:,3,:], axis = 0)
        avg_2P = np.average(simDat_rel_fracs[:,2,:], axis = 0)
        avg_3P = np.average(simDat_rel_fracs[:,1,:], axis = 0)
        avg_4P = np.average(simDat_rel_fracs[:,0,:], axis = 0)
        
        sd_0P = np.std(simDat_rel_fracs[:,4,:], axis = 0)
        sd_1P = np.std(simDat_rel_fracs[:,3,:], axis = 0)
        sd_2P = np.std(simDat_rel_fracs[:,2,:], axis = 0)
        sd_3P = np.std(simDat_rel_fracs[:,1,:], axis = 0)
        sd_4P = np.std(simDat_rel_fracs[:,0,:], axis = 0)

        #plot averages
                            
        plt.plot(time,avg_0P,color=c0P, alpha=0.5, lw=2.75)        
        plt.plot(time,avg_1P,color=c1P, alpha=0.5, lw=2.75)   
        plt.plot(time,avg_2P,color=c2P, alpha=0.5, lw=2.75) 
        plt.plot(time,avg_3P,color=c3P, alpha=0.5, lw=2.75) 
        plt.plot(time,avg_4P,color=c4P, alpha=0.5, lw=2.75) 
        
        #plot SD
        plt.fill_between(time, avg_0P-sd_0P, avg_0P+sd_0P, color=c0P,alpha=0.15)
        plt.fill_between(time, avg_1P-sd_1P, avg_1P+sd_1P, color=c1P,alpha=0.15)
        plt.fill_between(time, avg_2P-sd_2P, avg_2P+sd_2P, color=c2P,alpha=0.15)
        plt.fill_between(time, avg_3P-sd_3P, avg_3P+sd_3P, color=c3P,alpha=0.15)
        plt.fill_between(time, avg_4P-sd_4P, avg_4P+sd_4P, color=c4P,alpha=0.15)

def plot_SS_3D(kinase_name, kinase_vector, PPase_name,PPase_vector,xtick_array = np.array([1e-11,1e-10,1e-9,1e-8,1e-7,1e-6,1e-5])):
    
    fig = plt.figure(figsize=(7.5,7.5))
    ax = plt.axes(projection='3d')

    for p in range(len(PPase_vector)):
        
        PPase = np.ones(len(kinase_vector))*PPase_vector[p]
        
        avg_0P = np.average(simDat_rel_fracs_SS[:,p,:,4], axis = 0)
        avg_1P = np.average(simDat_rel_fracs_SS[:,p,:,3], axis = 0)
        avg_2P = np.average(simDat_rel_fracs_SS[:,p,:,2], axis = 0)
        avg_3P = np.average(simDat_rel_fracs_SS[:,p,:,1], axis = 0)
        avg_4P = np.average(simDat_rel_fracs_SS[:,p,:,0], axis = 0)
        
        sd_0P = np.std(simDat_rel_fracs_SS[:,p,:,4], axis = 0)
        sd_1P = np.std(simDat_rel_fracs_SS[:,p,:,3], axis = 0)
        sd_2P = np.std(simDat_rel_fracs_SS[:,p,:,2], axis = 0)
        sd_3P = np.std(simDat_rel_fracs_SS[:,p,:,1], axis = 0)
        sd_4P = np.std(simDat_rel_fracs_SS[:,p,:,0], axis = 0)
        
        #plot averages
                            
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_0P,color=c0P, alpha=0.5, lw=2.75)
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_1P,color=c1P, alpha=0.5, lw=2.75)   
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_2P,color=c2P, alpha=0.5, lw=2.75) 
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_3P,color=c3P, alpha=0.5, lw=2.75) 
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_4P,color=c4P, alpha=0.5, lw=2.75)
        
        #plot errors
        
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_0P-sd_0P, np.log(kinase_vector),np.log(PPase),avg_0P+sd_0P,  c=c0P, mode = 1,alpha=0.15)
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_1P-sd_1P, np.log(kinase_vector),np.log(PPase),avg_1P+sd_1P,  c=c1P, mode = 1,alpha=0.15)
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_2P-sd_2P, np.log(kinase_vector),np.log(PPase),avg_2P+sd_2P,  c=c2P, mode = 1,alpha=0.15)
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_3P-sd_3P, np.log(kinase_vector),np.log(PPase),avg_3P+sd_3P,  c=c3P, mode = 1,alpha=0.15)
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_4P-sd_4P, np.log(kinase_vector),np.log(PPase),avg_4P+sd_4P,  c=c4P, mode = 1,alpha=0.15)
        
        # logtransform tick labels
        plot_xticks = np.log(xtick_array)      
        ax.set_xticks(plot_xticks)
        ax.set_xticklabels((str(x) for x in xtick_array),fontsize=14)
        plt.xlabel('\n['+kinase_name+'] (mol/L)',fontsize=16)
        
        plot_yticks = np.log(PPase_vector)      
        ax.set_yticks(plot_yticks)
        ax.set_yticklabels((str(x) for x in PPase_vector),fontsize=14)
        plt.ylabel('\n['+PPase_name+'] (mol/L)',fontsize=16)
        
        ax.set_zlim([0,1])
        ax.set_zlabel('\n fraction',fontsize=16)
        ax.zaxis.set_tick_params(labelsize=14)
        # ax.set_zticklabels([0,0.2,0.4,0.6,0.8,1],fontsize=14)
     
        ax.grid(False)
        
def plot_SS_3D_noD(kinase_name, kinase_vector, PPase_name,PPase_vector,xtick_array = np.array([1e-11,1e-10,1e-9,1e-8,1e-7,1e-6,1e-5])):
    
    fig = plt.figure(figsize=(7.5,7.5))
    ax = plt.axes(projection='3d')

    for p in range(len(PPase_vector)):
        
        PPase = np.ones(len(kinase_vector))*PPase_vector[p]
        
        # 0 P0, 1 A, 2 At, 3 AB, 4 ABG, 5 D, 6 AD, 7 ABD, 8 ABGD
                
        avg_0P = np.average(simDat_SS[:,p,:,0]/np.sum(simDat_SS[:,p,:,:],2), axis = 0)
        avg_A = np.average((simDat_SS[:,p,:,1]+simDat_SS[:,p,:,2]+simDat_SS[:,p,:,6])/np.sum(simDat_SS[:,p,:,:],2), axis = 0)
        avg_AB = np.average((simDat_SS[:,p,:,3]+simDat_SS[:,p,:,7])/np.sum(simDat_SS[:,p,:,:],2), axis = 0)
        avg_ABG = np.average((simDat_SS[:,p,:,4]+simDat_SS[:,p,:,8])/np.sum(simDat_SS[:,p,:,:],2), axis = 0)

        
        sd_0P = np.std(simDat_SS[:,p,:,0]/np.sum(simDat_SS[:,p,:,:],2), axis = 0)
        sd_A = np.std((simDat_SS[:,p,:,1]+simDat_SS[:,p,:,2]+simDat_SS[:,p,:,6])/np.sum(simDat_SS[:,p,:,:],2), axis = 0)
        sd_AB = np.std((simDat_SS[:,p,:,3]+simDat_SS[:,p,:,7])/np.sum(simDat_SS[:,p,:,:],2), axis = 0)
        sd_ABG = np.std((simDat_SS[:,p,:,4]+simDat_SS[:,p,:,8])/np.sum(simDat_SS[:,p,:,:],2), axis = 0)
        
        #plot averages
                            
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_0P,color=c0P, alpha=0.5, lw=2.5)
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_A,color=c1P, alpha=0.5, lw=2.5)   
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_AB,color=c2P, alpha=0.5, lw=2.5) 
        plt.plot(np.log(kinase_vector),np.log(PPase),avg_ABG,color=c3P, alpha=0.5, lw=2.5) 
        
        #plot errors
        
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_0P-sd_0P, np.log(kinase_vector),np.log(PPase),avg_0P+sd_0P,  c=c0P, mode = 1,alpha=0.15)
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_A-sd_A, np.log(kinase_vector),np.log(PPase),avg_A+sd_A,  c=c1P, mode = 1,alpha=0.15)
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_AB-sd_AB, np.log(kinase_vector),np.log(PPase),avg_AB+sd_AB,  c=c2P, mode = 1,alpha=0.15)
        fb3d.fill_between_3d(ax,np.log(kinase_vector),np.log(PPase),avg_ABG-sd_ABG, np.log(kinase_vector),np.log(PPase),avg_ABG+sd_ABG,  c=c3P, mode = 1,alpha=0.15)
       
        # logtransform tick labels
        plot_xticks = np.log(xtick_array)      
        ax.set_xticks(plot_xticks)
        ax.set_xticklabels((str(x) for x in xtick_array),fontsize=14)
        plt.xlabel('\n['+kinase_name+'] (mol/L)',fontsize=16)
        
        plot_yticks = np.log(PPase_vector)      
        ax.set_yticks(plot_yticks)
        ax.set_yticklabels((str(x) for x in PPase_vector),fontsize=14)
        plt.ylabel('\n['+PPase_name+'] (mol/L)',fontsize=16)
        
        ax.set_zlim([0,1])
        ax.set_zlabel('\n fraction',fontsize=16)
        # ax.set_zticklabels([0,0.2,0.4,0.6,0.8,1],fontsize=14)
        ax.zaxis.set_tick_params(labelsize=14)
     
        ax.grid(False)
              
def run_simulation(ICs,params,t0,t_end,h,naFun,naFunParams,model = mod.cMyBPC_model_final,noisyS = False):
    output = np.array([])
    try:
        output = fun.odeRK4(model,ICs,params,t0,t_end+1,h,naFun,naFunParams)
        if output[np.where(output<0)].shape[0] > 0:
            print("Numerical issue occured: negative values\n retrying with reduced stepsize: 0.1")
            h2 = 0.1
            if noisyS == False:                
                output = fun.odeRK4(model,ICs,params,t0,t_end+1,h2,naFun,naFunParams)
                output = output[:,::10]
                if output[np.where(output<0)].shape[0] == 0:
                    print("succeeded!")
                else:
                    print("Numerical issue occured: negative values\n retrying with reduced stepsize: 0.01")
                    h2 = 0.01
                    output = fun.odeRK4(model,ICs,params,t0,t_end+1,h2,naFun,naFunParams)
                    output = output[:,::100]                   
    except RuntimeWarning:
        try:
            print("Numerical issue occured: runtime warning\n retrying with reduced stepsize: 0.1")
            h2 = 0.1
            output = fun.odeRK4(model,ICs,params,t0,t_end+1,h2,naFun,naFunParams)
            output = output[:,::10]
        except:
              print("Numerical issue occured: runtime warning\n retrying with reduced stepsize: 0.01")
              h2 = 0.01
              output = fun.odeRK4(model,ICs,params,t0,t_end+1,h2,naFun,naFunParams)
              output = output[:,::100] 
    return output

#############################################################
#%% ==~~==~~==~~== SIMULATIONS ==~~==~~==~~==~~==~~==~~==~

#%% #########################################################
# Timecourse simulations
#%% #########################################################

# %% cell 3: Timecourses single pulses PKA vs PP1/PP2A (Figure S21)

# Time setting for simulations
t0 = 0
t_end = 3*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C
c_enzymes = np.array([[1e-8,0,1e-7,0], #PKA, PKC, PP1, PP2A
                      [1e-7,0,1e-7,0],
                      [1e-8,0,1e-6,0],
                      [1e-7,0,1e-6,0],
                      [1e-8,0,0,1e-7],
                      [1e-7,0,0,1e-7],
                      [1e-8,0,0,1e-6],
                      [1e-7,0,0,1e-6]                     
                      ])         

onePulse = [300,300+60*60] #start and stop of PKA pulse

for l in range(2):
    for i in range(4):
        ii = l*4 + i
        
        simDat = []      
        simDat_rel_fracs = []
        if loadData == False:   
            for p in range(nr_paramsets):
                if printSimProg == True:
                    print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
                    
                # parameters
                k = paramsHJ[p,2:32]
                K = paramsHJ[p,32:62]
                additionalParams = paramsHJ[p,62:]
                params = [k,K,additionalParams,c_enzymes[ii,:]]
                
                output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,onePulse)
                    
                simDat.append(output)
                simDat_rel_fracs.append([
                    fun.fraction(output,'4P',4),
                    fun.fraction(output,'3P',4),
                    fun.fraction(output,'2P',4),
                    fun.fraction(output,'1P',4),
                    fun.fraction(output,'0P',4),
                    ])
                    
            simDat = np.reshape(simDat, (nr_paramsets,9,npts+1))        
            simDat_rel_fracs = np.reshape(simDat_rel_fracs, (nr_paramsets,5,npts+1))
            
            if saveData == True:
                np.save(os.path.join(path_simdat,'simDat_tc_pka_pkc_pp1_pp2a_'+str(c_enzymes[ii])+'.npy'),simDat_rel_fracs)
                np.save(os.path.join(path_simdat,'simDat_rf_tc_pka_pkc_pp1_pp2a_'+str(c_enzymes[ii])+'.npy'),simDat)
        else:    
            simDat_rel_fracs = np.load(os.path.join(path_simdat,'simDat_tc_pka_pkc_pp1_pp2a_'+str(c_enzymes[ii])+'.npy'))
            simDat = np.load(os.path.join(path_simdat,'simDat_rf_tc_pka_pkc_pp1_pp2a_'+str(c_enzymes[ii])+'.npy'))
        
        # plot
        
        plt.figure(figsize=(4,2.5))
        plot_timecourse(time/60)  
        profile_signal = fun.sig2array(onePulse,t_end+1,h)
        
        plt.yticks([0,0.5,1],fontsize=14); plt.ylabel("value",fontsize=16) 
        plt.xticks([])
        
        if saveFigs == True:
            plt.savefig(os.path.join(path_figures,'tc_PKA_PKC_PP1_PP2A_'+str(c_enzymes[ii])+'.png'),dpi=300, bbox_inches = "tight")
        plt.show()    
            
        plt.figure(figsize=(4,1.25))
        plt.plot(time/60,profile_signal*c_enzymes[ii,0],"-b",label = "signal")
        plt.fill_between(time/60,profile_signal*c_enzymes[ii,0], color='b',alpha=0.1)
        
        plt.yticks(fontsize=14); plt.xticks([0,60,120,180],fontsize=14)
        plt.xlabel("time (min)",fontsize=16); plt.ylabel("PKA (M)",fontsize=16) 
        plt.ylim([0,1.1e-7])
        
        if saveFigs == True:
            plt.savefig(os.path.join(path_figures,'tc_PKA_PKC_PP1_PP2A_'+str(c_enzymes[ii])+'_input.png'),dpi=300, bbox_inches = "tight")
        plt.show()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          

    
#%% #########################################################
# Steady state dose response simulations
#%% #########################################################

#%% cell 4: Steady state PKA vs PP1/PP2A (Figure 3A, S19)

PP1v = np.array([1e-8,1e-7,1e-6])
PKAv = np.logspace(-11,-5, num=21)
PKAv = PKAv[np.where(PKAv<=6e-6)]

# Time setting for simulations
t0 = 0
t_end = 5*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP1v:
                for jj in PKAv:
                    
                    # parameters
                    c_enzymes = np.array([jj,0,j,0]) #PKA, PKC, PP1, PP2A
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKAv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKAv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKAvsPP1_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKAvsPP1.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP1_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP1.npy'))
         

plot_SS_3D('PKA',PKAv,'PP1', PP1v)

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKAvsPP1.png'),dpi=300, bbox_inches = "tight")


#=====================================================
    
# PKA vs PP2A

PP2Av = np.array([1e-8,1e-7,1e-6])

# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C

simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP2Av:
                for jj in PKAv:
                    
                    # parameters
                    c_enzymes = np.array([jj,0,0,j]) #PKA, PKC, PP1, PP2A
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKAv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKAv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKAvsPP2A_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKAvsPP2A.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP2A_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP2A.npy'))

plot_SS_3D('PKA',PKAv,'PP2A', PP2Av)

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKAvsPP2A.png'),dpi=300, bbox_inches = "tight")


# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
#%% cell 5: Steady state RSK2 vs PP1/PP2A (Figure S18)

PP1v = np.array([1e-8,1e-7,1e-6])
RSK2v = np.logspace(-12,-6, num=20)


# Time setting for simulations
t0 = 0
t_end = 10*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C  

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP1v:
                for jj in RSK2v:
                    
                    # parameters
                    c_enzymes = np.array([0,0,j,0,jj]) #PKA, PKC, PP1, PP2A
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(RSK2v),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(RSK2v),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_RSK2vsPP1_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_RSK2vsPP1.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_RSK2vsPP1_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_RSK2vsPP1.npy'))
         

plot_SS_3D('RSK2',RSK2v,'PP1', PP1v, np.array([1e-12,1e-11,1e-10,1e-9,1e-8,1e-7,1e-6]))

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_RSK2vsPP1.png'),dpi=300, bbox_inches = "tight")

#====================================================================

# RSK2 vs PP2A

PP2Av = np.array([1e-8,1e-7,1e-6])
RSK2v = np.logspace(-12,-6, num=20)


# Time setting for simulations
t0 = 0
t_end = 10*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C  

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP2Av:
                for jj in RSK2v:
                    
                    # parameters
                    c_enzymes = np.array([0,0,j,0,jj]) #PKA, PKC, PP2A, PP2A
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP2Av),len(RSK2v),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP2Av),len(RSK2v),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_RSK2vsPP2A_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_RSK2vsPP2A.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_RSK2vsPP2A_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_RSK2vsPP2A.npy'))
         

plot_SS_3D('RSK2',RSK2v,'PP2A', PP2Av, np.array([1e-12,1e-11,1e-10,1e-9,1e-8,1e-7,1e-6]))
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_RSK2vsPP2A.png'),dpi=300, bbox_inches = "tight")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
#%% cell 6: Steady state PKA vs PP1/PP2A in presence of RSK2 (Figure 3C, S19)

PP1v = np.array([1e-8,1e-7,1e-6])
PKAv = np.logspace(-11,-5, num=21)
PKAv = PKAv[np.where(PKAv<=6e-6)]

# Time setting for simulations
t0 = 0
t_end = 5*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C  

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP1v:
                for jj in PKAv:
                    
                    # parameters
                    c_enzymes = np.array([jj,0,j,0,1e-7]) #PKA, PKC, PP1, PP2A, RSK2
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKAv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKAv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP1_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP1.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP1_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP1.npy'))
         

plot_SS_3D('PKA',PKAv,'PP1', PP1v)
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKA+RSK2vsPP1.png'),dpi=300, bbox_inches = "tight")

# PKA vs PP2A

PP2Av = np.array([1e-8,1e-7,1e-6])

# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C

simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP2Av:
                for jj in PKAv:
                    
                    # parameters
                    c_enzymes = np.array([jj,0,0,j,1e-7]) #PKA, PKC, PP1, PP2A, RSK2
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKAv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKAv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP2A_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP2A.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP2A_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP2A.npy'))

plot_SS_3D('PKA',PKAv,'PP2A', PP2Av)
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKA+RSK2vsPP2A.png'),dpi=300, bbox_inches = "tight")


    
#%% cell 7: Steady state PKC vs PP1/PP2A (Figure S18)

PP1v = np.array([1e-8,1e-7,1e-6])
PKCv = np.logspace(-10,-5, num=20)


# Time setting for simulations
t0 = 0
t_end = 10*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C  

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP1v:
                for jj in PKCv:
                    
                    # parameters
                    c_enzymes = np.array([0,jj,j,0,0]) #PKA, PKC, PP1, PP2A
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKCv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKCv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKCvsPP1_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKCvsPP1.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKCvsPP1_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKCvsPP1.npy'))
         

plot_SS_3D('PKC',PKCv,'PP1', PP1v, np.array([1e-10,1e-9,1e-8,1e-7,1e-6,1e-5]))

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKCvsPP1.png'),dpi=300, bbox_inches = "tight")

 
#====================================================================

# PKC vs PP2A

PP2Av = np.array([1e-8,1e-7,1e-6])

# Time setting for simulations
t0 = 0
t_end = 10*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        

# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C  

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP2Av:
                for jj in PKCv:
                    
                    # parameters
                    c_enzymes = np.array([0,jj,j,0,0]) #PKA, PKC, PP2A, PP2A
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP2Av),len(PKCv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP2Av),len(PKCv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKCvsPP2A_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKCvsPP2A.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKCvsPP2A_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKCvsPP2A.npy'))
         

plot_SS_3D('PKC',PKCv,'PP2A', PP2Av, np.array([1e-10,1e-9,1e-8,1e-7,1e-6,1e-5]))
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKCvsPP2A.png'),dpi=300, bbox_inches = "tight")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#%% cell 8: Steady state PKA vs PP1/PP2A in presence of PKC (Figure 3C, D)

PP1v = np.array([1e-8,1e-7,1e-6])
PKAv = np.logspace(-11,-5, num=21)
PKAv = PKAv[np.where(PKAv<=6e-6)]

# Time setting for simulations
t0 = 0
t_end = 5*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C  

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP1v:
                for jj in PKAv:
                    print(jj)
                    # parameters
                    c_enzymes = np.array([jj,1e-7,j,0,0]) #PKA, PKC, PP1, PP2A, RSK2
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKAv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKAv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1.npy'))
         

plot_SS_3D('PKA', PKAv,'PP1', PP1v)
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKA+PKCvsPP1.png'),dpi=300, bbox_inches = "tight")


plot_SS_3D_noD('PKA', PKAv,'PP1', PP1v)
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKA+PKCvsPP1_lumped.png'),dpi=300, bbox_inches = "tight")

#=====================================================

# PKA vs PP2A

PP2Av = np.array([1e-8,1e-7,1e-6])

# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C

simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP2Av:
                for jj in PKAv:
                    
                    # parameters
                    c_enzymes = np.array([jj,1e-7,0,j,0]) #PKA, PKC, PP1, PP2A, RSK2
                    k = paramsHJ[p,2:32]
                    K = paramsHJ[p,32:62]
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKAv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKAv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP2A_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP2A.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP2A_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP2A.npy'))

plot_SS_3D('PKA',PKAv,'PP2A', PP2Av)
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKA+PKCvsPP2A.png'),dpi=300, bbox_inches = "tight")

plot_SS_3D_noD('PKA',PKAv,'PP2A', PP2Av)
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKA+PKCvsPP2A_lumped.png'),dpi=300, bbox_inches = "tight")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#%% cell 9: Steady state PKA vs PP1 with PP2A parameters for v26 in presence of PKC (Figure 3H)

from scipy.integrate import solve_ivp 

# Load fitted parametersets for PKA, PP1, PP2A
paramsHJ = np.load(os.path.join(path_paramsets,'paramset_final.npy'))
nr_paramsets = paramsHJ.shape[0]

# Add experimentally measured PKC parameters to fitted parameterset
pkc_Kms = np.linspace(3.167e-6,	7.537e-6,4)
pkc_kcat = (5.053+5.262)/2
paramsHJ[:,42] = pkc_Kms[0]
paramsHJ[:,45] = pkc_Kms[1]
paramsHJ[:,48] = pkc_Kms[2]
paramsHJ[:,51] = pkc_Kms[3]
paramsHJ[:,[12,15,18,21]] = pkc_kcat

# Add experimentally measured RSK2 parameters to fitted parameterset
paramsRSK2 = np.array([1.8,1.8,1.3e-6,1.3e-6]) # kcat reaction 31 and 32, Km reaction 31 and 32

k = paramsHJ[:,2:32]
K = paramsHJ[:,32:62]

# # swap parameters
k[:,[19,20]] = k[:,[20,19]]
k[:,[25,26]] = k[:,[26,25]]

K[:,[19,20]] = K[:,[20,19]]
K[:,[25,26]] = K[:,[26,25]]


PP1v = np.array([1e-8,1e-7,1e-6])
PKAv = np.logspace(-11,-5, num=41)

# Time setting for simulations
t0 = 0
t_end = 1*60*60 #h/min/s
h = 1
npts = int(t_end/h)
time = np.linspace(t0,t_end,npts+1)        


# Initial conditions
ICs = np.zeros(9)    #P0,A,Atr,AB,ABG,D,AD,ABD,ABGD
ICs[0] = 20e-6      #0P cMyBP-C  

signalPulses = [0, t_end+1]
simDat_SS = []      
simDat_rel_fracs_SS = []

if loadData == False:   
        for p in range(nr_paramsets):#
            if printSimProg == True:
                print('simulation for parameterset '+str(p+1)+'/'+str(nr_paramsets))
            for j in PP1v:
                for jj in PKAv:
                    c_enzymes = np.array([jj,1e-7,j,0,0]) #PKA, PKC, PP1, PP2A, RSK2
                    
                    
                    additionalParams = paramsHJ[p,62:]
                    params = [k,K,additionalParams,c_enzymes,paramsRSK2]
                    
                    # output = run_simulation(ICs,params,t0,t_end,h,fun.fromIntv,signalPulses,mod.cMyBPC_model_final_RSK2)
                        
                    solution = solve_ivp(mod.cMyBPC_model_final_RSK2, (t0, t_end), ICs, rtol=1.e-8, atol=1.e-8,
                                          t_eval=time, args=(params,fun.fromIntv,signalPulses), method='LSODA')  #RK45, RK23, BDF, LSODA, Radau, DOP853
                    
                    output = solution.y
                    
                    simDat_SS.append(output[:,t_end])
                    simDat_rel_fracs_SS.append([
                        fun.fraction(output,'4P',4)[t_end],
                        fun.fraction(output,'3P',4)[t_end],
                        fun.fraction(output,'2P',4)[t_end],
                        fun.fraction(output,'1P',4)[t_end],
                        fun.fraction(output,'0P',4)[t_end],
                        ])
            
        simDat_SS = np.reshape(simDat_SS, (nr_paramsets,len(PP1v),len(PKAv),9))        
        simDat_rel_fracs_SS = np.reshape(simDat_rel_fracs_SS, (nr_paramsets,len(PP1v),len(PKAv),5))
        
        if saveData == True:
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1pp2ified_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1pp2ified.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1pp2ified_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1pp2ified.npy'))
         

plot_SS_3D('PKA', PKAv,'PP1', PP1v)


if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKA+PKCvsPP1pp2ified.png'),dpi=300, bbox_inches = "tight")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#%% ==~~==~~==~~== DATA ANALYSIS ==~~==~~==~~==~~==~~==~~==~

#%% cell 10: Plot dose response comparisons of fitted Hill parameters (Figure 3F)

# Dictionary to which fitted dose-response parameters will be added
# for statistical analysis. Each entry will be a list consisting of
# nH values, nHs avg, nHs sd, EC50 values, EC50 avg, EC50 sd
doseResponses = {} 



# Hill fits PP1

plt.figure(figsize=(20,4.5))

PP1v = np.array([1e-8,1e-7,1e-6])
PKAv = np.logspace(-11,-5, num=21)
PKAv = PKAv[np.where(PKAv<=6e-6)]

keys = ['PKAPKCvsPP1','PKARSK2vsPP1','PKAvsPP1']


for i in range(3):
    if i == 2:    
        simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP1_relFracs.npy'))
        simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP1.npy'))
    if i == 1:    
        simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP1_relFracs.npy'))
        simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP1.npy'))
    if i == 0:
        simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1_relFracs.npy'))
        simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP1.npy'))
    
    # Dose response fit to Hill equation
    
    PPaseV = PP1v
    nHs_hill = []
    Ks_hill = []
    
    if i == 2: myColor = 'slateblue'; myAlpha = 0.75
    if i == 1 or i == 4: myColor = 'pink'; myAlpha = 1
    if i == 0: myColor = 'red'; myAlpha = 0.55
    
    for p in range(len(PPaseV)):
    
        plt.subplot(1,len(PPaseV)+1,p+1)
            
        for ii in range(nr_paramsets):
            ABG_D = (simDat_SS[ii,p,:,4]+simDat_SS[ii,p,:,8])/np.sum(simDat_SS[ii,p,:,:],1)
            plt.plot(PKAv, ABG_D, 'o', color = myColor, alpha = 0.1)
            par_opt, _ = curve_fit(fun.hillEQ, PKAv, ABG_D, p0 = [1, 1e-9], bounds=(0,[10,1e-3]))
            nHs_hill.append(par_opt[0])
            Ks_hill.append(par_opt[1])
        plt.xscale('log')
        if p == 1:
            plt.xlim(5e-10,1e-6)
        
    nHs_hill = np.reshape(np.asarray(nHs_hill),(len(PPaseV),nr_paramsets))
    nH_avg = np.average(nHs_hill,axis = 1)
    nH_sd = np.std(nHs_hill,axis = 1)
    
    Ks_hill = np.reshape(np.asarray(Ks_hill),(len(PPaseV),nr_paramsets))
    Ks_avg = np.average(Ks_hill,axis = 1)
    Ks_sd = np.std(Ks_hill,axis = 1)
    
    # plot average fit
    for p in range(len(PPaseV)):
        plt.subplot(1,len(PPaseV)+1,p+1)
        plt.plot(PKAv, fun.hillEQ(PKAv,nH_avg[p],Ks_avg[p]), '-', color = myColor, alpha=myAlpha, lw = 2.2)
        plt.title('[PPase] (M) = '+str(PPaseV[p]),fontsize=14)
        #if p == 0: 
        plt.ylabel('fraction $\\alpha\\beta\\gamma$+$\\alpha\\beta\\gamma\\delta$',fontsize=15)
        plt.xlabel('[PKA] (mol/L)',fontsize=15.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
    
    
    # nHs, nHs avg, nHs sd, EC50s, EC50 avg, EC50 sd 
    # nHs and EC50s each of len(PPase)x NrParamsets dimension
    doseResponses[keys[i]] = [nHs_hill,nH_avg,nH_sd,Ks_hill,Ks_avg,Ks_sd]

plt.tight_layout()
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'hillfit_pp1.png'),dpi=400, bbox_inches = "tight")
    

# Hill fits PP2A

plt.figure(figsize=(20,4.5))

PP2Av = np.array([1e-8,1e-7,1e-6])
PKAv = np.logspace(-11,-5, num=21)
PKAv = PKAv[np.where(PKAv<=6e-6)]

keys = ['PKAPKCvsPP2A','PKARSK2vsPP2A','PKAvsPP2A']


for i in range(3):
    if i == 2:    
        simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP2A_relFracs.npy'))
        simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKAvsPP2A.npy'))
    if i == 1:    
        simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP2A_relFracs.npy'))
        simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_RSK2_vsPP2A.npy'))
    if i == 0:
        simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP2A_relFracs.npy'))
        simDat_SS = np.load(os.path.join(path_simdat,'simDat_SS_PKA_PKC_vsPP2A.npy'))
    
    # Dose response fit to Hill equation
    
    PPaseV = PP2Av
    nHs_hill = []
    Ks_hill = []
    
    if i == 2: myColor = 'slateblue'; myAlpha = 0.75
    if i == 1 or i == 4: myColor = 'pink'; myAlpha = 1
    if i == 0: myColor = 'red'; myAlpha = 0.55
    
    for p in range(len(PPaseV)):
    
        plt.subplot(1,len(PPaseV)+1,p+1)
            
        for ii in range(nr_paramsets):
            ABG_D = (simDat_SS[ii,p,:,4]+simDat_SS[ii,p,:,8])/np.sum(simDat_SS[ii,p,:,:],1)
            plt.plot(PKAv, ABG_D, 'o', color = myColor, alpha = 0.1)
            par_opt, _ = curve_fit(fun.hillEQ, PKAv, ABG_D, p0 = [1, 1e-9], bounds=(0,[10,1e-3]))
            nHs_hill.append(par_opt[0])
            Ks_hill.append(par_opt[1])
        plt.xscale('log')
        if p == 1:
            plt.xlim(5e-10,1e-6)
        
    nHs_hill = np.reshape(np.asarray(nHs_hill),(len(PPaseV),nr_paramsets))
    nH_avg = np.average(nHs_hill,axis = 1)
    nH_sd = np.std(nHs_hill,axis = 1)
    
    Ks_hill = np.reshape(np.asarray(Ks_hill),(len(PPaseV),nr_paramsets))
    Ks_avg = np.average(Ks_hill,axis = 1)
    Ks_sd = np.std(Ks_hill,axis = 1)
    
    # plot average fit
    for p in range(len(PPaseV)):
        plt.subplot(1,len(PPaseV)+1,p+1)
        plt.plot(PKAv, fun.hillEQ(PKAv,nH_avg[p],Ks_avg[p]), '-', color = myColor, alpha=myAlpha, lw = 2.2)
        plt.title('[PPase] (M) = '+str(PPaseV[p]),fontsize=14)
        #if p == 0: 
        plt.ylabel('fraction $\\alpha\\beta\\gamma$+$\\alpha\\beta\\gamma\\delta$',fontsize=15)
        plt.xlabel('[PKA] (mol/L)',fontsize=15.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
    
    
    # nHs, nHs avg, nHs sd, EC50s, EC50 avg, EC50 sd 
    # nHs and EC50s each of len(PPase)x NrParamsets dimension
    doseResponses[keys[i]] = [nHs_hill,nH_avg,nH_sd,Ks_hill,Ks_avg,Ks_sd]

plt.tight_layout()
if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'hillfit_pp2a.png'),dpi=400, bbox_inches = "tight")
    

#%% Hill exponents

plt.figure()

ydat_nH = [doseResponses['PKAvsPP1'][1],
            doseResponses['PKARSK2vsPP1'][1],
            doseResponses['PKAPKCvsPP1'][1],
            doseResponses['PKAvsPP2A'][1],
            doseResponses['PKARSK2vsPP2A'][1],
            doseResponses['PKAPKCvsPP2A'][1]
            ]
ydat_nH_err = [doseResponses['PKAvsPP1'][2],
            doseResponses['PKARSK2vsPP1'][2],
            doseResponses['PKAPKCvsPP1'][2],
            doseResponses['PKAvsPP2A'][2],
            doseResponses['PKARSK2vsPP2A'][2],
            doseResponses['PKAPKCvsPP2A'][2]
            ]

for i in range(6):
    if i == 0 or i == 3: myColor = 'slateblue'; myAlpha = 0.5
    if i == 1 or i == 4: myColor = 'pink'; myAlpha = 1
    if i == 2 or i == 5: myColor = 'red'; myAlpha = 0.7
    plt.bar(np.arange(3)+i*3, ydat_nH[i], yerr = ydat_nH_err[i], color=myColor, alpha = myAlpha)

plt.xticks(range(18), [1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6], rotation = 45)
plt.ylim([0,3.5])

plt.xlabel('[Phosphatase] (mol/L)',fontsize=14.5)
plt.ylabel('Hill exponent n$_H$',fontsize=14.5)

if saveFigs == True:
    print(os.path.join(path_figures,'hillExps.png saved'))
    plt.savefig(os.path.join(path_figures,'hillExps.png'),dpi=300, bbox_inches = "tight")


#EC50s

plt.figure()

ydat_ECs = [doseResponses['PKAvsPP1'][4],
            doseResponses['PKARSK2vsPP1'][4],
            doseResponses['PKAPKCvsPP1'][4],
            doseResponses['PKAvsPP2A'][4],
            doseResponses['PKARSK2vsPP2A'][4],
            doseResponses['PKAPKCvsPP2A'][4]
            ]
ydat_ECs_err = [doseResponses['PKAvsPP1'][5],
            doseResponses['PKARSK2vsPP1'][5],
            doseResponses['PKAPKCvsPP1'][5],
            doseResponses['PKAvsPP2A'][5],
            doseResponses['PKARSK2vsPP2A'][5],
            doseResponses['PKAPKCvsPP2A'][5]
            ]

for i in range(6):
    if i == 0 or i == 3: myColor = 'slateblue'; myAlpha = 0.5
    if i == 1 or i == 4: myColor = 'pink'; myAlpha = 1
    if i == 2 or i == 5: myColor = 'red'; myAlpha = 0.7
    plt.bar(np.arange(3)+i*3, ydat_ECs[i], yerr = ydat_ECs_err[i], color=myColor, alpha = myAlpha)

plt.xticks(range(18), [1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6, 1e-8, 1e-7, 1e-6], rotation = 45)

plt.ylim([5e-10,5e-7])
plt.xlabel('[Phosphatase] (mol/L)',fontsize=14.5)
plt.ylabel('EC50 (M)',fontsize=14.5)
plt.yscale('log')

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'ec50s.png'),dpi=300, bbox_inches = "tight")



#%% cell 11: Statistical analysis (Table S1)

print('########################################################')       
print('Statistical analysis of Hill-exponents') 
print('######################################################## \n \n')  


print('Shapiro-Wilk tests for Hill-exponent distributions\n \n') #if pvalue < 0.05, values are likely not from normal distribution

PPaseV = [1e-8,1e-7,1e-6]

for p in range(len(PPaseV)):
    nHs = [doseResponses['PKAvsPP1'][0][p],
                doseResponses['PKARSK2vsPP1'][0][p],
                doseResponses['PKAPKCvsPP1'][0][p],
                doseResponses['PKAvsPP2A'][0][p],
                doseResponses['PKARSK2vsPP2A'][0][p],
                doseResponses['PKAPKCvsPP2A'][0][p]
                ]
    strings = ['PKAvsPP1','PKARSK2vsPP1','PKAPKCvsPP1','PKAvsPP2A','PKARSK2vsPP2A','PKAPKCvsPP2A']
    for i in range(len(nHs)):
        print(strings[i], ', [PPase] = ',PPaseV[p],':', stats.shapiro(nHs[i]),'\n\n')


print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('1 - comparisons within dose response experiment at different [PPase]:') 
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n \n')

strings = ['PKAvsPP1','PKARSK2vsPP1','PKAPKCvsPP1','PKAvsPP2A','PKARSK2vsPP2A','PKAPKCvsPP2A']
pvals = []
for i in range(len(nHs)):
    pvals.append(stats.kruskal(doseResponses[strings[i]][0][0],
                                        doseResponses[strings[i]][0][1],
                                        doseResponses[strings[i]][0][2])[1])
  
corrStat = fdrcorrection(pvals)    

for i in range(len(nHs)):
    print(strings[i],': \n Significantly different? ',corrStat[0][i],  '\n p-value:',corrStat[1][i], '\n' )
    
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('2 -  comparisons across dose responses at given [PPase]:') 
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n \n')

pvals = []
for p in range(len(PPaseV)):
    pvals.append(stats.kruskal(doseResponses[strings[0]][0][p],
                                    doseResponses[strings[1]][0][p],
                                    doseResponses[strings[2]][0][p])[1])
corrStat = fdrcorrection(pvals)    

for p in range(len(PPaseV)):
    print('PP1 at ', PPaseV[p],'mol/L: \n Significantly different? ',corrStat[0][p],  '\n p-value:',corrStat[1][p], '\n')

pvals = []
for p in range(len(PPaseV)):
    pvals.append(stats.kruskal(doseResponses[strings[3]][0][p],
                                    doseResponses[strings[4]][0][p],
                                    doseResponses[strings[5]][0][p])[1])
corrStat = fdrcorrection(pvals)    

for p in range(len(PPaseV)):
    print('PP2A at ', PPaseV[p],'mol/L: \n Significantly different? ',corrStat[0][p],  '\n p-value:',corrStat[1][p], '\n')
      
    
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('3 -  comparisons between PPases:') 
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n \n')

pvals = []
for i in range(3):
    for p in range(len(PPaseV)):
        pvals.append(stats.mannwhitneyu(doseResponses[strings[i]][0][p],doseResponses[strings[3+i]][0][p], alternative='two-sided')[1])

corrStat = fdrcorrection(pvals)    

for i in range(3):
    for p in range(len(PPaseV)):
        ii = i*3+p
        print(strings[i],' ', strings[3+i],' at [PPases] = ',PPaseV[p],': \n Significantly different? ',corrStat[0][ii],  '\n p-value:',corrStat[1][ii], '\n')
  
        
print('########################################################')       
print('Statistical anlysis of EC50 values') 
print('######################################################## \n \n') 


print('Shapiro-Wilk tests for EC50 value distributions\n \n') #if pvalue < 0.05, values are likely not from normal distribution

PPaseV = [1e-8,1e-7,1e-6]

for p in range(len(PPaseV)):
    EC50s = [doseResponses['PKAvsPP1'][3][p],
                doseResponses['PKARSK2vsPP1'][3][p],
                doseResponses['PKAPKCvsPP1'][3][p],
                doseResponses['PKAvsPP2A'][3][p],
                doseResponses['PKARSK2vsPP2A'][3][p],
                doseResponses['PKAPKCvsPP2A'][3][p]
                ]
    strings = ['PKAvsPP1','PKARSK2vsPP1','PKAPKCvsPP1','PKAvsPP2A','PKARSK2vsPP2A','PKAPKCvsPP2A']
    for i in range(len(EC50s)):
        print(strings[i], ', [PPase] = ',PPaseV[p],':', stats.shapiro(EC50s[i]),'\n\n')

print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print(' comparisons between PPases:') 
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n \n')

pvals = []
for i in range(3):
    for p in range(len(PPaseV)):
        pvals.append(stats.mannwhitneyu(doseResponses[strings[i]][3][p],doseResponses[strings[3+i]][3][p], alternative='two-sided')[1])

corrStat = fdrcorrection(pvals)    

for i in range(3):
    for p in range(len(PPaseV)):
        ii = i*3+p
        print(strings[i],' ', strings[3+i],' at [PPases] = ',PPaseV[p],': \n Significantly different? ',corrStat[0][ii],  '\n p-value:',corrStat[1][ii], '\n')
