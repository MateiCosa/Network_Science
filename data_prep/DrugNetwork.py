import numpy as np
import pandas as pd
import networkx as nx

class DrugNetwork():
    
    def __init__(self, structure, start_year = 2006, end_year = 2017):
        self.structure = structure
        self.start_year = start_year
        self.end_year = end_year
        
    def _aggregate(self):
        pass
    
    def summary_statistics(self):
        stats = pd.DataFrame(columns = ['Year', 'Countries', 'Connections'])
        for year in range(self.start_year, self.end_year + 1):
            stats = stats.append({'Year': year, 'Countries': len(self.structure[year].nodes), 'Connections': len(self.structure[year].edges)}, ignore_index = True)
        return stats