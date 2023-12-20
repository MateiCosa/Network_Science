import networkx as nx

import torch
import torch.nn.functional as F

import torch_geometric.nn as pyg_nn
from torch_geometric.utils import train_test_split_edges
from torch_geometric.utils.convert import from_networkx

import utils
from models import GAE_Encoder, VGAE_Encoder

import warnings
warnings.filterwarnings('ignore')

import importlib
importlib.reload(utils)

def train(epoch, model, optimizer, x, train_pos_edge_index):
    model.train()
    optimizer.zero_grad()
    z = model.encode(x, train_pos_edge_index)
    loss = model.recon_loss(z, train_pos_edge_index)
    loss.backward()
    optimizer.step()
    return loss.item()

def test(model, x, train_pos_edge_index, pos_edge_index, neg_edge_index):
    model.eval()
    with torch.no_grad():
        z = model.encode(x, train_pos_edge_index)
    return model.test(z, pos_edge_index, neg_edge_index)

def train_test_model(pyg_model, encoder, dataset_path, args, verbose = False):
    
    # Get srings for reporting
    model_name, drug, period = utils.get_model_info(pyg_model, dataset_path)

    # Initialize a model logger
    logger = utils.get_model_logger(drug, period, model_name)
    
    # Read data from file and covert to pyg dataset
    G = nx.read_gml(dataset_path)
    data = from_networkx(G)

    # Important: Normalize the features by row
    data.x = F.normalize(data.x, dim = 0)

    # Set the parameters
    channels = args['hidden1_dim']
    dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Encoder written by us; decoder is the default one (inner product)
    model = pyg_model(encoder(data.num_features, channels)).to(dev)
    data.train_mask = data.val_mask = data.test_mask = data.y = None
    data = train_test_split_edges(data)
    x, train_pos_edge_index = data.x.to(dev), data.train_pos_edge_index.to(dev)
    optimizer = torch.optim.Adam(model.parameters(), lr = args['learning_rate'])
    num_epochs = args['num_epochs']

    if verbose:
        print(f'Began training {model_name} on {drug} ({period})...')

    for epoch in range(0, num_epochs):
        train_loss = train(epoch, model, optimizer, x, train_pos_edge_index)
        auc, ap = test(model, x, train_pos_edge_index, data.test_pos_edge_index, data.test_neg_edge_index)
        utils.add_to_model_logger(logger, drug, period, model_name, train_loss, auc, ap)

        if verbose:
            print('Epoch: {}, train loss: {:.4f}, AUC: {:.4f}, AP: {:.4f}'.format(epoch, train_loss, auc, ap))
    
    if verbose:
        print(f"Training and testing complete. Best AUC: {max(logger[drug][period][model_name]['test']['AUC'])}")
    
    return model, logger

def train_test_all_models(args, verbose = False):

    # Get the log path
    log_to = args['log_to']

    # Obtain the list of dataset files to train on
    path_list = utils.get_path_list(args['data_path'])

    # Initiliaze the master logger and the dict of models
    master_logger = dict()
    model_dict = dict()

    if verbose:
        print('CUDA availability:', torch.cuda.is_available())
        print('Start loop over all datasets...')

    # Iterate over all datasets
    for file in path_list:
        # GAE model
        model, logger = train_test_model(pyg_model = pyg_nn.GAE, encoder = GAE_Encoder, dataset_path = file, args = args, verbose = verbose)
        drug, period, model_name = utils.get_model_info_from_logger(logger)
        utils.merge_nested_dicts(master_logger, logger)
        utils.add_to_model_dict(model_dict, drug, period, model_name, model)

        # VGAE model
        model, logger = train_test_model(pyg_model = pyg_nn.VGAE, encoder = VGAE_Encoder, dataset_path = file, args = args, verbose = verbose)
        drug, period, model_name = utils.get_model_info_from_logger(logger)
        utils.merge_nested_dicts(master_logger, logger)
        utils.add_to_model_dict(model_dict, drug, period, model_name, model)
    
    if verbose:
        print('Loop completed.')
        print('Logging to file...')
    
    # Dump log to json
    utils.dump_to_json(master_logger, log_to)

    if verbose:
        print('Logging completed.')

    # Return the models
    return model_dict