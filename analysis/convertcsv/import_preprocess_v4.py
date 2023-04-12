import pandas as pd
#from sklearn.decomposition import PCA
from sktime.datatypes import convert_to
from sklearn.impute import KNNImputer

def _removeNaNs(df:pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].isna().any():
            df = df.drop(col, axis=1)
    return df

def _remove_monotonically_increasing_rows(df_list:list) -> list:
    x:pd.DataFrame
    returnlist = []
    for x in df_list:
        dropme = []
        for column in x.columns:
            if x[column].is_monotonic_increasing or x[column].is_monotonic_decreasing:
                dropme.append(column)
        returnlist.append(x.drop(dropme,axis=1))
    return returnlist

def _removeUniqueColumns2(frames:list) -> list:
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

def _make_datetime_index(timestamps:list) -> pd.DatetimeIndex:
    beginning = timestamps[0]
    end = timestamps[-1]
    beginning, end = pd.to_datetime((beginning,end), unit="s")
    index = pd.date_range(start=beginning, end=end, periods=len(timestamps))
    return index

def _readcsv_modified(csv_loc:str) ->pd.DataFrame:
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
    timestamps = _make_datetime_index(timestamps)
   # index = pd.MultiIndex.from_product([[num], timestamps], names=['instances','timepoints'])
    vals = csv.drop(labels="identifier",axis=1).to_numpy().transpose()
    s = pd.DataFrame(vals, index=timestamps, columns=metrics)
    return s

def _reduce_NaNs_treshold(df:pd.DataFrame, treshold:int):
    #Calculate the percent of NaNs in each columns (corresponds to feature in the time series)
    length = len(df)
    nan_counts = df.isna().sum()
    nan_percentages = (nan_counts / length) * 100
    #Put it neatly into a dataframe 
    percentdf = pd.DataFrame({'Column':nan_percentages.index,'nan_percent':nan_percentages.values })
    #Create a boolean mask that corresponds to NaN percent being under the treshold (True=good)
    removal_mask = percentdf["nan_percent"] < treshold
    #trim the dataframe to only include only truthy values
    percentdf = percentdf.loc[removal_mask]
    #Get the names of the columns that pass
    okay_cols = percentdf["Column"]
    #Return a trimmed dataframe with only the listed columns
    return df[okay_cols]

def readcsvs(csv_loc_list:list, remove_monotonic_increasing=True, reduce_NaNs_treshold=70, remove_unique_cols=True, pca_components=0):
    individual_dataframes = []
    for i in range(len(csv_loc_list)):
        df = _readcsv_modified(csv_loc_list[i])
        #The read_csv pandas function sometimes fails when something went wrong with the metric collection from prometheus. These are simply skipped without throwing errors
        if df is not None:
            individual_dataframes.append(df) #time series

    # if pca_components != 0:
    #     pca_scaler = PCA(n_components = pca_components)
    #     concated_for_pca = pd.concat(individual_dataframes)
    #     scaled = pca_scaler.fit_transform(concated_for_pca)
    #     print(scaled)

    if remove_monotonic_increasing:
        individual_dataframes = _remove_monotonically_increasing_rows(individual_dataframes)
    #Here: Go through the loop once again, start trimming. compare everything to element at 0, trim with it so it stays as the leanest version.

    if remove_unique_cols:
        individual_dataframes = _removeUniqueColumns2(individual_dataframes)

    concated = convert_to(individual_dataframes,to_type='pd-multiindex' )
    #NaNs can appear when concating dfs so this is done after the conversion to multiindex df
    if reduce_NaNs_treshold:
        concated = _reduce_NaNs_treshold(concated, reduce_NaNs_treshold)

    return concated
