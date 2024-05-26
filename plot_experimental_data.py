# -*- coding: utf-8 -*-

"""
This code generates figures 1b, 2f, 2g and 3b from the publication:

Thomas Kampourakis, Saraswathi Ponnam, Kenneth S. Campbell, Austin Wellette-Hunsucker, 
Daniel Koch (2024): The cardiac myosin binding protein-C phosphorylation state as a 
function of multiple protein kinase and phosphatase activities.
Nature Communcations (forthcoming)

README:
    
Before running this script, make sure that the files:
    'exp1_plotting.txt',
    'exp2_plotting.txt' 
    'expSS_PKAvsPP1_plotting.txt' 
    'SYPRO_plotting.txt'
    'MST_unphos.txt'
    'MST_thiophos.txt'
    'pNPP.txt'

are in the subfolder 'experimental data' relative to the directory from which this script
is executed.

Code by Daniel Koch, 2021-2024
"""

#%% Import and misc settings
import os
import sys

#paths
fileDirectory = os.path.dirname(os.path.abspath(__file__))   
path_figures = os.path.join(fileDirectory, 'figures')   
if not os.path.exists(path_figures):
    os.makedirs(path_figures)
path_expdat = os.path.join(fileDirectory, 'experimental data')  
sys.path.append(fileDirectory)

import functions_cMyBPC as fun
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib import cm
from scipy import stats
from statsmodels.stats.multitest import fdrcorrection

plt.rcParams.update({'font.family':'Arial'})

saveFigs = True # saves figures as files

if saveFigs == True and os.path.exists(path_figures) == False:
    os.makedirs(path_figures)


# define colors for plotting
cmap = cm.get_cmap('gnuplot2',7)
colV = []
for i in [0,0.3,0.5,0.6,0.8]: colV.append(cmap(i))
xPstr = ['4P','3P','2P','1P','0P']

# plotting functions

def plot_TC_exp(n,ttl='',flnm=''):
    plt.figure(figsize=(4.1,3.5))
    for i in range(1,6):
        
        plt.plot(np.asarray(time_intp)/60,expDat_interpol[n][i-1,:],'-',color=colV[i-1],lw=2.5)
        means = np.mean(expDat[n][:,(i-1)*expReps[n]:(i-1)*expReps[n]+expReps[n]],1)
        SDs = np.std(expDat[n][:,(i-1)*expReps[n]:(i-1)*expReps[n]+expReps[n]],1) 
        plt.errorbar(time_exp[n]/60,means,yerr=SDs,fmt='o', mfc=colV[i-1], ecolor = 'k', mec ='k', capsize = 5, ms=9)
        plt.ylabel("fraction",fontsize=17)
        plt.ylim(0,1)
        plt.yticks([0,0.25,0.5,0.75,1],fontsize=14)
        plt.xticks(fontsize=14)
        plt.xlabel("time (min)",fontsize=17.5)
           
          
    if saveFigs == True:
        print("figure "+flnm+'.svg'+" saved")
        plt.savefig(os.path.join(path_figures, flnm+'.svg'), bbox_inches = "tight")

    plt.show()
    
def plot_SS_exp(n,figNr = 1, ttl='',flnm=''):
    for i in range(1,5): #3:0P, 2:1P, 1: 2P, 0:3P4P
        
        plt.plot(np.asarray(pka_intp),expDat_interpol[n][i-1,:],'-',color=colV[i],lw=2.5)
        means = np.mean(expDat[n][:,(i-1)*expReps[n]:(i-1)*expReps[n]+expReps[n]],1)
        SDs = np.std(expDat[n][:,(i-1)*expReps[n]:(i-1)*expReps[n]+expReps[n]],1) 
        plt.errorbar(pka_exp,means,yerr=SDs,fmt='o', mfc=colV[i], ecolor = 'k', mec ='k', capsize = 5, ms=9)
        plt.ylabel("fraction",fontsize=17)
        plt.ylim(0,1)
        plt.yticks([0,0.25,0.5,0.75,1],fontsize=14)
        plt.xticks(fontsize=14)
        plt.xlabel("[PKA] (mol/L)",fontsize=17.5)
        plt.xscale('log')


# paths to experimental data
datFlNm = [
    os.path.join(path_expdat, 'exp1_plotting.txt'), # ABD/ABGD + PP1        
    os.path.join(path_expdat, 'exp2_plotting.txt'), # ABD/ABGD + PP2A       
    os.path.join(path_expdat, 'expSS_PKAvsPP1_plotting.txt'), # PKA vs PP1  
    ]

expNames = ['ABD-ABGD+PP1','ABD-ABGD+PP2A', 'SS_PKAvsPP1']
expReps = [3,3,3]


expDat = []   
expDat_interpol = []

# define timepoints for which to interpolate experimental timecourse data
time_exp = []
time_intp = list(range(0,3601))

# define PKA concentrations for which to interpolate experimental dose response data
dataRaw = np.loadtxt(datFlNm[2],delimiter='\t',dtype=str)
pka_exp = np.asarray(dataRaw[1:,0],dtype='float')
pka_intp = np.geomspace(3.125e-9,8e-7,num=100,endpoint=True)
pka_intp = np.append(pka_intp,pka_exp)
pka_intp = np.unique(pka_intp)
pka_intp = np.sort(pka_intp)

# load and interpolate experimental data

for n in range(len(datFlNm)):
    dataRaw = np.loadtxt(datFlNm[n],delimiter='\t',dtype=str)
    dataClean = np.asarray(dataRaw[1:,1:],dtype='float')
    
    if n <=1: #
        t_exp = np.asarray(dataRaw[1:,0],dtype='float')*60
        intpDat = fun.intpExpDat(t_exp,dataClean,time_intp,expReps[n])
        time_exp.append(t_exp)
    
    if n == 2:
        pka_exp = np.asarray(dataRaw[1:,0],dtype='float')
        intpDat = fun.intpExpDat(pka_exp,dataClean,pka_intp,expReps[n])
    
    expDat.append(dataClean)
    expDat_interpol.append(intpDat)
    

# plot timecourse data (Figure 1B)

plot_TC_exp(0,'','exp_4PcMyBPCvsPP1')
plot_TC_exp(1,'','exp_4PcMyBPCvsPP2A')

# plot and analyse experimental SS data (Figure 3B)

plt.figure(1,figsize=(4.1,3.5))

nHs_hill = []
Ks_hill = []

# fit experimental data to Hill-equation
for i in range(3):
    expDat[n][:,(i-1)*expReps[n]:(i-1)*expReps[n]+expReps[n]]
    par_opt, _ = curve_fit(fun.hillEQ, pka_exp, expDat[2][:,i], p0 = [1, 1e-9], bounds=(0,[10,1e-3]))
    nHs_hill.append(par_opt[0])
    Ks_hill.append(par_opt[1])
    plt.xscale('log')
        
# plot experimental and interpolated data 
plot_SS_exp(2,1,'')

# plot Hill-curve 
plt.plot(pka_intp, fun.hillEQ(pka_intp,np.average(nHs_hill),np.average(Ks_hill)), ':',color=colV[1], lw = 5)

if saveFigs == True:
    print("figure "+'exp_SS_PKAvsPP1'+'.svg'+" saved")
    plt.savefig(os.path.join(path_figures, 'exp_SS_PKAvsPP1'+'.svg'), bbox_inches = "tight")
plt.show()

# plot distribution of fitted Hill-exponents
plt.figure(figsize=(0.7,1.5))
plt.plot([1,1,1], nHs_hill, 'o',color=colV[1], mec ='k', alpha = 0.5)
plt.plot([1], np.average(nHs_hill), '_k',ms=15)
plt.xticks([]); plt.ylim([0,3])
plt.title('n$_H$',weight='bold',fontsize=14)
print("figure "+'exp_SS_PKAvsPP1_inset'+'.svg'+" saved")
plt.savefig(os.path.join(path_figures, 'exp_SS_PKAvsPP1_inset'+'.svg'), bbox_inches = "tight")


#%% SYPRO data

# paths to experimental data
datFlNm = os.path.join(path_expdat, 'SYPRO_plotting.txt')

dataRaw = np.loadtxt(datFlNm,delimiter='\t',dtype=str)
SYPRO_exp = np.asarray(dataRaw[1:,:],dtype='float')

plt.figure(figsize=(2.5,4))
plt.plot(np.arange(1,5),np.mean(SYPRO_exp,axis = 0),'_k',ms=20)
for i in range(4):
    plt.scatter(np.ones(4)*(i+1),SYPRO_exp[:,i],color=colV[4-i],s=70,ec='k')

plt.ylabel('Normalized Fluorescence (600 nm)',fontsize=15)
plt.xlim(0,5)
plt.ylim(0.9,1.125)
plt.yticks(fontsize=13)
ax = plt.gca()
ax.set_xticks(np.arange(1,5))
xlabs = ['0P','$\\alpha$','$\\alpha\\beta$','$\\alpha\\beta\\gamma$']
ax.set_xticklabels(xlabs,rotation = 45,size=15)  
plt.savefig(os.path.join(path_figures, 'SYPROdata.svg'),dpi=400, bbox_inches = "tight")


print('Analysis Sypro data')
print('-------------------')
pvals = []
for i in range(3):
    pvals.append(stats.ttest_ind(SYPRO_exp[:,0], SYPRO_exp[:,i+1], equal_var=True)[1])
    # pvals.append(stats.ttest_1samp(a=SYPRO_exp[:,i+1], popmean=100)[1])
stats_corrected = fdrcorrection(pvals)
for i in range(3):
    print(['alpha','alpha,beta','alpha,beta,gamma'][i]+' significantly different from 0P? ', stats_corrected[0][i], ' p = ', stats_corrected[1][i])

#%% MST data

# paths to experimental data
datFlNm = os.path.join(path_expdat, 'MST_unphos.txt')
dataRaw = np.loadtxt(datFlNm,delimiter='\t',dtype=str)
dataRaw[np.where(dataRaw == '')]=np.nan
MST_unphos_exp = np.asarray(dataRaw[1:,:],dtype='float')
datFlNm = os.path.join(path_expdat, 'MST_thiophos.txt')
dataRaw = np.loadtxt(datFlNm,delimiter='\t',dtype=str)
dataRaw[np.where(dataRaw == '')]=np.nan
MST_thiophos_exp = np.asarray(dataRaw[1:,:],dtype='float')

plt.figure(figsize=(4,4))
for i in range(MST_unphos_exp.shape[0]-1):
    m = MST_unphos_exp[i,1:]
    idcs = np.where(np.invert(np.isnan(m)))[0]
    m_n = m[idcs]
    plt.errorbar(MST_unphos_exp[i,0]*1e-6, np.mean(m_n),yerr=np.std(m_n)/np.sqrt(len(m_n)),fmt='o',color=colV[4])
    
for i in range(MST_thiophos_exp.shape[0]-1):
    m = MST_thiophos_exp[i,1:]
    idcs = np.where(np.invert(np.isnan(m)))[0]
    m_n = m[idcs]
    plt.errorbar(MST_thiophos_exp[i,0]*1e-6, np.mean(m_n),yerr=np.std(m_n)/np.sqrt(len(m_n)),fmt='o',color=colV[0])
    
par_unphos = []
par_thiophos = []

# fit
for i in range(MST_unphos_exp.shape[1]-1):

    m = MST_unphos_exp[:,i+1]
    idcs = np.where(np.invert(np.isnan(m)))[0]
    m_n = m[idcs]
    ligand = MST_unphos_exp[idcs,0]*1e-6
    
    par_opt, _ = curve_fit(fun.bindingEQ, ligand, m_n, p0 = [0.05*1e-6, 0.5, 0.5, 1e-6], bounds=([0.049*1e-6,0,0,0.01*1e-6],[0.05*1e-6,1,1,10*1e-6]))
    par_unphos.append(par_opt[:])

for i in range(MST_thiophos_exp.shape[1]-1):

    m = MST_thiophos_exp[:,i+1]
    idcs = np.where(np.invert(np.isnan(m)))[0]
    m_n = m[idcs]
    ligand = MST_thiophos_exp[idcs,0]*1e-6
    
    par_opt, _ = curve_fit(fun.bindingEQ, ligand, m_n, p0 = [0.05*1e-6, 0.5, 0.5, 1e-6], bounds=([0.049*1e-6,0,0,0.01*1e-6],[0.05*1e-6,1,1,10*1e-6]))
    par_thiophos.append(par_opt[:])

par_unphos = np.asarray(par_unphos)
par_thiophos = np.asarray(par_thiophos)
par_unphos_mean = np.mean(par_unphos,axis=0)
par_thiophos_mean = np.mean(par_thiophos,axis=0)

x = np.logspace(-2,2,100)*1e-6
plt.plot(x, fun.bindingEQ(x,par_unphos_mean[0],par_unphos_mean[1],par_unphos_mean[2],par_unphos_mean[3]),'-',color=colV[4],label='unphosphorylated')
plt.plot(x, fun.bindingEQ(x,par_thiophos_mean[0],par_thiophos_mean[1],par_thiophos_mean[2],par_thiophos_mean[3]),'-',color=colV[0],label='thiophosphorylated')

plt.xscale('log')
plt.xlim(0.01*1e-6, 20*1e-6)
plt.ylabel('fraction bound',fontsize=15)
plt.xlabel('[cMyBP-C] (mol/L)',fontsize=15)
plt.yticks(fontsize=13)
plt.xticks(fontsize=13)
plt.legend(fontsize=13)

if saveFigs == True:
    print("figure "+'exp_MST'+'.svg'+" saved")
    plt.savefig(os.path.join(path_figures, 'exp_MST'+'.svg'), bbox_inches = "tight")

plt.figure(figsize=(0.8,1.8))
plt.bar([0,1], 
        [par_unphos_mean[3],par_thiophos_mean[3]], 
        yerr =  [np.std(par_unphos[:,3])/np.sqrt(len(par_unphos[:,3])),np.std(par_thiophos[:,3])/np.sqrt(len(par_thiophos[:,3]))],
        color=[colV[4],colV[0]],alpha = 0.6)

plt.plot(np.zeros(len(par_unphos[:,3])),par_unphos[:,3],'o',color=colV[4])
plt.plot(np.ones(len(par_thiophos[:,3])),par_thiophos[:,3],'o',color=colV[0])
plt.ylim(0,1.65e-6)
plt.ylabel('$K_d$ (mol/L)',fontsize=15)
plt.xticks([])

if saveFigs == True:
    print("figure "+'exp_MST_inset'+'.svg'+" saved")
    plt.savefig(os.path.join(path_figures, 'exp_MST_inset'+'.svg'), bbox_inches = "tight")

# T-test
print('Kd of thiophosphorylated lower than unphosphorylated? p=',stats.ttest_ind(par_unphos[:,3],par_thiophos[:,3],alternative='greater',equal_var=False)[1])


#%% pNPP data

# paths to experimental data
datFlNm = os.path.join(path_expdat, 'pNPP.txt')
dataRaw = np.loadtxt(datFlNm,delimiter='\t',dtype=str)
pNPP_exp = np.flipud(np.asarray(dataRaw[1:,:],dtype='float'))


# fit
par_MM_pp1 = []
par_MM_pp1_c1mc2  = []
par_MM_pp1_tpc1mc2 = []

pNPP_pp1 = pNPP_exp[:pNPP_exp.shape[0]-1,1:4]
pNPP_pp1_c1mc2 = pNPP_exp[:pNPP_exp.shape[0]-1,4:7]
pNPP_pp1_tpc1mc2 = pNPP_exp[:pNPP_exp.shape[0]-1,7:]
substrate = pNPP_exp[:pNPP_exp.shape[0]-1,0]*1e-3

for i in range(3):
    par_opt, _ = curve_fit(fun.mmEQ, substrate, pNPP_pp1[:,i], p0 = [0.005,20e-3], bounds=([0,0],[1,1]))
    par_MM_pp1.append(par_opt[:])
    par_opt, _ = curve_fit(fun.mmEQ, substrate, pNPP_pp1_c1mc2[:,i], p0 = [0.005,20e-3], bounds=([0,0],[1,1]))
    par_MM_pp1_c1mc2.append(par_opt[:])
    par_opt, _ = curve_fit(fun.mmEQ, substrate, pNPP_pp1_tpc1mc2[:,i], p0 = [0.005,20e-3], bounds=([0,0],[1,1]))
    par_MM_pp1_tpc1mc2.append(par_opt[:])
    
par_MM_pp1 = np.asarray(par_MM_pp1)    
par_MM_pp1_c1mc2 = np.asarray(par_MM_pp1_c1mc2)
par_MM_pp1_tpc1mc2 = np.asarray(par_MM_pp1_tpc1mc2)
 
plt.figure()
plt.subplot(1,2,1)
plt.title('Vmax')
plt.scatter(1*np.ones(3),par_MM_pp1[:,0],label='PP1 only')
plt.scatter(2*np.ones(3),par_MM_pp1_c1mc2[:,0],label='PP1 + C1mC1')
plt.scatter(3*np.ones(3),par_MM_pp1_tpc1mc2[:,0],label='PP1 + thiophos. C1mC2')
plt.xticks([])
plt.legend()
plt.subplot(1,2,2)
plt.title('Km')
plt.scatter(1*np.ones(3),par_MM_pp1[:,1],label='PP1 only')
plt.scatter(2*np.ones(3),par_MM_pp1_c1mc2[:,1],label='PP1 + C1mC1')
plt.scatter(3*np.ones(3),par_MM_pp1_tpc1mc2[:,1],label='PP1 + thiophos. C1mC2')
plt.xticks([])
plt.legend()
plt.tight_layout()

anova_Vmax = stats.f_oneway(par_MM_pp1[:,0],par_MM_pp1_c1mc2[:,0],par_MM_pp1_tpc1mc2[:,0])[1]
anova_Km = stats.f_oneway(par_MM_pp1[:,1],par_MM_pp1_c1mc2[:,1],par_MM_pp1_tpc1mc2[:,1])[1]

print('Vmax/Km of pNPP assay different between conditions? p = '+str(anova_Vmax)+'/'+str(anova_Km))

# plot

plt.figure(figsize=(4,4))
for i in range(pNPP_exp.shape[0]-1):
    pNPP_pp1 = pNPP_exp[i,1:4]
    pNPP_pp1_c1mc2 = pNPP_exp[i,4:7]
    pNPP_pp1_tpc1mc2 = pNPP_exp[i,7:]
    plt.errorbar(pNPP_exp[i,0]*1e-3, np.mean(pNPP_pp1),yerr=np.std(pNPP_pp1)/np.sqrt(len(pNPP_pp1)),fmt='o',color='teal')
    plt.errorbar(pNPP_exp[i,0]*1e-3, np.mean(pNPP_pp1_c1mc2),yerr=np.std(pNPP_pp1_c1mc2)/np.sqrt(len(pNPP_pp1_c1mc2)),fmt='o',color=colV[4])
    plt.errorbar(pNPP_exp[i,0]*1e-3, np.mean(pNPP_pp1_tpc1mc2),yerr=np.std(pNPP_pp1_tpc1mc2)/np.sqrt(len(pNPP_pp1_tpc1mc2)),fmt='o',color=colV[0])
    

x = np.linspace(0,0.045,100)
plt.plot(x, fun.mmEQ(x,np.mean(par_MM_pp1[:,0]),np.mean(par_MM_pp1[:,1])),'-',color='teal',label='PP1')
plt.plot(x, fun.mmEQ(x,np.mean(par_MM_pp1_c1mc2[:,0]),np.mean(par_MM_pp1_c1mc2[:,1])),'-',color=colV[4],label='PP1 + C1mC2 (unphos.)')
plt.plot(x, fun.mmEQ(x,np.mean(par_MM_pp1_tpc1mc2[:,0]),np.mean(par_MM_pp1_tpc1mc2[:,1])),'-',color=colV[0],label='PP1 + C1mC2 (thiophos.)')
          
plt.ylabel('rate (a.u.)',fontsize=15)
plt.xlabel('[pNPP] (mol/L)',fontsize=15)
plt.yticks(fontsize=13)
plt.xticks(fontsize=13)
plt.legend(fontsize=13)    

if saveFigs == True:
    print("figure "+'exp_pNPP'+'.svg'+" saved")
    plt.savefig(os.path.join(path_figures, 'exp_pNPP'+'.svg'), bbox_inches = "tight")



