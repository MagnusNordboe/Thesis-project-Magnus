import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
def get_nan_percents(df:pd.DataFrame):
    #Calculate the percent of NaNs in each columns (corresponds to feature in the time series)
    length = len(df)
    nan_counts = df.isna().sum()
    nan_percentages = (nan_counts / length) * 100
    percentdf = pd.DataFrame({'Column':nan_percentages.index,'nan_percent':nan_percentages.values })
    
    return percentdf #.sort_values(by='nan_percent').reset_index(drop=True)