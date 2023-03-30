import pandas as pd
from sklearn.decomposition import PCA

def removeNaNs(df:pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].isna().any():
            df = df.drop(col, axis=1)
    return df

def remove_monotonically_increasing_rows(df_list:list) -> list:
    x:pd.DataFrame
    returnlist = []
    for x in df_list:
        dropme = []
        for column in x.columns:
            if x[column].is_monotonic_increasing or x[column].is_monotonic_decreasing:
                dropme.append(column)
        returnlist.append(x.drop(dropme,axis=1))
    return returnlist

def remove_monotonic_rows(df_list:list) -> list:
    x:pd.DataFrame
    returnlist = []
    for x in df_list:
        row_count = x.apply(pd.Series.nunique, axis=1)
        returnlist.append(x[row_count > 1])
    return returnlist

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

def make_datetime_index(timestamps:list) -> pd.DatetimeIndex:
    beginning = timestamps[0]
    end = timestamps[-1]
    beginning, end = pd.to_datetime((beginning,end), unit="s")
    index = pd.date_range(start=beginning, end=end, periods=len(timestamps))
    return index

def readcsv_modified(csv_loc:str) ->pd.DataFrame:
    csv:pd.DataFrame
    try:
        csv = pd.read_csv(csv_loc, skip_blank_lines=True)   
    except pd.errors.ParserError:
        return
    except pd.errors.EmptyDataError:
        print(csv_loc)
        return
    metrics = csv["identifier"].to_list()
    timestamps = csv.columns[1:].to_flat_index()
    timestamps = timestamps.to_numpy().tolist()
    timestamps = make_datetime_index(timestamps)
   # index = pd.MultiIndex.from_product([[num], timestamps], names=['instances','timepoints'])
    vals = csv.drop(labels="identifier",axis=1).to_numpy().transpose()
    s = pd.DataFrame(vals, index=timestamps, columns=metrics)
    return s

def readcsvs(csv_loc_list:list, remove_monotonic_increasing=True, remove_nans=True,remove_unique_cols=True, pca_components=0):
    individual_dataframes = []
    for i in range(len(csv_loc_list)):
        df = readcsv_modified(csv_loc_list[i])
        #The read_csv pandas function sometimes fails when something went wrong with the metric collection from prometheus. These are simply skipped without throwing errors
        if df is not None:
            individual_dataframes.append(df) #time series

    if pca_components != 0:
        pca_scaler = PCA(n_components = pca_components)
        concated_for_pca = pd.concat(individual_dataframes)
        scaled = pca_scaler.fit_transform(concated_for_pca)
        print(scaled)


        
    return

    if remove_monotonic_increasing:
        individual_dataframes = remove_monotonically_increasing_rows(individual_dataframes)
    #Here: Go through the loop once again, start trimming. compare everything to element at 0, trim with it so it stays as the leanest version.

    if remove_nans:
        removed_nans = []
        for frame in individual_dataframes:
            removed_nans.append(removeNaNs(frame))
        individual_dataframes = removed_nans

    if remove_unique_cols:
        individual_dataframes = removeUniqueColumns2(individual_dataframes)
    concated = pd.concat(individual_dataframes, keys=[f'csv {i}' for i in range(1, len(individual_dataframes)+1)])


    return concated

from get_all_metrics_with_tags import get_all_metrics_with_tags
readcsvs(get_all_metrics_with_tags(r"F:\Master\Kubernetes\sockshop\microservices-demo\query\automated\generated_csvs_4")[0], pca_components=100)
