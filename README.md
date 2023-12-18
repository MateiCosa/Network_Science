# Network Science Meets Graph Neural Networks:
# An Empirical Analysis of the International Drug Trafficking Networks

## Author: Matei Gabriel Cosa
## Supervisors: prof. Daniele Durante, prof. Omiros Papaspiliopoulos

## Introduction
Networks are fascinating ways of representing and analysing data. These complex structures allow one to model the relations between different entities in a way that goes beyond the traidtional *i.i.d.* assumption made in statistical learning. These interdependencies between the memebers of the network (nodes) create amazing opportunities for capturing the underlying phenonmenons described by the network 

International drug trafficking is one of the primary forms of illicit trade accounting for billions of dollars every year. Even more sinister is the impact that these illegal substances have on the lives of many and, consequently, on health care systems around the world. Furthermore, they are a major source of financing for organzied crime and, implcitly, for the violence and corruption carried out by these organizations. 

With major international bodies such as the UN through UNODC and the EU, as well as national governments and agencies trying to combat this problem, one may wonder if the computational tools available to us today could play a role. This is what this project is about: constructing and analysing a global drug trafficking network in order to derive meaningful insights. 

To achieve this, we turn to the use of network science, a branch of statistics and graph theory that attempts to model network data. Following this line of thought, we apply exponential random graph models (ERGMs) to conduct inference on the parameters behind the formation of the network. 

We further attempt to construct a predictive model using graph neural networks (GNNs), which are powerful and flexible tools that can be used for link prediction, node and graph classification, recommendation systems, etc. In our case, we seek to apply GNNs for link prediction in an unsupervised way.

## Data

We construct our own datasets by gathering, cleaning, processing, and aggregating data from several sources. We focus on the trafficking of cocaine and heroin over the period between 2006 and 2017. This timeframe is dictated by data availability. In particular, the fundamental information about the edges of our network is derived from the International Drug Seizures (IDS) dataset. 

Following a series of steps from the criminology literature (Giommoni, L., Berlusconi, G. & Aziani, A. Interdicting International Drug Trafficking: a Network Approach for Coordinated and Targeted Interventions, 2022), we construct a series of networks based on yearly seizures. 

Additionally, we augment our datasets with country-level features relating to socio-economic indicators, drug-related data, and geographical location. In the end, we construct both yearly and aggregate networks which can used for both statistical models and deep learning on graphs.

For a detailed overview, please check out *data_prep* for all the code relating to data preparation and the main notebook that summarizes the most important steps of the process.

## Methods

Coming soon...