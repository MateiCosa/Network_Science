
# Collection of functions for obtaining drug purity levels from UNODC data
# The default period is 2006-2017;
# The drugs of interest are: cocaine, opioids, cannabis, amphetamines, and ecstasy
# Source of data: https://dataunodc.un.org/dp-drug-purity

import numpy as np
import pandas as pd

# Name conversion for convenience and compatibility
drug_name_change = {
                    'Cocaine-type': 'Cocaine',
                    'Opioids': 'Heroin',
                    'Cannabis-type': 'Cannabis',
                    'Amphetamine-type stimulants': 'Amphetamine',
                    '“Ecstasy”-type substances': 'Ecstasy'
                   }

def prepare_data(file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/Drug_Purities.xlsx'):
    '''
    Parameters
    ----------
    df_pure : pd.DataFrame
    Returns
    -------
    df_pure : pd.DataFrame
        Filters and pre-processes the dataframe according to several criteria.
    '''
    
    # Read the file to a pd.DataFrame
    df_pure = pd.read_excel(file)
    
    # We are interested in the typical purity in each country.
    # For all missing value, we impute either the average of the min and max values, where available;
    # or he min or the max value, where available.
    # Finally, we remove the remaining missing values.
    df_pure['Typical'] = df_pure['Typical'].fillna((df_pure['Minimum'] + df_pure['Maximum']) / 2)
    df_pure['Typical'] = df_pure['Typical'].fillna(df_pure['Minimum'])
    df_pure['Typical'] = df_pure['Typical'].fillna(df_pure['Maximum'])
    df_pure = df_pure[df_pure['Typical'].notna()]
    
    # Check that we are left with no missing values
    if df_pure['Typical'].isna().sum() != 0:
        raise Exception('Missing values remain!')
        
    # We are interested only in the values measured in percentages
    df_pure = df_pure[df_pure['Measurement'] == '% (percent)']
    
    # Some values are greater than one, so we divide them by 100 to ensure consistency of the results
    df_pure.loc[df_pure['Typical'] > 1, 'Typical'] /= 100
    
    # Check that all values are not greater than 1
    if (df_pure['Typical'] > 1).sum() != 0:
        raise Exception('Incosistent values remain!')
    
    # We are interested only in values at wholesale level
    df_pure = df_pure[df_pure['LevelOfSale'] == 'Wholesale']
    
    # Change labels to include all drugs in each category
    df_pure['DrugGroup'] = df_pure['DrugGroup'].replace('Cocaine-type drugs', 'Cocaine-type')
    df_pure['DrugGroup'] = df_pure['DrugGroup'].replace('Cannabis-type drugs', 'Cannabis-type')
    df_pure['DrugGroup'] = df_pure['DrugGroup'].replace('ATS', 'Amphetamine-type stimulants')
    
    return df_pure

def get_sub_region_avgs(df_pure, drug, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_pure : pd.DataFrame
    drug : str
    start_year : int
    end_year : int
    Returns
    -------
    output : dict of dicts
        Compute average purity levels at a sub-regional levels for a given drug and for a given period of time.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    if not (isinstance(drug, str) and drug in get_drug_types()):
        raise Exception('Invalid drug!')
        
    output = dict()
    for year in range(start_year, end_year + 1):
        output[year] = dict(df_pure[(df_pure['DrugGroup'] == drug) & (df_pure['Year'] == year)].groupby('SubRegion')['Typical'].mean())
    return output

def get_region_avgs(df_pure, drug, start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_pure : pd.DataFrame
    drug : str
    start_year : int
    end_year : int
    Returns
    -------
    output : dict of dicts
        Compute average purity levels at a regional levels for a given drug and for a given period of time.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    if not (isinstance(drug, str) and drug in get_drug_types()):
        raise Exception('Invalid drug!')
        
    output = dict()
    for year in range(start_year, end_year + 1):
        output[year] = dict(df_pure[(df_pure['DrugGroup'] == drug) & (df_pure['Year'] == year)].groupby('Region')['Typical'].mean())
    return output

def get_global_avgs(region_avgs):
    '''
    Parameters
    ----------
    region_avgs : dict of dicts
    Returns
    -------
    year_total : dict
        Computes global average purity levels for the period of time contained in region_avgs.
    '''
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

def get_drug_types():
    '''
    Returns
    -------
    output : list
        Retrieves the list of drugs we are interested in.
    '''
    output = ['“Ecstasy”-type substances',
              'Amphetamine-type stimulants',
              'Cocaine-type',
              'Opioids',
              'Cannabis-type']
    return output

def get_sub_region(location, df_pure):
    '''
    Parameters
    ----------
    location : str
    df_pure : pd.DataFrame
    Returns
    -------
    list
        Retrieves the sub-region the location belongs to.
    '''
    if not location in get_locations(df_pure):
        raise Exception('Invalid location!')
        
    return list(set(df_pure[df_pure['Country/Territory'] == location]['SubRegion']))[0]

def get_region(location, df_pure):
    '''
    Parameters
    ----------
    location : str
    df_pure : pd.DataFrame
    Returns
    -------
    list
        Retrieves the region the location belongs to.
    '''
    if not location in get_locations(df_pure):
        raise Exception('Invalid location!')
        
    return list(set(df_pure[df_pure['Country/Territory'] == location]['Region']))[0]

def create_output_df(start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    start_year : int
    end_year : int
    Returns
    -------
    pure_df : dict of pd.DataFrames
        Creates an empty dictionary of dataframes to store the final output.
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    pure_df = dict()
    for i in range(start_year, end_year + 1):
        pure_df[i] = pd.DataFrame(columns=['Location', 'Drug', 'Purity'])
    return pure_df

def get_location_values(location, df_pure, target_df, 
                        sub_region_dict = None, region_dict = None, 
                        start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    location : str
    df_pure : pd.DataFrame
    target_df : pd.DataFrame
    sub_region_dict : dict, optional
    region_dict : dict, optional
    start_year : int
    end_year : int
    Returns
    -------
    None; adds locations data to target_df
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    # Retrieve the list of drugs and the region & sub-region of the given location
    drug_types = get_drug_types()
    # If provided, we use the sub-region and region data
    if sub_region_dict is None:
        sub_region = get_sub_region(location, df_pure)
    else:
        sub_region = sub_region_dict[location]
        
    if region_dict is None:
        region = get_region(location, df_pure)
    else:
        region = region_dict[location]
            
    # Iterate over all drug types
    for drug in drug_types:
        # Retrieve regional and sub-regional values, as well as annual global averages to use for imputation
        sub_region_vals = get_sub_region_avgs(df_pure, drug)
        region_vals = get_region_avgs(df_pure, drug)
        global_vals = get_global_avgs(region_vals)
        
        # Prepare an empty vector to store the time-series
        time_series = np.zeros(end_year - start_year + 1)
        
        # Iterate over the given period of time
        for year in range(start_year, end_year + 1):
            #Extract data for the given location, drug, and year
            df_temp = df_pure[(df_pure['Country/Territory'] == location) & (df_pure['DrugGroup'] == drug) & (df_pure['Year'] == year)]
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
                time_series[year-start_year] = df_temp['Typical']
            # If multiple results are found
            else:
                time_series[year-start_year] = df_temp['Typical'].mean()
            
            new_row = {'Location': location, 'Drug': drug_name_change[drug], 'Purity': time_series[year-start_year]}
            target_df[year] = target_df[year].append(new_row, ignore_index=True)

def get_purity_values(df_pure, locations = None, sub_region_dict = None, region_dict = None, 
                      start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    df_pure : pd.DataFrame
    target_df : pd.DataFram
    locations : list of str, optional
    sub_region_dict : dict, optional
    region_dict : dict, optional
    start_year : int
    end_year : int
    Returns
    -------
    None; Populates target_df with purity values.

    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
    
    # Create output_df
    output_df = create_output_df()
    
    # If no locations list is provided, then use get_locations()
    if locations is None:
        locations = get_locations(df_pure)
    
    # Iterate over the locations
    for location in locations:
        get_location_values(location, df_pure, output_df, sub_region_dict = sub_region_dict, region_dict = region_dict, start_year = start_year, end_year = end_year)
        
    # Return output_df
    return output_df
    
def write_to_xlsx(output, target_file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/Purity.xlsx'):
    '''
    Parameters
    ----------
    output : dict of pd.DataFrame obejcts
    target_file : str
        The default is 'Purity.xlsx'.
    Returns
    -------
    None; Writes the ouput to the file, creating an .xlsx document with one spreadsheet corresponding to each year.

    '''
    with pd.ExcelWriter(target_file) as writer:  
        for year in output.keys():
            output[year].to_excel(writer, sheet_name = str(year))