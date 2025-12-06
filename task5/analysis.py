import pandas as pd
from outliers import smirnov_grubbs

class MineStatsAnalyzer:
    def __init__(self, df:pd.DataFrame):
        self.df = df.copy()
        self.mines = []
        for col in df.columns:
            if col != 'Date':
                self.mines.append(col)

    def get_all_mines(self):
        return self.mines

    def _aggregate_outliers(self, function_per_mine, mine:str, *args, **kwargs):
        if mine is not None:
            return function_per_mine(mine, *args, **kwargs)
        else:
            outliers = []
            for m in self.mines:
                outliers.append(function_per_mine(m, *args, **kwargs))
            return pd.concat(outliers).reset_index(drop=True)

    def get_descriptive_statistics(self, mine:str=None):
        if mine is not None:
            data = self.df[mine]
        else:
            data = self.df[self.mines]
        stats = data.describe().transpose()
        stats['iqr'] = stats['75%'] - stats['25%']
        stats['median'] = stats['50%']
        return stats[['mean','std','median','iqr']]
    
    # ---- IQR ----
    def _iqr_outliers_for_mine(self, mine:str, bound_modifier:float):
        q1 = self.df[mine].quantile(0.25)
        q3 = self.df[mine].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - bound_modifier * iqr
        upper_bound = q3 + bound_modifier * iqr
        outliers = self.df[(self.df[mine] < lower_bound) | (self.df[mine] > upper_bound)].copy()
        outliers['Mine'] = mine
        return outliers

    def get_outliers_IQR(self, mine=None, bound_modifier=1.5):
        return self._aggregate_outliers(self._iqr_outliers_for_mine, mine, bound_modifier)
    
    # ---- z-score ----
    def _zscore_outliers_for_mine(self, mine:str, treshold:float):
        mean = self.df[mine].mean()
        std = self.df[mine].std()
        z = abs((self.df[mine] - mean) / std)
        outliers = self.df[z > treshold].copy()
        outliers['Mine'] = mine
        return outliers
    
    def get_outliers_zscore(self, mine=None, treshold=2):
        return self._aggregate_outliers(self._zscore_outliers_for_mine, mine, treshold)

    # ---- distance from MA ----
    def _ma_outliers_for_mine(self, mine:str, window:int, distance_percent_treshold:float):
        mine_data = self.df[mine]
        moving_avarage = mine_data.rolling(window).mean()
        distance_percent = (abs(mine_data - moving_avarage)) / moving_avarage
        outliers = self.df[distance_percent > distance_percent_treshold].copy()
        outliers['Mine'] = mine
        return outliers
    
    def get_outliers_moving_avarage(self, mine=None, window:int=7, distance_percent_treshold:float=0.15):
        return self._aggregate_outliers(self._ma_outliers_for_mine, mine, window, distance_percent_treshold)
    
    # ---- grubbs test ----
    def _grubbs_test_for_mine(self, mine:str, alpha:float, side:str):
        mine_data = self.df[mine].copy()
        values = mine_data.to_numpy()
        idx = mine_data.index

        if side == 'max':
            outliers_idx = smirnov_grubbs.max_test_indices(values, alpha)
        elif side == 'min':
            outliers_idx = smirnov_grubbs.min_test_indices(values, alpha)
        elif side == 'both':
            outliers_idx = sorted(set(
                smirnov_grubbs.max_test_indices(values, alpha) +
                smirnov_grubbs.min_test_indices(values, alpha)
            ))
        else:
            raise ValueError('side must be: min, max or both')
        out_idx = idx[outliers_idx]
        outliers = self.df.loc[out_idx]
        outliers['Mine'] = mine
        return outliers
    
    def get_outliers_grubbs(self, mine=None, alpha:float=0.05, side:str='both'):
        return self._aggregate_outliers(self._grubbs_test_for_mine, mine, alpha, side)

    def get_all_outliers_by_method(self, iqr_params:dict, z_params:dict, ma_params:dict, grubbs_params:dict):
        out_iqr = self.get_outliers_IQR(mine=None, **iqr_params)
        out_z = self.get_outliers_zscore(mine=None, **z_params)
        out_ma = self.get_outliers_moving_avarage(mine=None, **ma_params)
        out_grubbs = self.get_outliers_grubbs(mine=None, **grubbs_params)
        return {
            'IQR':out_iqr,
            'Z-score':out_z,
            'Moving avarage distance':out_ma,
            'Grubbs Test':out_grubbs
        }
