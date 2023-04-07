**************************************************************************************
*********************************	README	     *********************************
**************************************************************************************

This code reproduces the simulation results and analyses from the publication:

Thomas Kampourakis, Saraswathi Ponnam, Daniel Koch (2023):
The cardiac myosin binding protein-C phosphorylation state as a function
of multiple protein kinase and phosphatase activities. BioRxiv:
https://doi.org/10.1101/2023.02.24.529959 

To successfully reproduce the results you will need:
- COPASI (http://copasi.org/)
- PythonL
	- JupyterLab (or a similar environment for running *.ipynb notebooks)
	- An environment for running *.py scripts

We recommend using Anaconda, which will enable you to recreate the exact environments
with all the python packages and versions used in this study by importing the respective
*.yaml files.

Below is a short description of the directories and files:

>MAIN FOLDER:

	simulations.py
	Predictive simulations shown in Figure 3 and several supplementary figures.

	models_cMyBPC.py 
	Contains the ODE systems used by simulations.py

	functions_cMyBPC.py
	Contains various functions including for numerical integration of ODE systems 
	and other functions for data analysis.

	model_comparisons_cMyBPC.py
	Reproduces comparison results between model simulations/fits and experimental data
	shown in Figures 2C and E, S2-S7, S9-S10 and S13-S15

	plot_experimental_data.py
	This file reproduces 1B and 3B based on the data in the subfolder "experimental data".

	FillBetween3d.py: 
	Auxilliary function for line plots with shaded error bars.


SUBFOLDERS:

	>ENVIRONMENTS
	Contains the Anaconda environments with all python packages and their specific versions used. 
	JupyterLab was used for interfacing Python and Copasi via the basico package and used for all 
	parameter estimation and optimization tasks. Spyder contains the packages used for all other
	simulations and analyses performed with python in the Spyder IDE.
	
	>EXPERIMENTAL DATA
	This folder contains the experimental data used for fitting but formatted for plotting by
	the file 'plot_experimental_data.py'

	>HUMAN HEART DATA AND OPTIMIZATION
	Contains all files used for fitting the cMyBPC model to the data from Copeland et al. 2010 
	and the optimization results shown in Figure 4 and Figures S22-S27. 
	Run the *.ipynb notebooks to execute the parameter estimation task and optimization tasks.

	>PARAMETER ESTIMATION
	Contains the copasi implementation of all model versions used for fitting 
	the kinetic data on PKA, PP1 and PP2A. Data formatted for compatibility with copasi are 
	in the subfolder "DataFormatted". The notebook 'parameterEstimation.ipynb' runs the parameter
	estimation task.

	>PARAMETERSETS
	Contains all parametersets resulting from the parameter estimation and refinement procedure.
	The numpy file "paramset_final.npy" is contains the final parameter sets used for all predictive
	simulations with the final model. The excel sheet "Parameterset_finalModel.xlsx" is a human
	readable format with same parameter sets ordered according to their objective function value.


For further questions, please contact Daniel Koch (dkoch.research@protonmail.com).