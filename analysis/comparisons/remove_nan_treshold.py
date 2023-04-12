#Abandoned
import pandas as pd
class remove_nan_treshold():
    remove_mask:pd.Series
    def __init__(self, treshold=70) -> None:
        self.treshold = treshold
    
    def fit(self, df:pd.DataFrame):
        length = len(df)
        nan_counts = df.isna().sum()
        nan_percentages = (nan_counts / length) * 100
        percentdf = pd.DataFrame({'Column':nan_percentages.index,'nan_percent':nan_percentages.values })
        self.remove_mask = percentdf["nan_percent"] < self.treshold
    
    def transform(self, df:pd.DataFrame):

        return
