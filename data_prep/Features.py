import numpy as np
import pandas as pd
import networkx as nx
import Seizures
import Aggregation

import warnings
warnings.filterwarnings('ignore')

def get_drug_prices(file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Drug_prices.xlsx', drug_list = ['Cocaine', 'Heroin'], 
                    countries_list = None, sub_region_dict = None, region_dict = None, 
                    start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    file : str, optional
    drug_list : list of str, optional
    countries_list : list of str, optional 
    sub_region_dict : dict, optional
    region_dict : dict, optional
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    seiz_df : dict of pd.DataFrames
        Creates a dict of dataframes with the wholesale prices for the specified drug list
    '''
    
    # Input validation
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
    
    # Read the data from the file
    df_price = pd.read_excel(file)
    
    # Take only entries measured in USD/kg at wholesale level
    df_price = df_price[(df_price['Unit'] == 'Kilogram') & (df_price["LevelOfSale"] == 'Wholesale')]
    
    # Rename drug type for convenience
    df_price['Drug'] = df_price['Drug'].replace('Cocaine salts', 'Cocaine')
    df_price['Drug'] = df_price['Drug'].replace('Cocaine hydrochloride', 'Cocaine')
    
    # Auxiliary function to deal with missing vals
    def _remove_missing_vals(df_aux):
        # Impute typical vals with averages or existing vals and remove the remaining entries
        for index, row in df_aux.iterrows():
            if np.isnan(row['Typical_USD']):
                if not np.isnan(row['Minimum_USD']) and not np.isnan(row['Maximum_USD']):
                    row['Typical_USD'] = (row['Minimum_USD'] + row['Maximum_USD']) / 2
                elif not np.isnan(row['Minimum_USD']):
                    row['Typical_USD'] = row['Minimum_USD']
                else:
                    row['Typical_USD'] = row['Maximum_USD']
            df_aux.at[index, 'Typical_USD'] = row['Typical_USD']
            
        df_aux = df_aux[df_aux['Typical_USD'].notna()]
        return df_aux
    
    # Auxiliary function to compute sub_regional vals
    def _get_sub_region_avgs(df_aux, drug, start_year = 2006, end_year = 2017):
        output = dict()
        for year in range(start_year, end_year + 1):
            output[year] = dict(df_aux[(df_aux['Drug'] == drug) & (df_aux['Year'] == year)].groupby('SubRegion')['Typical_USD'].mean())
        return output

    # Auxiliary function to compute regional vals
    def _get_region_avgs(df_aux, drug, start_year = 2006, end_year = 2017):
        output = dict()
        for year in range(start_year, end_year + 1):
            output[year] = dict(df_aux[(df_aux['Drug'] == drug) & (df_aux['Year'] == year)].groupby('Region')['Typical_USD'].mean())
        return output

    # Auxiliary function to compute global vals
    def _get_global_avgs(region_avgs):
        # Create dict of total averages
        year_total = dict()

        # Keep track of total avergae for the entire period and missing years
        total_average = 0
        missing_years = 0

        # Iterate over years
        for year in region_avgs.keys():
            # Check if no data exists for the given year
            if len(region_avgs[year]) == 0:
                year_total[year] = None
                missing_years += 1
                continue
            # Compute the yearly global average across all available regions
            total = 0
            for region in region_avgs[year].keys():
                total += region_avgs[year][region]
            year_total[year] = (total / len(region_avgs[year].keys()))
            total_average += year_total[year]

        # Fill in missing years if they exist
        if missing_years > 0:
            total_average = (total_average / (len(year_total.keys()) - missing_years))
            for year in year_total.keys():
                if year_total[year] is None:
                    year_total[year] = total_average

        return year_total
    
    # Auxiliary function to extract the list of locations
    def _get_locations(df_aux):
        return list(set(df_aux['Country/Territory']))

    # Auxiliary function to return the subregion
    def _get_sub_region(location, df_aux):
        return list(set(df_aux[df_aux['Country/Territory'] == location]['SubRegion']))[0]

    # Auxiliary function to return the region
    def _get_region(location, df_aux):
        return list(set(df_aux[df_aux['Country/Territory'] == location]['Region']))[0]

    # Auxiliary function to create output data structure: dict of dataframes
    def _create_output_df(start_year = 2006, end_year = 2017):
        price_df = dict()
        for i in range(start_year, end_year + 1):
            price_df[i] = pd.DataFrame(columns = ['Country', 'Sub_Region', 'Region', 'Price(USD)'])
        return price_df
    
    # Auxiliary function to retrieve price data for a given country for a given period
    def _get_location_values(location, df_aux, target_df, drug_types = drug_list, sub_region_dict = None, region_dict = None, start_year = 2006, end_year = 2017):
        
        # If provided, we use the sub-region and region data
        if sub_region_dict is None:
            sub_region = _get_sub_region(location, df_aux)
        else:
            sub_region = sub_region_dict[location]

        if region_dict is None:
            region = _get_region(location, df_aux)
        else:
            region = region_dict[location]

        # Iterate over all drug types
        for drug in drug_types:
            # Retrieve regional and sub-regional values, as well as annual global averages to use for imputation
            sub_region_vals = _get_sub_region_avgs(df_aux, drug)
            region_vals = _get_region_avgs(df_aux, drug)
            global_vals = _get_global_avgs(region_vals)

            # Prepare an empty vector to store the time-series
            time_series = np.zeros(end_year - start_year + 1)

            # Iterate over the given period of time
            for year in range(start_year, end_year + 1):
                #Extract data for the given location, drug, and year
                df_temp = df_aux[(df_aux['Country/Territory'] == location) & (df_aux['Drug'] == drug) & (df_aux['Year'] == year)]
                # If no results are found
                if len(df_temp) == 0:
                    # If sub-regional values are available, we use those
                    if sub_region in sub_region_vals[year].keys():
                        time_series[year-start_year] = sub_region_vals[year][sub_region]
                    # Else if regional values are available, we use those
                    elif region in region_vals[year].keys():
                        time_series[year-start_year] = region_vals[year][region]
                    else:
                        time_series[year-start_year] = global_vals[year]
                # If exactly one result is found
                elif len(df_temp) == 1:
                    time_series[year-start_year] = df_temp['Typical_USD']
                # If multiple results are found
                else:
                    time_series[year-start_year] = df_temp['Typical_USD'].mean()

                new_row = {'Country': location, 
                           'Sub_Region': sub_region, 
                           'Region': region,
                           'Price(USD)': time_series[year-start_year]}
                target_df[year].loc[len(target_df[year])] = new_row
    
    # Remove missing values
    df_price = _remove_missing_vals(df_price)
    
    # Create the output data structure: dict of dataframes
    output_df = _create_output_df()
    
    # Get the list of countries
    if countries_list is None:
        locations = _get_locations(df_price)
    else:
        locations = countries_list
    
    # Iterate over the list of countries
    for location in locations:
        _get_location_values(location, df_price, output_df, 
                             sub_region_dict = sub_region_dict, region_dict = region_dict, 
                             start_year = start_year, end_year = end_year)
        
    # Return output_df
    return output_df

def get_gdp_per_capita(countries_list, file = "/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/GDP_per_capita.xlsx", 
                       start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    countries_list : list
    file : str, optional
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    output_df : dict of pd.DataFrames
        Creates a dict of dataframes with the GDP per capita for the specified list of countries
    '''

    # Input validation
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
    
    # Read the data from the file
    df_gdp = pd.read_excel(file)
    
    # Create output data structure: dict of dataframes
    output_df = dict()
    for i in range(start_year, end_year + 1):
        output_df[i] = pd.DataFrame(columns = ['Country', 'GDP/capita'])
    
    for year in range(start_year, end_year + 1):
        year_format = f"{year} [YR{year}]"
        for country in countries_list:
            row = {'Country': country, 'GDP/capita': float(df_gdp[df_gdp['Country Name'] == country][year_format])}
            output_df[year].loc[len(output_df[year])] = row
        
    # Return output_df
    return output_df

def get_coordinates(countries_list, file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/countries.csv'):
    '''
    Parameters
    ----------
    countries_list : list
    file : str, optional
    Returns
    -------
    output_df : pd.DataFrame
        Creates a dataframe with the geographical coordinates for the specified list of countries
    '''

    # Read the data from the file
    df_coord = pd.read_csv(file)
    
    # Replace countries names for consistency
    names_to_replace = {
    'Moldova': 'Moldova, Republic of',
    'R?union': 'Réunion',
    'Bolivia': 'Bolivia, Plurinational State of',
    'Taiwan': 'Taiwan, Province of China',
    'Iran': 'Iran, Islamic Republic of',
    'S?o Tom? and Pr?ncipe': 'Sao Tome and Principe',
    'Laos': "Lao People's Democratic Republic",
    'Macedonia [FYROM]': 'North Macedonia',
    'North Korea': "Korea, Democratic People's Republic of",
    'Swaziland': 'Eswatini',
    'Saint Lucia': 'St. Lucia',
    'Venezuela': 'Venezuela, Bolivarian Republic of',
    'Tanzania': 'Tanzania, United Republic of',
    'Vietnam': 'Viet Nam',
    "C?te d'Ivoire": "Côte d'Ivoire",
    'Kosovo': 'Kosovo under UNSCR 1244',
    'Syria': 'Syrian Arab Republic',
    'Libya': 'Libyan Arab Jamahiriya',
    'Myanmar [Burma]': 'Myanmar',
    'Russia': 'Russian Federation',
    'South Korea': 'Korea, Republic of',
    'Congo [Republic]': 'Congo',
    'Congo [DRC]': 'Congo, the Democratic Republic of the'
    }
    df_coord['name'] = df_coord['name'].replace(names_to_replace)
    
    # Fill in missing values
    df_coord.loc[len(df_coord)] = {
            'country': 'CW', 
            'latitude': float(df_coord[df_coord['name'] == 'Netherlands Antilles']['latitude']),
            'longitude': float(df_coord[df_coord['name'] == 'Netherlands Antilles']['longitude']),
            'name': 'Curaçao'
            }
    
    # Rename columns for consistency
    df_coord = df_coord.rename(columns = {'country': 'ISO', 'latitude': 'Latitude', 'longitude': 'Longitude', 'name': 'Country'})
    
    # Pick only the countries in countries_list
    df_coord = df_coord.query("Country in @countries_list")
    df_coord = df_coord.reset_index(drop = True)
    
    # Missing ISO for Namibia
    df_coord = df_coord.set_index('Country')
    df_coord.at['Namibia', 'ISO'] = 'NA'
    df_coord = df_coord.reset_index()
    
    # Return the output
    return df_coord

def get_social_indicators(countries_list, file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Governance_Indicators.xlsx', start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    countries_list : list
    file : str, optional
    Returns
    -------
    output_df : dict of pd.DataFrames
        Creates a dict of dataframes with the social and political indicators for the specified list of countries
    '''

    # Input validation
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    # Read the data from the file
    df_gov = pd.read_excel(file)
    
    # Create output data structure: dict of dataframes
    output_df = dict()
    for i in range(start_year, end_year + 1):
        output_df[i] = pd.DataFrame(columns = ['Country', 'Control_of_Corruption', 
                                              'Gov_Effectiveness', 'Stability_No_Terrorism',
                                              'Regulatory_Quality', 'Rule_of_Law'])
    
    for year in range(start_year, end_year + 1):
        year_format = f"{year} [YR{year}]"
        for country in countries_list:
            try:
                row = {'Country': country, 
                       'Control_of_Corruption': float(df_gov[(df_gov['Country Name'] == country) & (df_gov['Series Name'] == 'Control of Corruption: Estimate')][year_format]),
                       'Gov_Effectiveness': float(df_gov[(df_gov['Country Name'] == country) & (df_gov['Series Name'] == 'Government Effectiveness: Estimate')][year_format]),
                       'Stability_No_Terrorism': float(df_gov[(df_gov['Country Name'] == country) & (df_gov['Series Name'] == 'Political Stability and Absence of Violence/Terrorism: Estimate')][year_format]),
                       'Regulatory_Quality': float(df_gov[(df_gov['Country Name'] == country) & (df_gov['Series Name'] == 'Regulatory Quality: Estimate')][year_format]),
                       'Rule_of_Law': float(df_gov[(df_gov['Country Name'] == country) & (df_gov['Series Name'] == 'Rule of Law: Estimate')][year_format])
                       }
                output_df[year].loc[len(output_df[year])] = row
            except:
                print(country)
    
    # Return the output
    return output_df

def get_node_attributes(drug, df_ids, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    drug : str
    df_ids : dict of pd.DataFrames
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    output_df : dict of pd.DataFrames
        Creates a dict of dataframes with all the country features of the nations present in the corresponding drug network
    '''
    # Input validation
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
    
    # Get the locations present in the network of the specific drug
    countries_list, sub_region_dict, region_dict = Seizures.get_ids_locations(df_ids, drug_list = [drug])
    
    # Get individual data structures
    df_price = get_drug_prices(countries_list = countries_list, sub_region_dict = sub_region_dict,
                           region_dict = region_dict, drug_list = [drug],
                           start_year = start_year, end_year = end_year)
    
    df_mark = Aggregation.get_national_markets_df(countries_list, 
                                              sub_region_dict,
                                              region_dict,
                                              df_ids,
                                              drug_list = [drug])
    
    df_gdp = get_gdp_per_capita(countries_list = countries_list, start_year = start_year, end_year = end_year)
    
    df_coord = get_coordinates(countries_list = countries_list)
    
    df_gov = get_social_indicators(countries_list = countries_list, start_year = start_year, end_year = end_year)
    
    # Create the output_df
    output_df = df_price.copy()
    
    # Iterate over the time period
    for year in range(start_year, end_year + 1):
        output_df[year] = output_df[year].join(df_mark[year].drop(columns = ['Drug', 'SubRegion']).set_index('Country'), on = 'Country')
        output_df[year] = output_df[year].join(df_gdp[year].set_index('Country'), on = 'Country')
        output_df[year] = output_df[year].join(df_coord.set_index('Country'), on = 'Country')
        output_df[year] = output_df[year].join(df_gov[year].set_index('Country'), on = 'Country')
    
        # Rearrange the columns
        output_df[year] = output_df[year].reindex(columns = [
                                    'Country', 'Sub_Region', 'Region', 'ISO', 'Latitude', 'Longitude', 
                                    'Price(USD)', 'Seizures(kg)', 'Consumption(kg)', 'Market(kg)',
                                    'GDP/capita', 'Control_of_Corruption', 'Gov_Effectiveness', 
                                    'Stability_No_Terrorism', 'Regulatory_Quality', 'Rule_of_Law'])
    
    # Return the output
    return output_df

def aggregate_yearly_features(df, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df : dict of pd.DataFrames
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    df : dict of pd.DataFrames
        Adds an additional pd.DataFrame to the input dict which contains average features across the time period
    '''
    # Create a new dataframe and make it containt the start_year values
    df['total'] = df[start_year].copy()
    
    # Get the column names over which we want to average
    avg_cols = [col for col in list(df[start_year].columns) if col not in ['Country', 'Sub_Region', 'Region', 'ISO', 'Latitude', 'Longitude']]
    
    # Iterate over the time period and average over the columns in avg_cols
    for year in range(start_year + 1, end_year + 1):
        df['total'][avg_cols] += df[year][avg_cols]
    df['total'][avg_cols] /= (end_year - start_year + 1)
    return df

def aggregate_yearly_edges(G, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    G : dict of nx.DiGraphs
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    list(edge_set) : list
        Returns a list of all edges present in the yearly networks across the time period
    '''
    edge_set = set()
    for year in range(start_year, end_year):
        for edge in G[year].edges:
            edge_set.add(edge)
    return list(edge_set)

def get_network_data(drug, df_ids = None,  
                     for_pyg = True, for_R = True,
                     aggregate_over_time_period = True,
                     write_to_file = True, 
                     base_file_path = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/',
                     start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    drug : str
    df_ids : dict of pd.DataFrames
    for_pyg : bool, optional (pytorch_geometric format)
    for_R : bool, optionl (R format)
    base_file_path : str, optional
    start_year : int, optional
    end_year : int, optional
    Returns
    -------
    output_networl : nx.DiGraph
        Returns a directed graph containing the aggregated data and optionally writes to a .gml file
    '''
    
    # Checks
    if not for_pyg and not for_R:
        raise Exception("The data must be prepared either for pyg or for R!")
    if start_year < 2006 or end_year > 2017:
        raise Exception("Data is available only for period 2006-2017!")

    # If no IDS data is not loaded, read it
    if df_ids is None:
        df_ids = Seizures.read_xlsx()
    
    # Get the node attributes
    df_yearly = get_node_attributes(drug, df_ids, start_year = start_year, end_year = end_year)
    df_aggregate = aggregate_yearly_features(df_yearly, start_year = start_year, end_year = end_year)
    
    # Get the edge data
    dict_of_nets = Seizures.get_drug_network_by_year(drug, df_ids, start_year = start_year, end_year= end_year)
    aggregate_edge_list = aggregate_yearly_edges(dict_of_nets, start_year = start_year, end_year = end_year)
    
    # Add the features
    for year in range(start_year, end_year + 1):
        nx.set_node_attributes(dict_of_nets[year], df_aggregate[year])

    # Create output container
    output = dict()

    if for_pyg:

        #Create output subcontainer
        output['pyg'] = dict()
        # Create a list of the networks we are interested in
        period = list(range(start_year, end_year + 1))
        # Potentially add agggregate data
        if aggregate_over_time_period:
            period.append('total')

        # Iterate over the time period
        for net in period:
            # Construct a new network
            output_network = nx.DiGraph()
            node_list = list()
            # Preproccesing: one-hot encoding plus dropping 'ISO' column
            df_features = pd.get_dummies(df_aggregate[net], columns = ['Sub_Region', 'Region'], dtype = float).drop(columns = ['ISO'])
            # Add the node with attributes in pytorch convention: y is the country name, x is a list of features
            for index, row in df_features.iterrows():
                node_list.append((row['Country'], {'y': row['Country'], 'x': list(row[1:])})) 
            output_network.add_nodes_from(node_list)
            if net == 'total':
                output_network.add_edges_from(aggregate_edge_list)
            else:
                output_network.add_edges_from(dict_of_nets[net].edges)
            
            # Add the network to output
            output['pyg'][net] = output_network

            # Write the output
            if write_to_file:
                
                # Create the path
                if net == 'total':
                    write_file_path = base_file_path + 'pyg_data/' + f'{drug}' + '_aggregate' + f'_{start_year}_{end_year}' + '.gml'
                else:
                    write_file_path = base_file_path + 'pyg_data/' + f'{drug}' + f'_{net}' + '.gml'

                # Write to the given path in gml format
                nx.write_gml(output_network, write_file_path)
        
    if for_R == True:

        #Create output subcontainer
        output['R'] = dict()
        # Create a list of the networks we are interested in
        period = list(range(start_year, end_year + 1))
        # Potentially add agggregate data
        if aggregate_over_time_period:
            period.append('total')

        for net in period:

            # Get the node features
            nodes_df = df_aggregate[net]

            # Get the edges
            if net == 'total':
                edges_df = pd.DataFrame(aggregate_edge_list, columns = ['to', 'from'])
            else:
                edges_df = pd.DataFrame(dict_of_nets[net].edges, columns = ['to', 'from'])

            # Add the datasets to the output
            output['R'][f'nodes_{net}'] = nodes_df
            output['R'][f'edges_{net}'] = edges_df
            
            # Write the output
            if write_to_file:
                
                # Create the path
                if net == 'total':
                    write_file_path_nodes = base_file_path + 'R_data/' + f'{drug}' + '_nodes' +  '_aggregate' + f'_{start_year}_{end_year}' + '.csv'
                    write_file_path_edges = base_file_path + 'R_data/' + f'{drug}' + '_edges' +  '_aggregate' + f'_{start_year}_{end_year}' + '.csv'
                else:
                    write_file_path_nodes = base_file_path + 'R_data/' + f'{drug}' + '_nodes' + f'_{net}' + '.csv'
                    write_file_path_edges = base_file_path + 'R_data/' + f'{drug}' + '_edges' + f'_{net}' + '.csv'

                # Write to the given path in .csv format
                nodes_df.to_csv(write_file_path_nodes)
                edges_df.to_csv(write_file_path_edges)
            
    return output