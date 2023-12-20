import os   
import json
import datetime 

def get_path_list(base_path):
    '''
    Parameters
    ----------
    base_path : str
    Returns
    -------
    path_list : list
    Produces a list of all files within the base directory.
    '''

    path_list = []
    for file in sorted(os.listdir(base_path)):
        path_list.append(base_path + '/' + str(file))
    return path_list

def get_model_logger(drug, period, model_name):
    '''
    Parameters
    ----------
    drug : str
    period : str
    model_name : str
    Returns
    -------
    logger : dict
    Produces a logger skeleton in the form of a nested dict.
    '''

    logger = dict()
    logger[drug] = dict()
    logger[drug][period] = dict()
    logger[drug][period][model_name] = dict()
    logger[drug][period][model_name]['train'] = dict()
    logger[drug][period][model_name]['test'] = dict()
    logger[drug][period][model_name]['train']['loss'] = []
    logger[drug][period][model_name]['test']['AUC'] = []
    logger[drug][period][model_name]['test']['AP'] = []
    return logger

def add_to_model_logger(logger, drug, period, model_name, train_loss, auc, ap):
    '''
    Parameters
    ----------
    logger : dict 
    drug : str
    period : str
    model_name : str
    train_loss : str
    auc : str
    ap : str
    Returns
    -------
    None
    Adds model training and test metrics to logger for one epoch.
    '''

    logger[drug][period][model_name]['train']['loss'].append(train_loss)
    logger[drug][period][model_name]['test']['AUC'].append(auc)
    logger[drug][period][model_name]['test']['AP'].append(ap)

def get_model_info(pyg_model, dataset_path):
    '''
    Parameters
    ----------
    pyg_model : pyg_nn
    dataset_path : str
    Returns
    -------
    (model_name, drug, period) : tuple
    Retrieves information about the drug, period, and model type.
    '''
    model_name = str(pyg_model).split(".")[-1][:-2]
    drug = dataset_path.split("/")[-1].split('_')[0]
    period = 'aggregate' if 'aggregate' in dataset_path.split("/")[-1].split('_') else dataset_path.split("/")[-1].split('_')[1].split('.')[0]
    return model_name, drug, period

def get_model_info_from_logger(logger):
    '''
    Parameters
    ----------
    logger : dict
    Returns
    -------
    (drug, period, model_name) : tuple
    Retrieves information about the drug, period, and model type from logger.
    '''
    drug = list(logger.keys())[0]
    period = list(logger[drug].keys())[0]
    model_name = list(logger[drug][period].keys())[0]
    return drug, period, model_name

def merge_nested_dicts(d1, d2):
    '''
    Parameters
    ----------
    d1 : dict
    d2 : dict
    Returns
    -------
    None
    Deep-merges two nested dictionaries.
    '''
    for key, value in d2.items():
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            merge_nested_dicts(d1[key], value)
        else:
            d1[key] = value

def add_to_model_dict(model_dict, drug, period, model_name, model):
    '''
    Parameters
    ----------
    model_dict : dict
    drug : str
    period : str
    model_name : str
    model : pyg_nn
    Returns
    -------
    None
    Adds a model to model_dict.
    '''
    if drug not in model_dict.keys(): 
        model_dict[drug] = {period: {}}
    if period not in model_dict[drug].keys():
        model_dict[drug][period] = {model_name: {}}
    if model_name not in model_dict[drug][period].keys():
        model_dict[drug][period][model_name] = model
    model_dict[drug][period][model_name] = model

def dump_to_json(master_logger, log_to):
    '''
    Parameters
    ----------
    master_logger : dict
    log_to : str
    Returns
    -------
    None
    Dumps the master_logger to a .json file.
    '''
    with open(log_to + '/' + datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + '.json', 'w') as log_file:
        json.dump(master_logger, log_file)