import pandas as pd
import numpy as np
from get_all_metrics_with_tags import get_all_metrics_with_tags

def make_datetime_index(timestamps:list) -> pd.DatetimeIndex:
    beginning = timestamps[0]
    end = timestamps[-1]
    beginning, end = pd.to_datetime((beginning,end), unit="s")
    index = pd.date_range(start=beginning, end=end, periods=len(timestamps))
    return index

def readcsv_modified(csv_loc:str):
    csv = pd.read_csv(csv_loc)
    metrics = csv["identifier"].to_list()
    timestamps = csv.columns[1:].to_flat_index()
    timestamps = timestamps.to_numpy().tolist()
    timestamps = make_datetime_index(timestamps)
   # index = pd.MultiIndex.from_product([[num], timestamps], names=['instances','timepoints'])
    vals = csv.drop(labels="identifier",axis=1).to_numpy().transpose()
    s = pd.DataFrame(vals, index=timestamps, columns=metrics)
    return s

def removeNaNs(df:pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].isna().any():
            df = df.drop(col, axis=1)
    return df

def removeUniqueColumns2(frames:list) -> list:
    template:pd.DataFrame = frames[0]
    #Round 1: Reduces the first frame to be the smallest size to match with everyone
    for frame in frames[1:]:
        common_columns = template.columns.intersection(frame.columns)
        template = template.reindex(columns=common_columns)
    returnlist = [template]
    #Round 2: Reduces all the other ones to the same minimum
    for frame in frames[1:]:
        common_columns = template.columns.intersection(frame.columns)
        returnlist.append(frame.reindex(columns=common_columns))
    return returnlist

def create_df():
    '''Gets the complete df form generated_csvs_2 with y array
    :return: Complete df and labels
    :rtype: pd.DataFrame, List
    '''
    metrics, tags = get_all_metrics_with_tags(r"F:\Master\Kubernetes\sockshop\microservices-demo\query\automated\generated_csvs_2")
    individual_dataframes = []
    for i in metrics:
        individual_dataframes.append(readcsv_modified(i)) #time series
    
    removed_nans = []
    for frame in individual_dataframes:
        removed_nans.append(removeNaNs(frame))

    removed_unique_cols = removeUniqueColumns2(removed_nans)
    concated = pd.concat(removed_unique_cols, keys=[f'csv {i}' for i in range(1, len(removed_unique_cols)+1)])

    return concated.reindex(index=pd.MultiIndex.from_tuples([(idx, date) for idx, date in zip(concated.index.get_level_values(0), concated.index.get_level_values(1))], names=['files','times'])), tags
    
