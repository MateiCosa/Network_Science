
# Collection of functions for obtaining drug prevalence levels from UNODC data
# The default period is 2006-2017;
# The drugs of interest are: cocaine, opioids, cannabis, amphetamines, and ecstasy
# Source of data: https://dataunodc.un.org/dp-drug-use-prevalence

import numpy as np
import pandas as pd

# Name conversion for convenience and compatibility
drug_name_change = {
                    'Cocaine': 'Cocaine',
                    'Opioids': 'Heroin',
                    'Cannabis': 'Cannabis',
                    'Amphetamines': 'Amphetamine',
                    'Ecstasy': 'Ecstasy'
                   }

def get_drug_types(initial_values = False):
    '''
    Parameters
    ----------
    initial_values : bool
    Returns
    -------
    output : list of strings
        Retrieves the list of drugs of interest
    '''
    # Inially we combine together opioids and opiates, later we are left only with opioids for convenience
    if initial_values == True:
        output = ['Cocaine', 'Opioids', 'Opiates', 'Amphetamines', 'Ecstasy', 'Cannabis']
    else:
        output = ['Cocaine', 'Opioids', 'Amphetamines', 'Ecstasy', 'Cannabis']
    return output

def prepare_data(file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/Drug_prevalence.xlsx'):
    '''
    Parameters
    ----------
    file : str
    Returns
    -------
    df_prev : pd.DataFrame
        Performs necessary pre-processing: merges together input spreadsheets and transforms prevalence values into percentages.
    '''
    # We read the excel spreadsheets corresponding to each drug and combine them into a single dataframe
    xlsx = pd.ExcelFile(file)
    df_prev = pd.DataFrame()
    for drug in get_drug_types(initial_values = True):
        new_df = pd.read_excel(xlsx, drug)
        if drug == 'Opiates':
            new_df['Drug'] = 'Opioids'
        else:
            new_df['Drug'] = drug
        df_prev = df_prev.append(new_df, ignore_index = True)
    
    # We transform the prevalence values in percentages
    df_prev['Best'] = df_prev['Best'] / 100
    
    # We return the pre-processed dataframe
    return df_prev

def create_output_df(start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    start_year : int
    end_year : int
    Returns
    -------
    prev_df : dict of pd.DataFrames
        Creates an empty dictionary of dataframes to store the final output.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    prev_df = dict()
    for i in range(start_year, end_year + 1):
        prev_df[i] = pd.DataFrame(columns=['Location', 'Drug', 'Prevalence'])
    return prev_df

def get_locations(df_prev):
    '''
    Parameters
    ----------
    df_prev : pd.DataFrame
    Returns
    -------
    list
        Obtains the list of countries/territories contained in the dataframe.
    '''
    return list(set(df_prev['Country/Territory']))

def get_sub_region(location, df_prev):
    '''
    Parameters
    ----------
    location : str
    df_prev : pd.DataFrame
    Returns
    -------
    list
        Retrieves the sub-region the location belongs to.
    '''
    if not location in get_locations(df_prev):
        raise Exception('Invalid location!')
        
    return list(set(df_prev[df_prev['Country/Territory'] == location]['Sub-region']))[0]

def get_region(location, df_prev):
    '''
    Parameters
    ----------
    location : str
    df_prev : pd.DataFrame
    Returns
    -------
    list
        Retrieves the region the location belongs to.
    '''
    if not location in get_locations(df_prev):
        raise Exception('Invalid location!')
        
    return list(set(df_prev[df_prev['Country/Territory'] == location]['Region']))[0]

def get_sub_region_avgs(df_prev, drug, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_prev : pd.DataFrame
    drug : str
    start_year : int
    end_year : int
    Returns
    -------
    output : dict of dicts
        Compute average prevalence levels at a sub-regional levels for a given drug and for a given period of time.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    if not (isinstance(drug, str) and drug in get_drug_types()):
        raise Exception('Invalid drug!')
        
    output = dict()
    for year in range(start_year, end_year + 1):
        output[year] = dict(df_prev[(df_prev['Drug'] == drug) & (df_prev['Year'] == year)].groupby('Sub-region')['Best'].mean())
    return output

def get_region_avgs(df_prev, drug, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_prev : pd.DataFrame
    drug : str
    start_year : int
    end_year : int
    Returns
    -------
    output : dict of dicts
        Compute average prevalence levels at a regional levels for a given drug and for a given period of time.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    if not (isinstance(drug, str) and drug in get_drug_types()):
        raise Exception('Invalid drug!')
        
    output = dict()
    for year in range(start_year, end_year + 1):
        output[year] = dict(df_prev[(df_prev['Drug'] == drug) & (df_prev['Year'] == year)].groupby('Region')['Best'].mean())
    return output

def get_global_avgs(region_avgs):
    '''
    Parameters
    ----------
    region_avgs : dict of dicts
    Returns
    -------
    year_total : dict
        Computes global average prevalence levels for the period of time contained in region_avgs.
    '''
    # Create dict of total averages
    year_total = dict()
    
    # Keep track of total average for the entire period and missing years
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

def get_location_values(location, df_prev, target_df, 
                        sub_region_dict = None, region_dict = None, 
                        start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    location : str
    df_prev : pd.DataFrame
    target_df : dict of pd.DataFrames
    start_year : int
    end_year : int
    Returns
    -------
    None; populates the output container with prevalence levels for the given period and location.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    # Retrieve the list of drugs and the region & sub-region of the given location
    drug_types = get_drug_types()
    
    # If provided, we use the sub-region and region data
    if sub_region_dict is None:
        sub_region = get_sub_region(location, df_prev)
    else:
        sub_region = sub_region_dict[location]
        
    if region_dict is None:
        region = get_region(location, df_prev)
    else:
        region = region_dict[location]
    
    # Iterate over all drug types
    for drug in drug_types:
        # Retrieve regional and sub-regional values, as well as annual global averages to use for imputation
        sub_region_vals = get_sub_region_avgs(df_prev, drug)
        region_vals = get_region_avgs(df_prev, drug)
        global_vals = get_global_avgs(region_vals)
        
        # Prepare an empty vector to store the time-series
        time_series = np.zeros(end_year - start_year + 1)
        
        # Iterate over the given period of time
        for year in range(start_year, end_year + 1):
            #Extract data for the given location, drug, and year
            df_temp = df_prev[(df_prev['Country/Territory'] == location) & (df_prev['Drug'] == drug) & (df_prev['Year'] == year)]
            # If no results are found
            if len(df_temp) == 0:
                time_series[year-start_year] = np.nan
            # If exactly one result is found
            elif len(df_temp) == 1:
                time_series[year-start_year] = df_temp['Best']
            # If multiple results are found
            else:
                time_series[year-start_year] = df_temp['Best'].max()
        
        # We compute the number of missing values in the time series
        missing_vals = np.sum(np.isnan(time_series))
        
        # If all values are missing we fill them with sub-regional, regional, or global averages
        if missing_vals == (end_year - start_year + 1):
            for year in range(start_year, end_year + 1):
                if sub_region in sub_region_vals[year].keys():
                    time_series[year-start_year] = sub_region_vals[year][sub_region]
                elif region in region_vals[year].keys():
                    time_series[year-start_year] = region_vals[year][region]
                else:
                    time_series[year-start_year] = global_vals[year]
                    
        # Otherwise, if there is at least one missing value and at least one value present in time series, we perform interpolation
        elif missing_vals > 0:
            
            # We check if there is a missing value on the first position
            if np.isnan(time_series[0]):
                if sub_region in sub_region_vals[start_year].keys():
                    time_series[0] = sub_region_vals[start_year][sub_region]
                elif region in region_vals[start_year].keys():
                    time_series[0] = region_vals[start_year][region]
                else:
                    time_series[0] = global_vals[start_year]
            
            # We check if there is a missing value on the last position
            if np.isnan(time_series[end_year-start_year]):
                if sub_region in sub_region_vals[end_year].keys():
                    time_series[end_year-start_year] = sub_region_vals[end_year][sub_region]
                elif region in region_vals[end_year].keys():
                    time_series[end_year-start_year] = region_vals[end_year][region]
                else:
                    time_series[end_year-start_year] = global_vals[end_year]
            
            # We finally interpolate the remaining missing values
            time_series = pd.Series(time_series).interpolate()
            
        # We add the new rows to target_df
        for year in range(start_year, end_year + 1):
            new_row = {'Location': location, 'Drug': drug_name_change[drug], 'Prevalence': time_series[year-start_year]}
            target_df[year] = target_df[year].append(new_row, ignore_index=True)
            
def get_prevalence_values(df_prev, countries_list = None, sub_regions_dict = None, regions_dict = None, 
                          start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_prev : pd.DataFrame
    target_df : dict of pd.DataFrames
    start_year : int
    end_year : int
    Returns
    -------
    None; populates the output container with prevalence levels for the given period for all locations.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
    
    # Create output_df
    output_df = create_output_df()
    
    # If no locations list is provided, then use get_locations()
    if countries_list is None:
        locations = get_locations(df_prev)
    else:
        # Make copies of location containers
        locations = countries_list.copy()
        sub_region_dict = sub_regions_dict.copy()
        region_dict = regions_dict.copy()
        
        # Adjustment for United Kindom
        locations.remove('United Kingdom')
        
        locations.append('United Kingdom (England and Wales)')
        sub_region_dict['United Kingdom (England and Wales)'] = sub_region_dict['United Kingdom']
        region_dict['United Kingdom (England and Wales)'] = region_dict['United Kingdom']
        
        locations.append('United Kingdom (Northern Ireland)')
        sub_region_dict['United Kingdom (Northern Ireland)'] = sub_region_dict['United Kingdom']
        region_dict['United Kingdom (Northern Ireland)'] = region_dict['United Kingdom']
        
        locations.append('United Kingdom (Scotland)')
        sub_region_dict['United Kingdom (Scotland)'] = sub_region_dict['United Kingdom']
        region_dict['United Kingdom (Scotland)'] = region_dict['United Kingdom']
    
    # Iterate over all locations and obtain local prevalence levels
    for location in locations:
        get_location_values(location, df_prev, output_df, sub_region_dict = sub_region_dict, region_dict = region_dict, start_year = start_year, end_year = end_year)
    
    # Special adjustment for the UK which is currently separated into England & Wales, Northern Ireland, and Scotland
    for year in range(start_year, end_year + 1):
        for drug in get_drug_types():
            # Extract the rows corresponding to the three locations and the given drug
            df_temp = output_df[year][((output_df[year]['Location'] == 'United Kingdom (England and Wales)') | (output_df[year]['Location'] == 'United Kingdom (Northern Ireland)') | (output_df[year]['Location'] == 'United Kingdom (Scotland)')) & (output_df[year]['Drug'] == drug_name_change[drug])]
            
            # Take the average prevalence across the three locations
            avg_prev = df_temp['Prevalence'].mean()
            
            # Add the average prevalence to the dataframe
            new_row = {'Location': 'United Kingdom', 'Drug': drug_name_change[drug], 'Prevalence': avg_prev}
            output_df[year] = output_df[year].append(new_row, ignore_index=True)
        
        # Remove the rows corresponding to the three locations
        output_df[year] = output_df[year][(output_df[year]['Location'] != 'United Kingdom (England and Wales)') & (output_df[year]['Location'] != 'United Kingdom (Northern Ireland)') & (output_df[year]['Location'] != 'United Kingdom (Scotland)')]
        
        # Finally reindex the dataframe
        output_df[year] = output_df[year].reset_index(drop = True)
        
    # Return output_df
    return output_df

def write_to_xlsx(output, target_file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/Prevalence.xlsx'):
    '''
    Parameters
    ----------
    output : dict of pd.DataFrame obejcts
    target_file : str
        The default is 'Prevalence.xlsx'.
    Returns
    -------
    None; Writes the ouput to the file, creating an .xlsx document with one spreadsheet corresponding to each year.

    '''
    with pd.ExcelWriter(target_file) as writer:  
        for year in output.keys():
            output[year].to_excel(writer, sheet_name = str(year))
