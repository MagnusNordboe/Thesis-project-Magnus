import pandas as pd
import json
import numpy as np
import os

def store_csv(df:pd.DataFrame, y, name:str="Current_best") -> None:
    filepath = os.path.dirname(os.path.abspath(__file__))
    df.to_csv(filepath + "/" + name + ".csv")
    yfile = open(filepath + "/" + name + ".json", mode="w")
    if type(y) == np.ndarray:
        y = y.tolist()
    json.dump(y,fp=yfile)
    return repr(filepath)

