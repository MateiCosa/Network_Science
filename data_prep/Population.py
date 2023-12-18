
# Collection of functions for obtaining population data from the UN;
# The default period is 2006-2017;
# The default age group is 15-64;
# Source of data: UN data portal API.

import pandas as pd
import requests
import json

def get_location_ids(base_url = "https://population.un.org/dataportalapi/api/v1"):
    '''
    Parameters
    ----------
    base_url : string
        API url; The default is "https://population.un.org/dataportalapi/api/v1".
    Returns
    -------
    list of location ids
    '''
    # Creates the target URL, indicators, in this instance
    target = base_url + "/locations/"

    # Get the response, which includes the first page of data as well as information on pagination and number of records
    response = requests.get(target)

    # Converts call into JSON
    j = response.json()

    # Converts JSON into a pandas DataFrame.
    df = pd.json_normalize(j['data']) # pd.json_normalize flattens the JSON to accomodate nested lists within the JSON structure

    # Loop until there are new pages with data
    while j['nextPage'] != None:
        # Reset the target to the next page
        target = j['nextPage']

        #call the API for the next page
        response = requests.get(target)

        # Convert response to JSON format
        j = response.json()

        # Store the next page in a data frame
        df_temp = pd.json_normalize(j['data'])

        # Append next page to the data frame
        df = df.append(df_temp)
    
    return list(df['id'])

def create_output_df(start_year = 2006, end_year = 2017):
    '''
    Parameters
    ----------
    start_year : int
    end_year : int
    Returns
    -------
    pop_df : empty dataframe with year and population columns
    '''
    if start_year > end_year:
        raise Exception('Invalid years!')
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise Exception('Invalid years!')
        
    pop_df = dict()
    for i in range(start_year, end_year + 1):
        pop_df[i] = pd.DataFrame(columns=['Location', 'Population'])
    return pop_df

def get_location_population(location_id, target_df, start_year = 2006, end_year = 2017, 
                            age_min = 15, age_max = 64, 
                            base_url = "https://population.un.org/dataportalapi/api/v1"):
    '''
    Parameters
    ----------
    location_id : int
    target_df : pd.DataFrame
    start_year : int
    end_year : int
    age_min : int
    age_max : int
    base_url : string
        API url; The default is "https://population.un.org/dataportalapi/api/v1".
    Returns
    -------
    None; Updates the target_df with population values for the given location

    '''
    # Creates the target URL, indicators, in this instance
    target = base_url + "/data/indicators/46/locations/" + str(location_id) + "/start/" + str(start_year) + "/end/" + str(end_year)

    # Get the response, which includes the first page of data as well as information on pagination and number of records
    response = requests.get(target)
    
    # Check that the request was sucessful
    if response.status_code != 200:
        return

    # Converts call into JSON
    j = response.json()
    
    # Converts JSON into a pandas DataFrame.
    df = pd.json_normalize(j['data']) # pd.json_normalize flattens the JSON to accomodate nested lists within the JSON structure

    # Loop until there are new pages with data
    while j['nextPage'] != None:
        # Reset the target to the next page
        target = j['nextPage']

        #call the API for the next page
        response = requests.get(target)
        
        # Convert response to JSON format
        j = response.json()

        # Store the next page in a data frame
        df_temp = pd.json_normalize(j['data'])

        # Append next page to the data frame
        df = df.append(df_temp)
    
    # Extract data for the given age range and take the total for both sexes
    df = df[(df['ageStart'] >= age_min) & (df['ageStart'] <= age_max) & (df['sex'] == 'Both sexes')]
    
    # Get the total population for each year
    sum_by_year = df.groupby('timeLabel')['value'].sum()
    
    # Add the data to the target df
    for i, value in enumerate(sum_by_year):
        new_row = {'Location': df.iloc[0]['location'], 'Population': value}
        target_df[start_year+i] = target_df[start_year+i].append(new_row, ignore_index=True)
        
def get_population(start_year = 2006, end_year = 2017, 
                   age_min = 15, age_max = 64, 
                   base_url = "https://population.un.org/dataportalapi/api/v1", debug = False):
    '''
    Parameters
    ----------
    start_year : int
    end_year : int
    age_min : int
    age_max : int
    base_url : string
        API url; The default is "https://population.un.org/dataportalapi/api/v1".
    debug :   bool
        The default is False.
    Returns
    -------
    pop_df : pd.DataFrame
        Obtains the population data for all locations for the given period and age groups.
    '''
    # Obtain the location ids
    location_ids = get_location_ids(base_url = base_url)
    
    # Create the output container: dict of dataframes
    pop_df = create_output_df()
    
    # Iterate over the location_ids and add the data for each location
    for location_id in location_ids:
        get_location_population(location_id = location_id, target_df = pop_df, 
                                start_year = start_year, end_year = end_year, 
                                age_min = age_min, age_max = age_max,
                                base_url = base_url)
        if debug:
            print(location_id)
    
    # Return the output
    return pop_df

def write_to_xlsx(output, target_file = '/Users/mateicosa/Bocconi/BIDSA/Network_Science/data/sources/Population.xlsx'):
    '''
    Parameters
    ----------
    output : dict of pd.DataFrame obejcts
    target_file : str
        The default is 'Population.xlsx'.
    Returns
    -------
    None; Writes the ouput to the file, creating an .xlsx document with one spreadsheet corresponding to each year.

    '''
    with pd.ExcelWriter(target_file) as writer:  
        for year in output.keys():
            output[year].to_excel(writer, sheet_name = str(year))