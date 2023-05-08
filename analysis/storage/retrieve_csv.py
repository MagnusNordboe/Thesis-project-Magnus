import pandas as pd
import json
import numpy as np
import os

def retrieve_csv(name:str="Current_best") -> tuple:
    filepath = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(filepath + "/" + name + ".csv", index_col=[0,1])
    yfile = open(filepath + "/" + name + ".json", mode="r")
    y = json.load(yfile)
    return df, y