# -*- coding: utf-8 -*-
"""
This code is a demo for the code associated with the paper:

Thomas Kampourakis, Saraswathi Ponnam, Daniel Koch (2023):
The cardiac myosin binding protein-C phosphorylation state 
as a function of multiple protein kinase and phosphatase activities 
Preprint available under: https://doi.org/10.1101/2023.02.24.529959 

It simulates and plots a single dose-response curve as an average resulting from 
two distinct parametersets and takes approximately 10-15 min to execute.


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
nr_paramsets = 2

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

# Steady state PKA vs PP1 

PP1v = np.array([1e-7])
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
            np.save(os.path.join(path_simdat,'demo_relFracs.npy'),simDat_rel_fracs_SS)
            np.save(os.path.join(path_simdat,'demo.npy'),simDat_SS)
else:    
    simDat_rel_fracs_SS = np.load(os.path.join(path_simdat,'demo_relFracs.npy'))
    simDat_SS = np.load(os.path.join(path_simdat,'demo.npy'))
         

plot_SS_3D('PKA',PKAv,'PP1', PP1v)

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'SS_PKAvsPP1.png'),dpi=300, bbox_inches = "tight")

