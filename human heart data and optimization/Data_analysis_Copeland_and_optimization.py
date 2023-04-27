# -*- coding: utf-8 -*-
"""
This code reproduces Figures 4A-C and S22-27 from the publication:

Thomas Kampourakis, Saraswathi Ponnam, Daniel Koch (2023):
The cardiac myosin binding protein-C phosphorylation state 
as a function of multiple protein kinase and phosphatase activities 
Preprint available under: https://doi.org/10.1101/2023.02.24.529959 

It also reproduces the statistical analysis shown in these figures.

Code by Daniel Koch, 2021-2023
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.multitest import fdrcorrection
from matplotlib.pyplot import cm

# Set working directory to location of the current file
os.chdir(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams.update({'font.family':'Arial'})
fileDirectory = os.path.dirname(os.path.abspath(__file__))
path_figures = os.path.join(fileDirectory, 'figures')   
path_results = os.path.join(fileDirectory, 'results')   

saveFigs=True

if saveFigs == True and os.path.exists(path_figures) == False:
    os.makedirs(path_figures)


#%% Analysis model and Copeland data

####### Experimental data from Copeland et al. 2010  ###########
nsamples_donor = 21
means_donor = np.array([0.093, 0.134, 0.105, 0.287, 0.364])
SEMs_donor = np.array([0.001, 0.027, 0.033, 0.037, 0.027])
SDs_donor = SEMs_donor*np.sqrt(nsamples_donor)

nsamples_HF = 19
means_HF = np.array([0.601,0.278,0.048,0.037,0.028])
SEMs_HF = np.array([0.028,0.048,0.02,0.012,0.013])
SDs_HF = SEMs_HF*np.sqrt(nsamples_HF)
###############################################################

# Load fitted/predicted values concentrations for matching Copeland et al 2010 heart data
fitvalsDonorHearts = np.load(os.path.join(path_results,'fittedMyBPCstates_Copeland_DonorHearts.npy'))
fitvalsFailingHearts = np.load(os.path.join(path_results,'fittedMyBPCstates_Copeland_FailingHearts.npy'))
predvalsFailingHearts = np.load(os.path.join(path_results,'predictedMyBPCstates_Copeland_FailingHearts.npy'))

fitvalsDonorHeartsCtrl = np.load(os.path.join(path_results,'fittedMyBPCstates_Copeland_DonorHearts_ctrl.npy'))
fitvalsFailingHeartsCtrl = np.load(os.path.join(path_results,'fittedMyBPCstates_Copeland_FailingHearts_ctrl.npy'))

# process data

means_donor_fit = np.mean(fitvalsDonorHearts,axis=0)
SDs_donor_fit = np.std(fitvalsDonorHearts,axis=0)
SEMs_donor_fit = SDs_donor_fit/np.sqrt(fitvalsDonorHearts.shape[0])

means_HF_fit = np.mean(fitvalsFailingHearts,axis=0)
SDs_HF_fit= np.std(fitvalsFailingHearts,axis=0)
SEMs_HF_fit = SDs_HF_fit/np.sqrt(fitvalsFailingHearts.shape[0])

means_HF_predicted = np.mean(predvalsFailingHearts,axis=0)
SDs_HF_predicted= np.std(predvalsFailingHearts,axis=0)
SEMs_HF_predicted = SDs_HF_predicted/np.sqrt(predvalsFailingHearts.shape[0])

means_donor_fit_ctrl = np.mean(fitvalsDonorHeartsCtrl,axis=0)
SDs_donor_fit_ctrl = np.std(fitvalsDonorHeartsCtrl,axis=0)
SEMs_donor_fit_ctrl = SDs_donor_fit_ctrl/np.sqrt(fitvalsDonorHeartsCtrl.shape[0])

means_HF_fit_ctrl = np.mean(fitvalsFailingHeartsCtrl,axis=0)
SDs_HF_fit_ctrl= np.std(fitvalsFailingHeartsCtrl,axis=0)
SEMs_HF_fit_ctrl = SDs_HF_fit/np.sqrt(fitvalsFailingHeartsCtrl.shape[0])


#%% Plot Copeland data and fitted values (Figure 4A)

cmap = cm.get_cmap('gnuplot2',7)
colV = []
for i in [0,0.3,0.5,0.6,0.8]: colV.append(cmap(i)[:3])
c4P,c3P,c2P,c1P,c0P = colV

c4P_2 =  (0.25,0.25,0.25) 
# c3P =  (159/255, 5/255, 240/255) 
# c2P =  (206/255, 6/255, 101/255) 
# c1P =  (232/255, 116/255, 0/255) 
# c0P =  (255/255, 192/255, 128/255) 
colors = [c0P,c1P,c2P,c3P,c4P_2]
pstates = ['0P','1P','2P','3P','4P']
width = 0.35 

colorV = np.vstack((np.array([0.3,0.2,0.9,1]),
    cm.RdPu(np.linspace(0, 1, 8))[4:,:]))

fig, ax = plt.subplots()

btm_donor = 0
btm_donor_fit = 0
btm_HF = 0
btm_HF_predicted = 0
btm_HF_fit = 0

for i in range(5):
    ax.bar(0, means_donor[i], width, yerr=SEMs_donor[i], bottom=btm_donor,label=pstates[i],color = colors[i],alpha=0.9)
    ax.bar(0.5, means_donor_fit[i], width, yerr=SEMs_donor_fit[i], bottom=btm_donor_fit,color = colors[i],alpha=0.9)
    ax.bar(1.5, means_HF[i], width, yerr=SEMs_HF[i], bottom=btm_HF,color = colors[i],alpha=0.9)
    ax.bar(2, means_HF_fit[i], width, yerr=SEMs_HF_fit[i], bottom=btm_HF_fit,color = colors[i],alpha=0.9)
    ax.bar(1, means_HF_predicted[i], width, yerr=SEMs_HF_predicted[i], bottom=btm_HF_predicted,color = colors[i],alpha=0.9)
    
    btm_donor = btm_donor + means_donor[i]
    btm_donor_fit = btm_donor_fit + means_donor_fit[i]
    btm_HF = btm_HF + means_HF[i]
    btm_HF_predicted = btm_HF_predicted + means_HF_predicted[i]
    btm_HF_fit = btm_HF_fit + means_HF_fit[i]
        
ax.set_xticks([0,0.5,1,1.5,2])
ax.set_xticklabels(['donor (CL)','donor (fit)','HF (predicted)','HF (CL)','HF (fit)'],rotation=40)
ax.set_ylabel('cumulative fraction',fontsize=14)
ax.set_ylim(-0.05,1.05)
ax.set_xlim(-0.25,2.25)
plt.legend(bbox_to_anchor=(1,1), loc="upper left") 

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'phosphostates_Copeland_vs_model.png'),dpi=300, bbox_inches = "tight")

#%% control experiment with fixed phosphatase ratios (Figure S22)

fig, ax = plt.subplots(figsize=(5,5))

btm_donor = 0
btm_donor_fit = 0
btm_HF = 0
btm_HF_fit = 0

for i in range(5):
    ax.bar(0, means_donor[i], width, yerr=SEMs_donor[i], bottom=btm_donor,label=pstates[i],color = colors[i],alpha=0.9)
    ax.bar(0.5, means_donor_fit_ctrl[i], width, yerr=SEMs_donor_fit_ctrl[i], bottom=btm_donor_fit,color = colors[i],alpha=0.9)
    ax.bar(1, means_HF[i], width, yerr=SEMs_HF[i], bottom=btm_HF,color = colors[i],alpha=0.9)
    ax.bar(1.5, means_HF_fit_ctrl[i], width, yerr=SEMs_HF_fit_ctrl[i], bottom=btm_HF_fit,color = colors[i],alpha=0.9)
   
    btm_donor = btm_donor + means_donor[i]
    btm_donor_fit = btm_donor_fit + means_donor_fit_ctrl[i]
    btm_HF = btm_HF + means_HF[i]
    btm_HF_fit = btm_HF_fit + means_HF_fit_ctrl[i]
        
ax.set_xticks([0,0.5,1,1.5])
ax.set_xticklabels(['donor (CL)','donor (fit, PP1/PPases$_{tot}$=1)','HF (CL)','HF (fit, PP2A/PPases$_{tot}$=1)'],rotation=60)
ax.set_ylabel('cumulative fraction',fontsize=14)
ax.set_ylim(-0.05,1.05)
ax.set_xlim(-0.25,1.75)
plt.legend(bbox_to_anchor=(1,1), loc="upper left") 

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'phosphostates_Copeland_vs_model_ctrl.png'),dpi=300, bbox_inches = "tight")


#%% Statistical analysis of fitted enzyme vectors for donor vs failing hearts

# Load fitted enzyme concentrations for matching Copeland et al 2010 heart data

enzymesDonorHearts = np.load(os.path.join(path_results,'fittedEnzymeConcentrations_Copeland_DonorHearts.npy'))
enzymesDonorHearts = enzymesDonorHearts[:,2:] # PKA, PKC, PP1, total Phosphatases, RSK2 
enzymesDonorHearts[:,3] = enzymesDonorHearts[:,3] - enzymesDonorHearts[:,2] # PKA, PKC, PP1, PP2A, RSK2 
enzymesDonorHearts[enzymesDonorHearts < 1e-15] = 0 

enzymesFailingHearts = np.load(os.path.join(path_results,'fittedEnzymeConcentrations_Copeland_FailingHearts.npy'))
enzymesFailingHearts = enzymesFailingHearts[:,2:] # PKA, PKC, PP1, total Phosphatases, RSK2 
enzymesFailingHearts[:,3] = enzymesFailingHearts[:,3] - enzymesFailingHearts[:,2] # PKA, PKC, PP1, PP2A, RSK2 
enzymesFailingHearts[enzymesFailingHearts < 1e-15] = 0 


print('########################################################')       
print('Statistical analysis of enzyme vectors healthy/HF donors') 
print('######################################################## \n \n')  


print('Shapiro-Wilk tests for enzyme vector distributions\n \n') #if pvalue < 0.05, values are likely not from normal distribution

enzymes = ['PKA', 'PKC', 'PP1', 'PP2A', 'RSK2']

for i in range(5):
    print(enzymes[i], ' for healthy donors: ', stats.shapiro(enzymesDonorHearts[:,i]),'\n\n')
for i in range(5):
    print(enzymes[i], ' for HF donors: ', stats.shapiro(enzymesFailingHearts[:,i]),'\n\n')
    
print('Mann-Whitney tests for enzyme vector distributions\n \n') 
pvals = []
for i in range(5):
    pvals.append(stats.mannwhitneyu(enzymesDonorHearts[:,i],enzymesFailingHearts[:,i], alternative='two-sided')[1])

pvals.append(stats.mannwhitneyu(enzymesDonorHearts[:,2]+enzymesDonorHearts[:,3],enzymesFailingHearts[:,2]+enzymesFailingHearts[:,3], alternative='two-sided')[1])
 
pvals_corrected = fdrcorrection(pvals)[1]   

for i in range(5):
    print(enzymes[i], ' Mann-Whitney healthy vs HF, p= ', pvals_corrected[i],'\n\n')
print('Total Phosphatases, Mann-Whitney healthy vs HF, p= ', pvals_corrected[5],'\n\n')
      
#%% Polar coordinate bar plots (Figure 4B)

nbars = 10
thetaCoords = []
barwidth = 2*np.pi/nbars*0.9
bullseye = 0.3
min10 = -11
max10 = -5

idcs1 = [0,2,4,6,8]
idcs2 = [1,3,5,7,9]

y1 = np.mean(enzymesDonorHearts,axis=0)
y1[y1 == 0] = 1e-11
y2 = np.mean(enzymesFailingHearts,axis=0)
y2[y2 == 0] = 1e-11
yerr1 = np.std(enzymesDonorHearts,axis=0)/np.sqrt(35)
yerr2 = np.std(enzymesFailingHearts,axis=0)/np.sqrt(35)

yerr1_top = y1 + yerr1
yerr1_btm = y1 - yerr1
yerr1_top = np.log10(yerr1_top) - min10 + bullseye
yerr1_btm = np.log10(yerr1_btm) - min10 + bullseye

yerr2_top = y2 + yerr2
yerr2_btm = y2 - yerr2
yerr2_top = np.log10(yerr2_top) - min10 + bullseye
yerr2_btm = np.log10(yerr2_btm) - min10 + bullseye

y1[y1 == 0] = 1e-11
y1 = np.log10(y1) - min10 + bullseye

y2[y2 == 0] = 1e-11
y2 = np.log10(y2) - min10 + bullseye

thetaCoords = np.linspace(0, 2 * np.pi, nbars, endpoint=False)

a = 0.7

plt.figure()
thetaCoords = np.asarray(thetaCoords)
ax = plt.gcf().add_subplot(1,1,1,projection= 'polar')

ax.bar(x=thetaCoords[idcs1], height=y1,width=barwidth, color = colorV[0],alpha=a,label='donor')
ax.bar(x=thetaCoords[idcs2], height=y2,width=barwidth, color = colorV[1],alpha=a,label='HF')

for i in range(5):
    ax.plot([thetaCoords[idcs1[i]],thetaCoords[idcs1[i]]], [yerr1_top[i],yerr1_btm[i]], '-k')
    ax.plot([thetaCoords[idcs2[i]],thetaCoords[idcs2[i]]], [yerr2_top[i],yerr2_btm[i]], '-k')

l = np.arange(np.floor(min10), -5)
ax.set_rticks(l - min10 + bullseye) 
ax.set_yticklabels([])
ax.set_rlim(0, max10 - min10 + bullseye)

plt.legend(bbox_to_anchor=(1,1), loc="upper left")
ax.set_xticks(
    [thetaCoords[1]+np.pi/nbars,
      thetaCoords[3]+np.pi/nbars,
      thetaCoords[5]+np.pi/nbars,
      thetaCoords[7]+np.pi/nbars,
      thetaCoords[9]+np.pi/nbars],[])

plt.tight_layout()

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'EnzymesFitted_Copeland_vs_model.png'),dpi=300, bbox_inches = "tight")

#%% Kinase/Phosphatase ratio (Figure 4B inset)

totPPases_donor = enzymesDonorHearts[:,2] + enzymesDonorHearts[:,3]
totPPases_HF = enzymesFailingHearts[:,2] + enzymesFailingHearts[:,3]

kin_donor = enzymesDonorHearts[:,0] #+ enzymesDonorHearts[:,1] #+ enzymesDonorHearts[:,4]
kin_HF = enzymesFailingHearts[:,0] #+ enzymesFailingHearts[:,1] #+ enzymesFailingHearts[:,4]

totPkaPPratio_donor = kin_donor/totPPases_donor
totPkaPPratio_HF = kin_HF/totPPases_HF

plt.figure(figsize=(1,2))
plt.bar([0,1], 
        [np.mean(totPkaPPratio_donor),np.mean(totPkaPPratio_HF)], 
        yerr =  [np.std(totPkaPPratio_donor)/np.sqrt(len(totPkaPPratio_donor)),
                  np.std(totPkaPPratio_HF)/np.sqrt(len(totPkaPPratio_HF))],
        color=[colorV[0],colorV[1]],alpha = a, label=['donor,HF'])


plt.ylabel('[PKA]/[phosphatase]$_{tot}$')
plt.xticks([])


plt.ylim([0,0.175])

if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'totalKinPPaseRatioFitted_Copeland_vs_model.png'),dpi=300, bbox_inches = "tight")


p = stats.mannwhitneyu(totPkaPPratio_donor,totPkaPPratio_HF, alternative='two-sided')[1]

print('Total Kin/PPases HF/Donor: ', str(np.mean(totPkaPPratio_HF)/np.mean(totPkaPPratio_donor)), 'significant? p=', p )

# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#%% Max possible fractions (Figure 4C)
    
ttls = ['0P','$\\alpha$','$\\alpha\\beta$','$\\alpha\\beta\\gamma$',
        '$\\delta$','$\\alpha\\delta$','$\\alpha\\beta\\delta$',
        '$\\alpha\\beta\\delta\\gamma$']

optResult_healthy = np.load(os.path.join(path_results,'optResult_healthy.npy'))
optResult_HF = np.load(os.path.join(path_results,'optResult_HF.npy'))
optResult_HF_fixPP1 = np.load(os.path.join(path_results,'optResult_HF_PP1fixed.npy'))
optResult_HF_fixPP2A = np.load(os.path.join(path_results,'optResult_HF_PP2Afixed.npy'))
optResult_HF_PPfree = np.load(os.path.join(path_results,'optResult_HF_PPasesFree.npy'))


nPKA, nPPtot, nstates, nparamsets = optResult_healthy.shape[:4]

data_healthy = optResult_healthy[0,0,:,:,:]
data_HF_clean = optResult_HF[0,0,:,:,:]
data_HF_PPfree = optResult_HF_PPfree[0,0,:,:,:]
data_HF_fixPP1 = optResult_HF_fixPP1[0,0,:,:,:]
data_HF_fixPP2A = optResult_HF_fixPP2A[0,0,:,:,:]

# calculate PP2A
for i in range(nstates):
    for ii in range(nparamsets):
        data_HF_fixPP1[i,ii,5] = data_HF_fixPP1[i,ii,5] - data_HF_fixPP1[i,ii,4]
        data_HF_fixPP2A[i,ii,5] = data_HF_fixPP2A[i,ii,5] - data_HF_fixPP2A[i,ii,4]
        data_HF_PPfree[i,ii,5] = data_HF_PPfree[i,ii,5] - data_HF_PPfree[i,ii,4]


plt.figure(figsize=(14,4))

plt.vlines([5.5,10.5,15.5,20.5,25.5,30.5,35.5],0,1.33,colors='k',lw=1.2)

for i in range(8):
    for ii in range(1,6):
        # print('test2',str((i,ii)))
        if ii%5 == 1: 
            myColor = colorV[0]
            plt.bar(i*5+ii, np.average(data_healthy[i,:,0]), yerr = max(np.std(data_healthy[i,:,0]),0.005), color=myColor, alpha =0.6)
            plt.scatter((i*5+ii)*np.ones(np.size(data_healthy[i,:,0])), data_healthy[i,:,0], color=myColor,s=20,alpha=0.4)
        elif ii%5 == 2:   
            myColor = colorV[1]
            plt.bar(i*5+ii, np.average(data_HF_clean[i,:,0]), yerr = max(np.std(data_HF_clean[i,:,0]),0.005), color=myColor, alpha =0.6)
            plt.scatter((i*5+ii)*np.ones(np.size(data_HF_clean[i,:,0])), data_HF_clean[i,:,0], color=myColor,s=20,alpha=0.4)
        elif ii%5 == 3:
            myColor = colorV[2]
            plt.bar(i*5+ii, np.average(data_HF_PPfree[i,:,0]), yerr = max(np.std(data_HF_PPfree[i,:,0]),0.005), color=myColor, alpha =0.6)
            plt.scatter((i*5+ii)*np.ones(np.size(data_HF_PPfree[i,:,0])), data_HF_PPfree[i,:,0], color=myColor,s=20,alpha=0.8)
        elif ii%5 == 4:
             myColor = colorV[3]
             plt.bar(i*5+ii, np.average(data_HF_fixPP1[i,:,0]), yerr = max(np.std(data_HF_fixPP1[i,:,0]),0.005), color=myColor, alpha =0.5)
             plt.scatter((i*5+ii)*np.ones(np.size(data_HF_fixPP1[i,:,0])), data_HF_fixPP1[i,:,0], color=myColor,s=20,alpha=0.5)
        else:
            myColor = colorV[4]
            plt.bar(i*5+ii, np.average(data_HF_fixPP2A[i,:,0]), yerr = max(np.std(data_HF_fixPP2A[i,:,0]),0.005), color=myColor, alpha =0.7)
            plt.scatter((i*5+ii)*np.ones(np.size(data_HF_fixPP2A[i,:,0])), data_HF_fixPP2A[i,:,0], color=myColor,s=20,alpha=0.9)
           
            
plt.xlim([0,41])
plt.xticks(np.linspace(3,38,8),['0P','$\\alpha$','$\\alpha\\beta$','$\\alpha\\beta\\gamma$','$\\delta$','$\\alpha\\delta$','$\\alpha\\beta\\delta$','$\\alpha\\beta\\delta\\gamma$'],rotation = 45,fontsize=16)
plt.yticks(fontsize=14)
plt.ylabel('Maximum possible fraction',fontsize=16)
# plt.title('PKA$_{max}$ = ' + str(vPKA[0]) + ' mol/L, Phosphatases$_{tot}$ = ' + str(vPPase[1]) + ' mol/L')
plt.ylim([0,1.33])
plt.yticks([0,0.2,0.4,0.6,0.8,1])
path = os.path.join(fileDirectory,'_')


if saveFigs == True:
    plt.savefig(os.path.join(path_figures,'maxVals.png'),dpi=300, bbox_inches = "tight")

plt.show()

#%% Statistical analyses of maximal fraction values

print('Shapiro-Wilk tests for max fraction value distributions\n \n') #if pvalue < 0.05, values are likely not from normal distribution

state = ['0P','$\\alpha$','$\\alpha\\beta$','$\\alpha\\beta\\gamma$','$\\delta$','$\\alpha\\delta$','$\\alpha\\beta\\delta$','$\\alpha\\beta\\delta\\gamma$']

for i in range(8):
    print(state[i], ', healthy: ',              stats.shapiro(data_healthy[i,:,0]),'\n')
    print(state[i], ', HF: ',                   stats.shapiro(data_HF_clean[i,:,0]),'\n')
    print(state[i], ', HF, free PPase ratio: ', stats.shapiro(data_HF_PPfree[i,:,0]),'\n')
    print(state[i], ', HF, PP2A fixed: ',       stats.shapiro(data_HF_fixPP2A[i,:,0]),'\n')
    print(state[i], ', HF, PP1 fixed: ',        stats.shapiro(data_HF_fixPP1[i,:,0]),'\n')
print('######################################################## \n \n')     

# Statistical analysis
# Healthy vs HF
# HF vs HF free, HF PP1 fix, HF PP2A fix
# HF free vs HF PP1 fix, HF PP2A fix

print('Mann-Whitney healthy vs HF\n \n') 
pvals_healthy_vs_HF = []

for i in range(8):
    pvals_healthy_vs_HF.append(stats.mannwhitneyu(data_healthy[i,:,0],data_HF_clean[i,:,0], alternative='two-sided')[1])

pvals_healthy_vs_HF_corrected = fdrcorrection(pvals_healthy_vs_HF)[1] 

for i in range(8):
    print(state[i], ' Mann-Whitney healthy vs HF, p= ', pvals_healthy_vs_HF_corrected[i],'\n\n')  

print('######################################################## \n \n')  

print('Mann-Whitney HF vs HF free PPases,\n \n') 
pvals_HF_vs_PP_free = []

for i in range(8):
    pvals_HF_vs_PP_free.append(stats.mannwhitneyu(data_HF_clean[i,:,0],data_HF_PPfree[i,:,0], alternative='two-sided')[1])

pvals_HF_vs_PP_free_corrected = fdrcorrection(pvals_HF_vs_PP_free)[1]

for i in range(8):
    print(state[i], ' Mann-Whitney HF vs HF free PPases, p= ', pvals_HF_vs_PP_free_corrected[i],'\n')  

print('######################################################## \n \n')  

print('Mann-Whitney HF vs HF PP2A fix,\n \n') 
pvals_HF_vs_PP2A_fix = []

for i in range(8):
    pvals_HF_vs_PP2A_fix.append(stats.mannwhitneyu(data_HF_clean[i,:,0],data_HF_fixPP2A[i,:,0], alternative='two-sided')[1])

pvals_HF_vs_PP2A_fix_corrected = fdrcorrection(pvals_HF_vs_PP2A_fix)[1]

for i in range(8):
    print(state[i], ' Mann-Whitney HF vs HF PP2A fix, p= ', pvals_HF_vs_PP2A_fix_corrected[i],'\n')  



print('######################################################## \n \n')  

print('Mann-Whitney HF vs HF PP1 fix,\n \n') 
pvals_HF_vs_PP1_fix = []

for i in range(8):
    pvals_HF_vs_PP1_fix.append(stats.mannwhitneyu(data_HF_clean[i,:,0],data_HF_fixPP1[i,:,0], alternative='two-sided')[1])

pvals_HF_vs_PP1_fix_corrected = fdrcorrection(pvals_HF_vs_PP1_fix)[1]

for i in range(8):
    print(state[i], ' Mann-Whitney HF vs HF PP1 fix, p= ', pvals_HF_vs_PP1_fix_corrected[i],'\n')  
 

#%% Polar coordinate plots of enzyme vectors after optimization (Figures S23-S27)

def plt_logpolar(ax, theta, r_, bullseye=0.3, **kwargs):
    #Modified code from: 
    #https://stackoverflow.com/questions/14919407/how-to-use-log-scale-on-polar-axis-in-matplotlib,
    #by User Trenton McKinney, accessed 27/07/2022
    # min10 = max(np.log10(np.min(r_)),-12)
       
    
    r_[r_ == 0] = 1e-12 #replace possible 0 zero values with 1e-12

    # min10 = np.log10(np.min(r_))
    # max10 = np.log10(np.max(r_))
    
    min10 = -12
    max10 = -5
    
    r = np.log10(r_) - min10 + bullseye
    rCirc = np.hstack((r,r[0]))
    thetaCirc = np.hstack((theta,theta[0]))
    ax.plot(thetaCirc, rCirc,'o-',ms=3, **kwargs)
    l = np.arange(np.floor(min10), -5)
    
    ax.set_rticks(l - min10 + bullseye) 
    ax.set_yticklabels(["1e%d" % x for x in l])
    
    ax.set_rlim(0, max10 - min10 + bullseye)
    # ax.set_rlim(0, 7.5)

    ax.set_xticks(theta)
    
ttlsDat = ['healthy', 'HF', 'HF, 0,75x max PKC,RSK2', 'HF, 0,75x max PKC,RSK2, PP1toPPtot = 1$','HF, 0,75x max PKC,RSK2, PP2AtoPPtot = 1$']

datasets = [data_healthy,data_HF_clean,data_HF_PPfree,data_HF_fixPP1,data_HF_fixPP2A]
   

for d in range(len(datasets)):

    plt.figure(figsize=(15,12))
    
    for i in range(8):
            
        thetaCoordinates = np.asarray([0,2*np.pi/5,2*2*np.pi/5,3*2*np.pi/5,4*2*np.pi/5])+0.315
        ax = plt.gcf().add_subplot(3,4,i+1,projection= 'polar')
    
        for ii in range(3):
            plt_logpolar(ax, thetaCoordinates, datasets[d][i,ii,1:],color=colorV[d],alpha=0.5,lw=4.5)
             
        ax.set_xticklabels(['PKA','RSK2','PKC','PP1','PP2A'],fontsize=14)
        ax.set_rlabel_position(60) 
        plt.title('max('+ttls[i]+')= '+"{:.2f}".format(np.average(data_healthy[i,:,0])),loc='left',fontsize=18)
    
    plt.tight_layout()
    # plt.suptitle(ttlsDat[d])
    if saveFigs == True:
        plt.savefig(os.path.join(path_figures,ttlsDat[d]+'_enzymeVectors.png'),dpi=300, bbox_inches = "tight")
  