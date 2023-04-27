# -*- coding: utf-8 -*-
"""

This file contains the model codes used for the simulations and analyses in the publication:
    
    Thomas Kampourakis, Saraswathi Ponnam, Daniel Koch (2023):
    The cardiac myosin binding protein-C phosphorylation state 
    as a function of multiple protein kinase and phosphatase activities 
    Preprint available under: https://doi.org/10.1101/2023.02.24.529959 
    
    model1 to model4 were used for model calibration and for comparing the fitted models
    to the experimental data. model4_full is the same as model4 except that it also accounts
    for structural transitions after alpha-dephosphorylation by PP2A.
    
    model4_final and model4_final_RSK2 were used for predictive simulations.
    They allow for time-varying PKA activity and also account for the possibility that 
    the transiently structured form alpha might be a substrate for PKA or PKC.
    model4_final_RSK2 further includes phosphorylation of 0P or delta cMyBPC by
    ribosomal S6 kinase 2 (RSK2).

@author: Daniel Koch
"""
import numpy as np

#%% Models used for fitting and comparison to experimental data

def cMyBPC_model1(t,ICs,params): 
    
    # Michaelis-Menten type rate laws only
    
    # assignment of initial conditions for state variables   
    P0,A,AB,ABG,D,AD,ABD,ABGD = ICs
      
    # parameters
    k = params[0]
    K = params[1]
    PKA, PKC, PP1, PP2A = params[2]
    
    # competition terms Kappa
    K_pka = P0/K[0]+A/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+A/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]

    # reaction rates

    #PKA
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #PP1
    v2 = k[1]*PP1*A/(K[1]*(1+K_pp1-A/K[1])+A)
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
     
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
 
    # ODEs
    dP0dt = v2 + v3 + v11  + v12  - v1 - v10 
    dAdt = v1 + v5 + v6 + v14  + v15  - v2 - v3 - v4 - v13 
    dABdt = v4 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 
    dADdt = v13  + v22  + v26  + v27  - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 

    # print('dABDG new: ', dABGDdt, ' v29 ', v29, 'K29: ', K[29], 'Kappa_PP1 ', K_pp1)


    return np.array([dP0dt, dAdt, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])

def cMyBPC_model2(t,ICs,params): 
    
    # Phenomenological model featuring activation of r2
    
    # assignment of initial conditions for state variables   
    P0,A,AB,ABG,D,AD,ABD,ABGD = ICs
      
    # parameters
    k = params[0]
    K = params[1]
    r2_actF, r2_Ka = params[2]
    PKA, PKC, PP1, PP2A = params[3]
    
    # competition terms Kappa
    K_pka = P0/K[0]+A/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+A/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]

    # reaction rates

    #PKA
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #PP1
    v2 = k[1]*PP1*A/(K[1]*(1+K_pp1-A/K[1])+A)
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
    
    #activation of r2
    frac_2P_3P = (AB+ABG+AD+ABD)/(P0+A+AB+ABG+D+AD+ABD+ABGD)
    activationFactor = 1 + r2_actF*frac_2P_3P/(r2_Ka + frac_2P_3P)
    v2 = v2*activationFactor
    
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
 
    # ODEs
    dP0dt = v2 + v3 + v11  + v12  - v1  - v10 
    dAdt = v1  + v5 + v6 + v14  + v15  - v2 - v3 - v4 - v13 
    dABdt = v4 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 
    dADdt = v13  + v22  + v26  + v27  - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 

    return np.array([dP0dt, dAdt, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])

def cMyBPC_model3(t,ICs,params): 
    
    # Model featuring allosteric activation of r2

    # assignment of initial conditions for state variables   
    P0,A,AB,ABG,D,AD,ABD,ABGD = ICs
      
    # parameters
    k = params[0]
    K = params[1]
    lambda_r2, kcat_A, Ka = params[2]
    PKA, PKC, PP1, PP2A = params[3]
    
    # competition terms Kappa
    K_pka = P0/K[0]+A/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+A/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]

    # reaction rates

    #PKA and RSK2
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #PP1
    v2 = (k[1]*PP1*A+kcat_A*PP1*A*(AD+AB)/(lambda_r2*Ka))/((K[1] + (AD+AB)*K[1]/Ka + A*(AD+AB)/(lambda_r2*Ka)+K[1]*(K_pp1-(A/K[1]))+A))
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
     
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
 
    # ODEs
    dP0dt = v2 + v3 + v11  + v12  - v1 - v10 
    dAdt = v1 + v5 + v6 + v14  + v15  - v2 - v3 - v4 - v13 
    dABdt = v4 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 
    dADdt = v13  + v22  + v26  + v27  - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 

    return np.array([dP0dt, dAdt, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])

def cMyBPC_model4(t,ICs,params): 
    
    # Structural transition model for alpha species during PP1 dephosphorylation
    
    # assignment of initial conditions for state variables   
    P0,A,Atr,AB,ABG,D,AD,ABD,ABGD = ICs
      
    # parameters
    k = params[0]
    K = params[1]
    k2_fast, K2_fast, k_isoF, k_isoR = params[2]
    PKA, PKC, PP1, PP2A = params[3]
       
    # competition terms Kappa
    K_pka = P0/K[0]+A/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+A/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]+Atr/K2_fast
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]

    # reaction rates

    #PKA
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #PP1
    v2 = k[1]*PP1*A/(K[1]*(1+K_pp1-A/K[1])+A)
    v2_fast = k2_fast*PP1*Atr/(K2_fast*(1+K_pp1-Atr/K2_fast)+Atr)
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
     
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
    
    #isomerization
    v_isoF = k_isoF*Atr
    v_isoR = k_isoR*A
 
    # ODEs
    dP0dt = v2 + v2_fast + v3 + v11  + v12  - v1 - v10 
    dAdt = v1 + v6 + v15  - v2 - v3 - v4 - v13  + v_isoF - v_isoR
    dAtr = v5 + v14  - v_isoF + v_isoR - v2_fast
    dABdt = v4 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 
    dADdt = v13  + v22  + v26  + v27  - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 
    
    return np.array([dP0dt, dAdt, dAtr, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])

def cMyBPC_model4_full(t,ICs,params): 
    
    # Structural transition model for alpha species during PP1 and PP2A dephosphorylation
    
    # assignment of initial conditions for state variables   
    P0,A,Atr,AB,ABG,D,AD,ABD,ABGD = ICs
      
    # parameters
    k = params[0]
    K = params[1]
    k2_fast, K2_fast, k_isoF, k_isoR, k3_fast, K3_fast = params[2]
   
    PKA, PKC, PP1, PP2A = params[3]
       
    # competition terms Kappa
    K_pka = P0/K[0]+A/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+A/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]+Atr/K2_fast
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]+Atr/K3_fast

    # reaction rates

    #PKA
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #PP1
    v2 = k[1]*PP1*A/(K[1]*(1+K_pp1-A/K[1])+A)
    v2_fast = k2_fast*PP1*Atr/(K2_fast*(1+K_pp1-Atr/K2_fast)+Atr)
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
     
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v3_fast = k3_fast*PP2A*Atr/(K3_fast*(1+K_pp2a-Atr/K3_fast)+Atr)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
    
    #isomerization
    v_isoF = k_isoF*Atr
    v_isoR = k_isoR*A
     
    # ODEs
    dP0dt = v2 + v2_fast + v3 + v3_fast + v11  + v12  - v1 - v10 
    dAdt = v1 - v2 - v3 - v4 - v13  + v_isoF - v_isoR
    dAtr = v5 + v6 + v14  + v15  - v_isoF + v_isoR - v2_fast - v3_fast
    dABdt = v4 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 
    dADdt = v13  + v22  + v26  + v27  - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 

    return np.array([dP0dt, dAdt, dAtr, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])

#%% Final models used for simulation 

def cMyBPC_model_final(t,ICs,params,naFun,naFunParams): 
    
    # Structural transition model for alpha species during PP1 and PP2A dephosphorylation. 
    # Also includes phosphorylation of transiently structured alpha species by PKC.
    
    # assignment of initial conditions for state variables   
    P0,A,Atr,AB,ABG,D,AD,ABD,ABGD = ICs
      
    # parameters
    k = params[0]
    K = params[1]
    k2_fast, K2_fast, k_isoF, k_isoR, k3_fast, K3_fast = params[2]
   
    PKA, PKC, PP1, PP2A = params[3]
       
    # competition terms Kappa
    K_pka = P0/K[0]+A/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+A/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]+Atr/K2_fast
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]+Atr/K3_fast

    # reaction rates

    #PKA
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #PP1
    v2 = k[1]*PP1*A/(K[1]*(1+K_pp1-A/K[1])+A)
    v2_fast = k2_fast*PP1*Atr/(K2_fast*(1+K_pp1-Atr/K2_fast)+Atr)
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
     
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v3_fast = k3_fast*PP2A*Atr/(K3_fast*(1+K_pp2a-Atr/K3_fast)+Atr)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
    
    #isomerization
    v_isoF = k_isoF*Atr
    v_isoR = k_isoR*A
     
    # ODEs
    dP0dt = v2 + v2_fast + v3 + v3_fast + v11  + v12  - v1 - v10 
    dAdt = v1 - v2 - v3 - v4 - v13  + v_isoF - v_isoR
    dAtr = v5 + v6 + v14  + v15  - v_isoF + v_isoR - v2_fast - v3_fast
    dABdt = v4 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 
    dADdt = v13  + v22  + v26  + v27  - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 

    return np.array([dP0dt, dAdt, dAtr, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])

    
    # assignment of initial conditions for state variables   
    P0,A,Atr,AB,ABG,D,AD,ABD,ABGD = ICs
      
    # parameters
    k = params[0]
    K = params[1]
    k2_fast, K2_fast, k_isoF, k_isoR, k3_fast, K3_fast = params[2]

    PKA, PKC, PP1, PP2A = params[3]

    # non-autonomous variables
    PKA = PKA*naFun(t,naFunParams)     
       
    # competition terms Kappa
    K_pka = P0/K[0]+(A+Atr)/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+(A+Atr)/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]+Atr/K2_fast
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]+Atr/K3_fast

    # reaction rates

    #PKA
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v4_2 = k[3]*PKA*Atr/(K[3]*(1+K_pka-Atr/K[3])+Atr)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v13_2  = k[12]*PKC*Atr/(K[12]*(1+K_pkc-Atr/K[12])+Atr)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #PP1
    v2 = k[1]*PP1*A/(K[1]*(1+K_pp1-A/K[1])+A)
    v2_fast = k2_fast*PP1*Atr/(K2_fast*(1+K_pp1-Atr/K2_fast)+Atr)
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
     
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v3_fast = k3_fast*PP2A*Atr/(K3_fast*(1+K_pp2a-Atr/K3_fast)+Atr)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
    
    #isomerization
    v_isoF = k_isoF*Atr
    v_isoR = k_isoR*A
     
    # ODEs
    dP0dt = v2 + v2_fast + v3 + v3_fast + v11  + v12  - v1 - v10 
    dAdt = v1 - v2 - v3 - v4 - v13  + v_isoF - v_isoR
    dAtr = v5 + v6 + v14  + v15  - v_isoF + v_isoR - v2_fast - v3_fast - v4_2 - v13_2
    dABdt = v4 + v4_2 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 
    dADdt = v13 + v13_2 + v22  + v26  + v27  - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 

    return np.array([dP0dt, dAdt, dAtr, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])

def cMyBPC_model_final_RSK2(t,ICs,params,naFun,naFunParams):
    
    # Extended version of cMyBPC_model_final which also includes RSK2 reactions. 
    
    # assignment of initial conditions for state variables   
    P0,A,Atr,AB,ABG,D,AD,ABD,ABGD = ICs
         
    # parameters
    k = params[0]
    K = params[1]
    k = np.append(k, params[4][0]) #kcat RSK2 reaction 31
    k = np.append(k, params[4][1]) #kcat RSK2 reaction 32
    K = np.append(K, params[4][2]) # Km RSK2 reaction 31
    K = np.append(K, params[4][3]) # Km RSK2 reaction 32
    
    k2_fast, K2_fast, k_isoF, k_isoR, k3_fast, K3_fast = params[2]

    PKA, PKC, PP1, PP2A, RSK2 = params[3]
    
    # non-autonomous variables
    PKA = PKA*naFun(t,naFunParams)
    
    # competition terms Kappa
    K_pka = P0/K[0]+(A+Atr)/K[3]+AB/K[6]+D/K[21]+AD/K[24]+ABD/K[27]
    K_pkc = P0/K[9]+(A+Atr)/K[12]+AB/K[15]+ABG/K[18]
    K_pp1 = A/K[1]+AB/K[4]+ABG/K[7]+D/K[10]+AD/K[13]+AD/K[22]+ABD/K[16]+ABD/K[25]+ABGD/K[19]+ABGD/K[28]+Atr/K2_fast
    K_pp2a = A/K[2]+AB/K[5]+ABG/K[8]+D/K[11]+AD/K[14]+AD/K[23]+ABD/K[17]+ABD/K[26]+ABGD/K[20]+ABGD/K[29]+Atr/K3_fast

    # reaction rates
    
    #PKA
    v1 = k[0]*PKA*P0/(K[0]*(1+K_pka-P0/K[0])+P0)
    v4 = k[3]*PKA*A/(K[3]*(1+K_pka-A/K[3])+A)
    v4_2 = k[3]*PKA*Atr/(K[3]*(1+K_pka-Atr/K[3])+Atr)
    v7 = k[6]*PKA*AB/(K[6]*(1+K_pka-AB/K[6])+AB)
    v22  = k[21]*PKA*D/(K[21]*(1+K_pka-D/K[21])+D)
    v25  = k[24]*PKA*AD/(K[24]*(1+K_pka-AD/K[24])+AD)
    v28  = k[27]*PKA*ABD/(K[27]*(1+K_pka-ABD/K[27])+ABD)
     
    #PKC
    v10  = k[9]*PKC*P0/(K[9]*(1+K_pkc-P0/K[9])+P0)
    v13  = k[12]*PKC*A/(K[12]*(1+K_pkc-A/K[12])+A)
    v13_2  = k[12]*PKC*Atr/(K[12]*(1+K_pkc-Atr/K[12])+Atr)
    v16  = k[15]*PKC*AB/(K[15]*(1+K_pkc-AB/K[15])+AB)
    v19  = k[18]*PKC*ABG/(K[18]*(1+K_pkc-ABG/K[18])+ABG)
     
    #RSK2
    v31  = k[30]*RSK2*P0/(K[30]+D/K[31]+P0)
    v32  = k[31]*RSK2*D/(K[31]+P0/K[30]+D)
    
    #PP1
    v2 = k[1]*PP1*A/(K[1]*(1+K_pp1-A/K[1])+A)
    v2_fast = k2_fast*PP1*Atr/(K2_fast*(1+K_pp1-Atr/K2_fast)+Atr)
    v5 = k[4]*PP1*AB/(K[4]*(1+K_pp1-AB/K[4])+AB)
    v8 = k[7]*PP1*ABG/(K[7]*(1+K_pp1-ABG/K[7])+ABG)
    v11  = k[10]*PP1*D/(K[10]*(1+K_pp1-D/K[10])+D)
    v14  = k[13]*PP1*AD/(K[13]*(1+K_pp1-AD/K[13])+AD)
    v17  = k[16]*PP1*ABD/(K[16]*(1+K_pp1-ABD/K[16])+ABD)
    v20  = k[19]*PP1*ABGD/(K[19]*(1+K_pp1-ABGD/K[19])+ABGD)
    v23  = k[22]*PP1*AD/(K[22]*(1+K_pp1-AD/K[22])+AD)
    v26  = k[25]*PP1*ABD/(K[25]*(1+K_pp1-ABD/K[25])+ABD)
    v29  = k[28]*PP1*ABGD/(K[28]*(1+K_pp1-ABGD/K[28])+ABGD)
     
    #PP2A
    v3 = k[2]*PP2A*A/(K[2]*(1+K_pp2a-A/K[2])+A)
    v3_fast = k3_fast*PP2A*Atr/(K3_fast*(1+K_pp2a-Atr/K3_fast)+Atr)
    v6 = k[5]*PP2A*AB/(K[5]*(1+K_pp2a-AB/K[5])+AB)
    v9 = k[8]*PP2A*ABG/(K[8]*(1+K_pp2a-ABG/K[8])+ABG)
    v12  = k[11]*PP2A*D/(K[11]*(1+K_pp2a-D/K[11])+D)
    v15  = k[14]*PP2A*AD/(K[14]*(1+K_pp2a-AD/K[14])+AD)
    v18  = k[17]*PP2A*ABD/(K[17]*(1+K_pp2a-ABD/K[17])+ABD)
    v21  = k[20]*PP2A*ABGD/(K[20]*(1+K_pp2a-ABGD/K[20])+ABGD)
    v24  = k[23]*PP2A*AD/(K[23]*(1+K_pp2a-AD/K[23])+AD)
    v27  = k[26]*PP2A*ABD/(K[26]*(1+K_pp2a-ABD/K[26])+ABD)
    v30  = k[29]*PP2A*ABGD/(K[29]*(1+K_pp2a-ABGD/K[29])+ABGD)
    
    #isomerization
    v_isoF = k_isoF*Atr
    v_isoR = k_isoR*A
     
    # ODEs
    dP0dt = v2 + v2_fast + v3 + v3_fast + v11  + v12  - v1 - v10 - v31
    dAdt = v1 + v31 - v2 - v3 - v4 - v13  + v_isoF - v_isoR
    dAtr = v5 + v6 + v14  + v15  - v_isoF + v_isoR - v2_fast - v3_fast - v4_2 - v13_2
    dABdt = v4 + v4_2 + v8 + v9 + v17  + v18  - v5 - v6 - v7 - v16 
    dABGdt = v7 + v20  + v21  - v8 - v9 - v19 
    dDdt = v10  + v23  + v24  - v11  - v12  - v22 - v32
    dADdt = v13 + v13_2  + v22  + v26  + v27 + v32 - v14  - v15  - v23  - v24  - v25 
    dABDdt = v16  + v25  + v29  + v30  - v17  - v18  - v26  - v27  - v28 
    dABGDdt = v19  + v28  - v20  - v21  - v29  - v30 

    return np.array([dP0dt, dAdt, dAtr, dABdt, dABGdt, dDdt, dADdt, dABDdt, dABGDdt])
    