
# Collection of functions for obtaining purity-adjusted drug seizures from the IDS dataset (UNODC);
# The default period is 2006-2017;
# The drugs of interest are: cocaine, opioids, cannabis, amphetamines, and ecstasy;
# Source of data: https://www.unodc.org/unodc/en/data-and-analysis/statistics/drugs/seizures_cases.html

import numpy as np
import pandas as pd
import networkx as nx
from Quantity_Conversion import convert

def read_xlsx(file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/IDS_Report.xlsx', start_year = 2006, end_year = 2017): 
    '''
    Parameters
    ----------
    file : str, optional
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    df : dict of pd.DataFrames
    '''
    
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    xlsx = pd.ExcelFile(file)
    df = dict()
    for year in range(start_year, end_year + 1):
        df[year] = pd.read_excel(xlsx, str(year))
    return df

def create_output_df(start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    seiz_df : dict of pd.DataFrames
        Creates an empty dictionary of pd.DataFrames to store the final output.
    '''
    
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    seiz_df = dict()
    for i in range(start_year, end_year + 1):
        seiz_df[i] = pd.DataFrame(columns=['Region', 'SubRegion', 'Country', 'Drug', 'Quantity(kg)'])
    return seiz_df

def get_ids_locations(df_ids, drug_list = ['Cocaine', 'Heroin', 'Cannabis', 'Amphetamine', 'Ecstasy'], start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_ids : dict of pd.DataFrame
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    countries_list : list of str
    sub_region_dict : dict
    region_dict : dict
        Obtains the countries, regions and sub-regions present among the countries of seizure across the period of time.
    '''
    
    # Dict for missing sub-regions
    missing_sub_region_map = {
    'Albania': 'East Europe',
    'Antigua and Barbuda': 'Caribbean',
    'Aruba': 'Caribbean',
    'Australia': 'Oceania',
    'Bahrain': 'Near and Middle East /South-West Asia',
    'Barbados': 'Caribbean',
    'Bermuda': 'Caribbean',
    'Burundi': 'East Africa',
    'Cameroon': 'West and Central Africa',
    'Congo, the Democratic Republic of the': 'West and Central Africa',
    'Cook Islands': 'Oceania',
    'Costa Rica': 'Central America',
    'Curaçao': 'Caribbean',
    'Dominica': 'Caribbean',
    'Equatorial Guinea': 'West and Central Africa',
    'Eritrea': 'East Africa',
    'Estonia': 'East Europe',
    'Faroe Islands': 'West & Central Europe',
    'Fiji': 'Oceania',
    'Gabon': 'West and Central Africa',
    'Grenada': 'Caribbean',
    'Guadeloupe': 'Caribbean',
    'Guernsey': 'West & Central Europe',
    'Guyana': 'South America',
    'Haiti': 'Caribbean',
    'Hong Kong': 'South Asia',
    'Iraq':'Near and Middle East /South-West Asia',
    'Isle of Man': 'West & Central Europe',
    'Israel': 'Near and Middle East /South-West Asia',
    'Jamaica': 'Caribbean',
    'Jordan': 'Near and Middle East /South-West Asia',
    "Korea, Democratic People's Republic of": 'East and South-East Asia',
    'Kosovo under UNSCR 1244': 'East Europe',
    'Kuwait': 'Near and Middle East /South-West Asia',
    'Liberia': 'West and Central Africa',
    'Madagascar': 'East Africa',
    'Mongolia': 'East and South-East Asia',
    'Namibia': 'Southern Africa',
    'Netherlands Antilles': 'Caribbean',
    'Nicaragua': 'Central America',
    'Niger': 'West and Central Africa',
    'Oman': 'Near and Middle East /South-West Asia',
    'Panama': 'Central America',
    'Papua New Guinea': 'Oceania',
    'Puerto Rico': 'Caribbean',
    'Qatar': 'Near and Middle East /South-West Asia',
    'Rwanda': 'East Africa',
    'Réunion': 'South Asia',
    'Saint Pierre and Miquelon': 'North America',
    'Samoa': 'Oceania',
    'Sao Tome and Principe': 'West and Central Africa',
    'Seychelles': 'East Africa',
    'St. Lucia': 'Caribbean',
    'Suriname': 'South America',
    'Taiwan, Province of China': 'East and South-East Asia',
    'Turks and Caicos Islands': 'North America',
    'Viet Nam': 'East and South-East Asia',
    'Yemen': 'Near and Middle East /South-West Asia'
    }
    
    # Dict for missing regions
    missing_region_map = {
    'Albania': 'Europe',
    'Antigua and Barbuda': 'Americas',
    'Aruba': 'Americas',
    'Australia': 'Oceania',
    'Bahrain': 'Asia',
    'Barbados': 'Americas',
    'Bermuda': 'Americas',
    'Burundi': 'Africa',
    'Cameroon': 'Africa',
    'Congo, the Democratic Republic of the': 'Africa',
    'Cook Islands': 'Oceania',
    'Costa Rica': 'Americas',
    'Curaçao': 'Americas',
    'Dominica': 'Americas',
    'Equatorial Guinea': 'Africa',
    'Eritrea': 'Africa',
    'Estonia': 'Europe',
    'Faroe Islands': 'Europe',
    'Fiji': 'Oceania',
    'Gabon': 'Africa',
    'Grenada': 'Americas',
    'Guadeloupe': 'Americas',
    'Guernsey': 'Europe',
    'Guyana': 'Americas',
    'Haiti': 'Americas',
    'Hong Kong': 'Asia',
    'Iraq':'Asia',
    'Isle of Man': 'Europe',
    'Israel': 'Asia',
    'Jamaica': 'Americas',
    'Jordan': 'Asia',
    "Korea, Democratic People's Republic of": 'Asia',
    'Kosovo under UNSCR 1244': 'Europe',
    'Kuwait': 'Asia',
    'Liberia': 'Africa',
    'Madagascar': 'Africa',
    'Mongolia': 'Asia',
    'Namibia': 'Africa',
    'Netherlands Antilles': 'Americas',
    'Nicaragua': 'Americas',
    'Niger': 'Africa',
    'Oman': 'Asia',
    'Panama': 'Americas',
    'Papua New Guinea': 'Oceania',
    'Puerto Rico': 'Americas',
    'Qatar': 'Asia',
    'Rwanda': 'Africa',
    'Réunion': 'Asia',
    'Saint Pierre and Miquelon': 'Americas',
    'Samoa': 'Oceania',
    'Sao Tome and Principe': 'Africa',
    'Seychelles': 'Africa',
    'St. Lucia': 'Americas',
    'Suriname': 'Americas',
    'Taiwan, Province of China': 'Asia',
    'Turks and Caicos Islands': 'Americas',
    'Viet Nam': 'Asia',
    'Yemen': 'Asia'
    }
    
    # Initialize an empty set
    countries_set = set()
    
    # Iterate over the period of time
    for year in range(start_year, end_year + 1):
        
        # Iterte over the drug list
        for drug in drug_list:
            # Get the approriate filtering function
            drug_filter = get_drug_selector_function(drug)
            # Filter the dataset for the given drug
            df_year_drug = drug_filter(df_ids[year])
        
            # Add the countries corresponding to every year
            countries_set = countries_set.union(set(df_year_drug['COUNTRY_OF_SEIZURE'].unique()))
            countries_set = countries_set.union(set(df_year_drug['DEPARTURE_COUNTRY'].unique()))
            countries_set = countries_set.union(set(df_year_drug['DESTINATION_COUNTRY'].unique()))
            countries_set = countries_set.union(set(df_year_drug['PRODUCING_COUNTRY'].unique()))
    
    # Remove irrelevant values
    countries_set.remove(np.nan)
    countries_set.remove('Unknown')
    countries_set.remove('Other')
    
    # Convert the set to a list
    countries_list = sorted(list(countries_set))

    # Initialize empty dicts for sub-regions and regions
    sub_region_dict = dict()
    region_dict = dict()
    
    # Get the sub-regions and regions
    for country in countries_list:
        # Add 'Unknown' for all countries initially
        sub_region_dict[country] = 'Unknown'
        region_dict[country] = 'Unknown'
        # Look for the country's first appearence in the yearly seizures
        for year in range(start_year, end_year + 1):
            df_temp = df_ids[year][df_ids[year]['COUNTRY_OF_SEIZURE'] == country]
            # If found, exract the sub-region and region and break, no need to look any further
            if len(df_temp) > 0:
                sub_region_dict[country] = df_temp['SUBREGION_OF_SEIZURE'].unique()[0]
                region_dict[country] = df_temp['REGION_OF_SEIZURE'].unique()[0]
                break
        if country in missing_sub_region_map:
            sub_region_dict[country] = missing_sub_region_map[country]
        if country in missing_region_map:
            region_dict[country] = missing_region_map[country]
    
    # Return a sorted list of countries present in the IDS dataset, as well as the corresponding sub-regions and regions dictionaries
    return countries_list, sub_region_dict, region_dict
          
def get_drug_selector_function(drug_name):
    '''
    Parameters
    ----------
    drug_name : str
    Returns
    -------
    function
        Function generator for filtering functions used to extract seizures corresponding to a given drug and its derivatives.
    '''
    
    if drug_name == 'Cocaine':
        
        def get_cocaine_seizures(df):
            df_cocaine = df[(df['DRUG_NAME'] == 'Cocaine') | (df['DRUG_NAME'] == 'Cocaine HCL') | (df['DRUG_NAME'] == 'Coca paste') | (df['DRUG_NAME'] == 'Coca leaf') | (df['DRUG_NAME'] == 'Crack')]
            return df_cocaine
            
        return get_cocaine_seizures
    
    elif drug_name == 'Heroin':
        
        def get_heroin_seizures(df):
            df_heroin = df[(df['DRUG_NAME'] == 'Heroin') | (df['DRUG_NAME'] == 'Opium') | (df['DRUG_NAME'] == 'Opium Poppy') | (df['DRUG_NAME'] == 'Poppy seeds') | (df['DRUG_NAME'] == 'Poppy straw') | (df['DRUG_NAME'] == 'Morphine')]
            return df_heroin
            
        return get_heroin_seizures
    
    elif drug_name == 'Cannabis':
        
        def get_cannabis_seizures(df):
            df_cannabis = df[(df['DRUG_NAME'] == 'Cannabis') | (df['DRUG_NAME'] == 'Cannabis resin') | (df['DRUG_NAME'] == 'Cannabis Oil') | (df['DRUG_NAME'] == 'Cannabis Pollen') | (df['DRUG_NAME'] == 'Cannabis seeds') | (df['DRUG_NAME'] == 'Cannabis Plants') | (df['DRUG_NAME'] == 'Cannabis Herb (Marijuana)') | (df['DRUG_NAME'] == 'THC')]
            return df_cannabis
            
        return get_cannabis_seizures
    
    elif drug_name == 'Amphetamine':
        
        def get_amphetamine_seizures(df):
            df_amphetamine = df[(df['DRUG_NAME'] == 'Amphetamine') | (df['DRUG_NAME'] == 'Methamphetamine') | (df['DRUG_NAME'] == '4-Fluoroamphetamine') | (df['DRUG_NAME'] == 'MDA')]
            return df_amphetamine
            
        return get_amphetamine_seizures
    
    elif drug_name == 'Ecstasy':
        
        def get_ecstasy_seizures(df):
            df_ecstasy = df[(df['DRUG_NAME'] == 'Ecstasy') | (df['DRUG_NAME'] == 'MDP2P')]
            return df_ecstasy
            
        return get_ecstasy_seizures
    
    else:
        raise Exception('Invalid drug type!')            
          
def get_purity_adjusted_seizures(df_ids, countries_list = None, sub_region_dict = None, region_dict = None, 
                                 drug_list = ['Cocaine', 'Heroin', 'Cannabis', 'Amphetamine', 'Ecstasy'], 
                                 purity_file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Purity.xlsx', 
                                 start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_ids : dict of pd.DataFrame
    purity_file : str, optional
        DESCRIPTION. file containing data on national purity levels.
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    output_df : dict of pd.DataFrame
        Produces a data structure containing all purity-adjusted seizures for cocaine, heroin, cannabis, amphetamine, and ecstasy, grouped by year of seizure.
    '''
    
    # Create output df
    output_df = create_output_df() # dict of pd.DataFrames
    
    # Obtain the purity levels 
    df_pure = read_xlsx(file = purity_file)
    
    # Get the list of countries
    if countries_list is None:
        countries_list, sub_region_dict, region_dict = get_ids_locations(df_ids)
    
    # Get the seizures corresponding to each drug
    for drug in drug_list:
        
        # Get the selector function for the given drug-type
        get_drug_seizures = get_drug_selector_function(drug)
        
        # Iterate over the period of time
        for year in range(start_year, end_year + 1):
            
            # Obtain drug and drug derivatives seizures for the given year for all countries
            df_year_drug = get_drug_seizures(df_ids[year])
            
            # Iterate over the country list
            for country in countries_list:
                
                # Initialize container for total drug seizures
                drug_total = 0
                
                # Obtain region and sub-region
                try:
                    region = region_dict[country]
                except:
                    region = 'Unknown'
                try:
                    sub_region = sub_region_dict[country]
                except:
                    sub_region = 'Unknown'
                
                # Obtain drug and drug derivatives seizures for the given year and country
                df_year_drug_country = df_year_drug[df_year_drug['COUNTRY_OF_SEIZURE'] == country]
                
                # Conversion for drug derivatives
                for i in df_year_drug_country.index:
                    drug_total += convert(drug, df_year_drug_country['AMOUNT_OF_DRUG'][i], df_year_drug_country['DRUG_NAME'][i], df_year_drug_country['DRUG_UNIT'][i]) 
                
                # Adjust total seized quantity by the average purity level in each country
                drug_total *= float(df_pure[year][(df_pure[year]['Location'] == country) & (df_pure[year]['Drug'] == drug)]['Purity'])
                
                # Add the new row to target_df
                new_row = {'Region': region, 'SubRegion': sub_region, 'Country': country, 'Drug': drug, 'Quantity(kg)': drug_total}
                output_df[year].loc[len(output_df[year])] = new_row
    
    # Sort each df alphabetically by country
    for year in range(start_year, end_year + 1):
        output_df[year] = output_df[year].sort_values(['Region', 'SubRegion', 'Country', 'Drug']).reset_index(drop = True)
    
    # Return the data
    return output_df

def write_to_xlsx(output, target_file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Seizures.xlsx'):
    '''
    Parameters
    ----------
    output : dict of pd.DataFrame obejcts
    target_file : str
        The default is 'Seizures.xlsx'.
    Returns
    -------
    None; Writes the ouput to the file, creating an .xlsx document with one spreadsheet corresponding to each year.
    '''
    
    with pd.ExcelWriter(target_file) as writer:  
        for year in output.keys():
            output[year].to_excel(writer, sheet_name = str(year))
            
def get_relative_weights(network):
    '''
    Parameters
    ----------
    network : nx.DiGraph
    Returns
    -------
    network : nx.DiGraph
        Helper function that adds a 'relative_weight' attribute to each edge by summing the weights of all neighbors and dividing by the number of neighbors.
    '''
    d = dict()
    for prev, curr in network.edges:
        if curr in d:
            d[curr] += network[prev][curr]['weight']
        else:
            d[curr] = network[prev][curr]['weight']
    for prev, curr in network.edges:
        network[prev][curr]['relative_weight'] = network[prev][curr]['weight'] / d[curr]
    return network

def get_market_values(network, year, drug, file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Markets.xlsx'):
    '''
    Parameters
    ----------
    network : nx.DiGraph

    year : int
    drug : str
    file : str, optional
        The default is 'Markets.xlsx'.
    Returns
    -------
    network : nx.DiGraph
        Populates the 'market' attribute of each node with the market values.
    '''
    xlsx = pd.ExcelFile(file)
    df_markets = pd.read_excel(xlsx, str(year))
    for node in network.nodes:
        network.nodes[node]['market'] = float(df_markets[(df_markets['Drug'] == drug) & (df_markets['Country'] == node)]['Market(kg)'])
    return network 

def get_drug_network_by_year(drug_name, df_ids, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    drug_name : str
    df_ids : dict of pd.DataFrames
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    network_by_year : dict of nx.DiGraphs
        Construct a dict of networks containing the graphs resulting from the seizures for each year.
        Nodes have the attribute 'producer': True or False.
        Edges have the attribute 'weight': float (total purity-adjusted quantity along the given edge).
    '''
    
    # Initialize container for the yearly graphs: dict of nx.DiGraphs
    network_by_year = {year: nx.DiGraph() for year in range(start_year, end_year + 1)}
    
    # Get the selector function for the given drug-type
    get_drug_seizures = get_drug_selector_function(drug_name)
    
    # Iterate over the time period
    for year in range(start_year, end_year + 1):
        
        # Select the year 
        df_year = df_ids[year]
        
        # Select the drug
        df_year_drug = get_drug_seizures(df_year)
        
        # Iterate over the results
        for ind in df_year_drug.index:
            
            # Check for non-string values (including nan) and 'Unknown' or 'Other'
            if not isinstance(df_year_drug['COUNTRY_OF_SEIZURE'][ind], str) or df_year_drug['COUNTRY_OF_SEIZURE'][ind] == 'Unknown' or df_year_drug['COUNTRY_OF_SEIZURE'][ind] == 'Other':
                continue 
            else:
                country_of_seizure = df_year_drug['COUNTRY_OF_SEIZURE'][ind]
                
            # Get the specific drug type
            drug_type = df_year_drug['DRUG_NAME'][ind]
            
            # Check for non-string values (including nan) and 'Unknown' or 'Other'
            if isinstance(df_year_drug['PRODUCING_COUNTRY'][ind], str) and df_year_drug['PRODUCING_COUNTRY'][ind] != 'Unknown' and df_year_drug['PRODUCING_COUNTRY'][ind] != 'Other':
                producing_country = df_year_drug['PRODUCING_COUNTRY'][ind]
            else:
                producing_country = None
            
            # Check for non-string values (including nan) and 'Unknown' or 'Other'
            if isinstance(df_year_drug['DEPARTURE_COUNTRY'][ind], str) and df_year_drug['DEPARTURE_COUNTRY'][ind] != 'Unknown' and df_year_drug['DEPARTURE_COUNTRY'][ind] != 'Other':
                departure_country = df_year_drug['DEPARTURE_COUNTRY'][ind]
            else:
                departure_country = None
            
            # Check for non-string values (including nan) and 'Unknown' or 'Other'
            if isinstance(df_year_drug['DESTINATION_COUNTRY'][ind], str) and df_year_drug['DESTINATION_COUNTRY'][ind] != 'Unknown' and df_year_drug['DESTINATION_COUNTRY'][ind] != 'Other':
                destination_country = df_year_drug['DESTINATION_COUNTRY'][ind]
            else:
                destination_country = None
            
            # Get the drug amount
            drug_amount = df_year_drug['AMOUNT_OF_DRUG'][ind]
            
            # Get the drug unit
            drug_unit = df_year_drug['DRUG_UNIT'][ind]
            
            # Convert the amount of drug to pure subtance in kilograms
            drug_amount = convert(drug_name, drug_amount, drug_type, drug_unit)
            
            # Check is drug amount is positive, else continue
            if drug_amount <= 0:
                continue
                
            # Add the nodes if not present already
            if not (country_of_seizure in network_by_year[year].nodes):
                network_by_year[year].add_node(country_of_seizure, producer = False)
            if (not (departure_country in network_by_year[year].nodes)) and (not (departure_country is None)):
                network_by_year[year].add_node(departure_country, producer = False)
            if not (destination_country in network_by_year[year].nodes) and (not (destination_country is None)):
                network_by_year[year].add_node(destination_country, producer = False)
            if not (producing_country is None):
                if not (producing_country in network_by_year[year].nodes):
                    network_by_year[year].add_node(producing_country, producer = True)
                else:
                    # Update the profucer status
                    network_by_year[year].nodes[producing_country]['producer'] = True
            
            # Add the edges
            if (not (departure_country is None)) and (departure_country != country_of_seizure) and (departure_country != 'Unknown'):
                
                if (departure_country, country_of_seizure) in network_by_year[year].edges:
                    network_by_year[year].edges[departure_country, country_of_seizure]['weight'] += drug_amount
                else:
                    network_by_year[year].add_edge(departure_country, country_of_seizure, weight = drug_amount)
            if (not (destination_country is None)) and (destination_country != country_of_seizure) and (destination_country != 'Unknown'):
                
                if (country_of_seizure, destination_country) in network_by_year[year].edges:
                    network_by_year[year].edges[country_of_seizure, destination_country]['weight'] += drug_amount
                else:
                    network_by_year[year].add_edge(country_of_seizure, destination_country, weight = drug_amount)
    
        # Add the relative weights of each edge for the current year
        network_by_year[year] = get_relative_weights(network_by_year[year])    
        
        # Add the national market value to each node
        network_by_year[year] = get_market_values(network_by_year[year], year, drug_name)
    
    # Return the dictionary of networks
    return network_by_year