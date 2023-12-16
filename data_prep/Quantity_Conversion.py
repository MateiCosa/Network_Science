
# Collection of functions for converting drug derivatives and different measurement units to pure generic drug quantities expressed in kilograms;
# The default period is 2006-2017;
# The drugs of interest are: cocaine, opioids, cannabis, amphetamines, and ecstasy;
# Sources of conversion factors: https://www.unodc.org/documents/data-and-analysis/WDR2010/WDR2010methodology.pdf ,
#                                https://wdr.unodc.org/wdr2019/prelaunch/WDR-2019-Methodology-FINAL.pdf


import numpy as np

# Generic conversion table
unit_to_kg = {
              'Kilogram': 1.0,
              'Gram': 0.001,
              'Pound': 0.453592,
              'Litre': 1,
              'Millilitre': 0.001,
              'Gallons (US, liquid)': 3.78541,
              'Ton': 1000,
              'Viss': 1.63293,
              'Picul': 60.478982,
              'Block (350gr)': 0.35,
              'other': 0,
              'unknown': 0,
              np.nan: 0
             }

def convert_cocaine(drug_type, q, unit):
    '''
    Parameters
    ----------
    q : float
       drug quantity
    drug_type : str
    unit : str
    Returns
    -------
    float
        Converts the quantity of drug to kg, taking into account different adjustment and conversion factors present in the literature.
    '''
    
    if drug_type == 'Cocaine' or 'Cocaine HCL' or 'Crack' or 'Coca paste':
        
        # Translate small doses of cocaine or equivalent derivatives to kilograms
        if unit == 'Tablet' or unit == 'Unit' or unit == 'Capsule':
            return q * 1e-4
        
        # Translate unit to kg
        return q * unit_to_kg[unit]
    
    if drug_type == 'Coca leaf':
        
        # Translate small doses of coca leafs to kilograms
        if unit == 'Unit':
            q *= 1e-4
            unit = 'Kilogram'
        
        # Translate unit to kg
        q *= unit_to_kg[unit]
        
        # Translate coca leaf to cocaine HCL
        return q / 220
    
    raise Exception('Unknown drug form for Cocaine: {drug_type}')
    

def convert_heroin(drug_type, q, unit):
    '''
    Parameters
    ----------
    q : float
       drug quantity
    drug_type : str
    unit : str
    Returns
    -------
    float
        Converts the quantity of drug to kg, taking into account different adjustment and conversion factors present in the literature.
    '''
    
    if drug_type == 'Heroin':
        
        # Translate small doses of heroin to kilograms
        if unit == 'Tablet' or unit == 'Unit' or unit == 'Ampoule' or unit == 'Piece' or unit == 'Capsule':
            return q * 3e-5
        
        # Translate unit to kg
        return q * unit_to_kg[unit]
    
    if drug_type == 'Opium' or drug_type == 'Opium Poppy' or drug_type == 'Poppy seeds':
        
        # Translate small doses of opium to kilograms
        if unit == 'Tablet' or unit == 'Unit' or unit == 'Ampoule' or unit == 'Piece' or unit == 'Capsule':
            q *= 0.0003
            unit = 'Kilogram'
        
        # Translate opium plants to hectars
        if unit == 'Plants':
            q *= 5.263157894736842e-06
            unit = 'Hectars'
        
        # Translate acres of opium to hectars
        if unit == 'Acres':
            q *= 0.404686
            unit = 'Hectars'
        
        # Translate hectars of opium to kg of opium
        if unit == 'Hectars' or unit == 'Hectar':
            q *= 42.4
            unit = 'Kilogram'
        
        # Translate unit to kg
        q *= unit_to_kg[unit]
        
        # Translate opium to heroin
        return q * 0.1
    
    if drug_type == 'Poppy straw':
        
        # Translate poppy straw plants to hectars
        if unit == 'Plants' or unit == 'Bush':
            q *= 5.263157894736842e-06
            unit = 'Hectars'
        
        # Translate acres of poppy straw to hectars
        if unit == 'Acres':
            q *= 0.404686
            unit = 'Hectars'
        
        # Translate hectars of poppy straw to kg of morphine
        if unit == 'Hectars' or unit == 'Hectar':
            q *= 411.1297071129707
            unit = 'Kilogram'
        
        # Translate unit to kg (morphine)
        q *= unit_to_kg[unit]
        
        # Translate kg of morphine to kg of heroin (assuming heroin is 3 times as potent as morphine)
        q /= 3 
        
        # Return the final quantity
        return q
    
    if drug_type == 'Morphine':
        
        # Translate small doses of morphine to kilograms
        if unit == 'Tablet' or unit == 'Unit' or unit == 'Ampoule' or unit == 'Dose' or unit == 'Vials' or unit == 'Injection' or unit == 'Bottles':
            q *= 1e-4
            unit = 'Kilogram'
        
        # Translate unit to kg, assuming 1:1 ratio
        q *= unit_to_kg[unit]
        
        # Return the final quantity
        return q
    
    raise Exception('Unknown drug form for Heroin: {drug_type}')

def convert_cannabis(drug_type, q, unit):
    '''
    Parameters
    ----------
    q : float
       drug quantity
    drug_type : str
    unit : str
    Returns
    -------
    float
        Converts the quantity of drug to kg, taking into account different adjustment and conversion factors present in the literature.
    '''
        
    # Translate small doses of cannabis to kilograms
    if unit == 'Tablet' or unit == 'Unit' or unit == 'Piece' or unit == 'Ampoule' or unit == 'Capsule' or unit == 'Dose' or unit == 'Vials' or unit == 'Injection' or unit == 'Bottles' or unit == 'Seed' or unit == 'Cigarette' or unit == 'Pill':
        q *= 0.0005
        unit = 'Kilogram'

    # Translate acres of cannabis to hectars
    if unit == 'Acres':
        q *= 0.404686
        unit = 'Hectars'

    # Translate hectars of cannabis to kg
    if unit == 'Hectars' or unit == 'Hectar':
        q *= 42.5 # Rough estimate for large range (15-70)
        unit = 'Kilogram'

    # Translate plants to kilograms of cannabis
    if unit == 'Plants' or unit == 'Bush':
        q *= 0.1 # asssuming the average weight of a plant is 100 grams
        # Translate plant weight to cannabis assuming only around 33% of the initial weight remains after drying
        q *= 0.33
        unit = 'Kilogram'

    # Translate unit to kg 
    q *= unit_to_kg[unit]

    # Return the quantity
    return q
    
    raise Exception('Unknown drug form for Cannabis: {drug_type}')
    
def convert_amphetamine(drug_type, q, unit):
    '''
    Parameters
    ----------
    q : float
       drug quantity
    drug_type : str
    unit : str
    Returns
    -------
    float
        Converts the quantity of drug to kg, taking into account different adjustment and conversion factors present in the literature.
    '''
        
    # Translate small doses of amphetamine to kilograms
    if unit == 'Tablet' or unit == 'Unit' or unit == 'Pill' or unit == 'Capsule':
        q *= 0.00025
        unit = 'Kilogram'
    
    # Translate hundred of units to kg
    if unit == 'Hundred of units':
        q *= 0.025
        unit = 'Kilogram'
    
    # Translate thousand of doses to kg
    if unit == 'Thousand of doses':
        q *= 0.25
        unit = 'Kilogram'
    
    # Translate unit to kg 
    q *= unit_to_kg[unit]
    
    # Return the quantity
    return q
    
def convert_ecstasy(drug_type, q, unit):
    '''
    Parameters
    ----------
    q : float
       drug quantity
    drug_type : str
    unit : str
    Returns
    -------
    float
        Converts the quantity of drug to kg, taking into account different adjustment and conversion factors present in the literature.
    '''
    
    # Translate small doses of amphetamine to kilograms
    if unit == 'Tablet' or unit == 'Unit' or unit == 'Pill' or unit == 'Capsule' or unit == 'Piece' or unit == 'Barette':
        q *= 0.00027
        unit = 'Kilogram'
        
    if unit == 'Thousand of tablets':
        q *= 0.27
        unit = 'Kilogram'
    
    # Translate unit to kg 
    q *= unit_to_kg[unit]
    
    # Return the quantity
    return q

def convert(drug_type, q, drug_form, unit):
    '''
    Parameters
    ----------
    drug_type : str
        'Cocaine', 'Heroin', 'Cannabis', 'Amphetamine', 'Ecstasy'
    q : float
        drug quantity
    drug_form : str
        specific variation of the drug
    unit : str
    Returns
    -------
    float
        Geeric function to convert the quantity of drug to kg, taking into account different adjustment and conversion factors present in the literature.
    '''
    
    #Call the respective conversion function
    
    if drug_type == 'Cocaine':
        return convert_cocaine(drug_form, q, unit)
    
    if drug_type == 'Heroin':
        return convert_heroin(drug_form, q, unit)
    
    if drug_type == 'Cannabis':
        return convert_cannabis(drug_form, q, unit)
    
    if drug_type == 'Amphetamine':
        return convert_amphetamine(drug_form, q, unit)
    
    if drug_type == 'Ecstasy':
        return convert_ecstasy(drug_form, q, unit)
    
    # Raise an exception is drug is not found
    raise Exception('Unknown drug type: {drug_type}')
