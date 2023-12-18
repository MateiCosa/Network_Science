import numpy as np
import pandas as pd
import networkx as nx
from copy import deepcopy
import Prevalence
import Seizures

def get_drug_users(drug, countries_list, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    drug : str
    countries_list : list(str)
    start_year : int, optional
        The default is 2006.
    end_year : int, optional
        The default is 2017.
    Returns
    -------
    drug_users : dict(dict(floate))
        Returns the number of drug users for each country for each year.
    '''
    
    # Read the population data
    xlsx = pd.ExcelFile('/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Population.xlsx')
    df_pop = dict()
    for year in range(start_year, end_year + 1):
        df_pop[year] = pd.read_excel(xlsx, str(year))
    
    # Read the prevalence data
    xlsx = pd.ExcelFile('/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Prevalence.xlsx')
    df_prev = dict()
    for year in range(start_year, end_year + 1):
        df_prev[year] = pd.read_excel(xlsx, str(year))
    
    # Container for total drug users per country
    drug_users = {year: {} for year in range(start_year, end_year + 1)}
    
    # Iterate over the time period
    for year in range(start_year, end_year + 1):
        # Iterate over the list of countries
        for country in countries_list:
            country_year_population = float(df_pop[year][df_pop[year]['Location'] == country]['Population'])
            country_year_drug_prevalence = float(df_prev[year][(df_prev[year]['Location'] == country) & (df_prev[year]['Drug'] == drug)]['Prevalence'])
            country_drug_users = country_year_population * country_year_drug_prevalence
            drug_users[year][country] = country_drug_users
    
    return drug_users

def get_yearly_consumption(drug, drug_users_dict, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    drug : str
    drug_users_dict : dict(dict(float))
    start_year : int, optional
        The default is 2006.
    end_year : int, optional
        The default is 2017.
    Returns
    -------
    consumption_dict : dict(float)
        Returns the yearly consumption of the drug in every year.
    '''
    # Import the production data
    prod_df = pd.read_excel('/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Production.xlsx')

    # Container for yearly consumption per user
    consumption_dict = dict()

    # Iterate over the time period
    for year in range(start_year, end_year + 1):
        # Total consumers
        yearly_consumers = sum(drug_users_dict[year].values())
        # Total production
        yearly_production = float(prod_df[(prod_df['Drug'] == drug) & (prod_df['Year'] == year)]['Quantity(kg)'])
        # Per user yearly consumption
        consumption_dict[year] = yearly_production / yearly_consumers
    
    # Return the output
    return consumption_dict

def get_national_markets_df(countries_list, sub_region_dict, region_dict, df_ids, drug_list = ['Cocaine', 'Heroin', 'Cannabis', 'Amphetamine', 'Ecstasy'], from_file = False, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    countries_list : list(str)
    drug_list : list(str), optional
        The default is ['Cocaine', 'Heroin', 'Cannabis', 'Amphetamine', 'Ecstasy'].
    start_year : int, optional
        The default is 2006.
    end_year : int, optional
        The default is 2017.
    Returns
    -------
    df_markets : dict(pd.DataFrame)
        Aggregates together seziures and market estimates.
    '''
    
    if from_file:
        # Read the seziures data for the given time period
        xlsx = pd.ExcelFile('/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Seizures.xlsx')
        df_seiz = dict()
        for year in range(start_year, end_year + 1):
            df_seiz[year] = pd.read_excel(xlsx, str(year))
    
    else:
        # Get the seziures from scratch
        df_seiz = Seizures.get_purity_adjusted_seizures(df_ids, 
                                                        countries_list = countries_list, 
                                                        sub_region_dict = sub_region_dict,
                                                        region_dict = region_dict, 
                                                        drug_list = drug_list)
        
    # Read the prevalence data for the given time period
    xlsx = pd.ExcelFile('/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Prevalence.xlsx')
    df_prev = dict()
    for year in range(start_year, end_year + 1):
        df_prev[year] = pd.read_excel(xlsx, str(year))
    
    # Read the population data for the given time period
    xlsx = pd.ExcelFile('/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Population.xlsx')
    df_pop = dict()
    for year in range(start_year, end_year + 1):
        df_pop[year] = pd.read_excel(xlsx, str(year))
    
    # Create a dict of pd.DataFrames to store the final result
    # We first copy the seizures data
    df_markets = deepcopy(df_seiz)
    for year in range(start_year, end_year + 1): 
        # We rename the 'Quantity(kg)': 'Seizures(kg)'
        df_markets[year].rename(columns = {'Quantity(kg)': 'Seizures(kg)'}, inplace = True)
        # Then we add two new columns: 'Consumption(kg)', 'Market(kg)'
        df_markets[year]['Consumption(kg)'] = ''
        df_markets[year]['Market(kg)'] = ''
    
    # Iterate over the drug list
    for drug in drug_list:
        # Obtain the yearly number of drug users
        drug_users = get_drug_users(drug, countries_list, start_year = start_year, end_year = end_year)
        # Obtain the yearly consumption for each drug
        yearly_consumption = get_yearly_consumption(drug, drug_users)
        
        # Iterate over the time period
        for year in range(start_year, end_year + 1):
            # Get the average yearly consumption
            average_quantity = yearly_consumption[year]
            # Extract the seizures data for the corresponding drug
            drug_seizures_year_df = df_markets[year][df_markets[year]['Drug'] == drug]

            # Iterate over the rows
            for ind in drug_seizures_year_df.index:
                # Get the country
                country = drug_seizures_year_df['Country'][ind]
                # Get the seizures
                seizures = float(drug_seizures_year_df['Seizures(kg)'][ind])
                # Get the population
                population = float(df_pop[year][df_pop[year]['Location'] == country]['Population'])
                # Get the prevalence
                prevalence = float(df_prev[year][(df_prev[year]['Location'] == country) & (df_prev[year]['Drug'] == drug)]['Prevalence'])
                
                # Compute internal consumption
                consumption = population * prevalence * average_quantity
                # Compute internal market
                market = consumption + seizures
                
                # Add the consumption and the market data to df_markets
                df_markets[year].loc[(df_markets[year]['Drug'] == drug) & (df_markets[year]['Country'] == country), 'Consumption(kg)'] = consumption
                df_markets[year].loc[(df_markets[year]['Drug'] == drug) & (df_markets[year]['Country'] == country), 'Market(kg)'] = market
    
    # Remove the first column in each dataframe:
    for year in range(start_year, end_year + 1):
        df_markets[year] = df_markets[year][df_markets[year].columns[1:]]
    
    # Return the output
    return df_markets

def write_to_xlsx(output, target_file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Markets.xlsx'):
    '''
    Parameters
    ----------
    output : dict of pd.DataFrame obejcts
    target_file : str
        The default is 'markets.xlsx'.
    Returns
    -------
    None; Writes the ouput to the file, creating an .xlsx document with one spreadsheet corresponding to each year.
    '''
    
    with pd.ExcelWriter(target_file) as writer:  
        for year in output.keys():
            output[year].to_excel(writer, sheet_name = str(year))


    
            
            
            
            
            
            
            
            