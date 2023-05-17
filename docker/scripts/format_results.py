#!/usr/bin/env python3
import os
import sys
import argparse
import json
import numpy as np
from glob import glob
import pandas as pd
import xml


def readArgs():
    try:
        path_metric = sys.argv[1]
        ext = sys.argv[2]

        return path_metric, ext
    except:
        sys.stderr.write(
            "Error: Error in passing arguments. \n")
        sys.exit(1)


def ls(expr='*.*'):
    return glob(expr)


def get_quality_metric(path_metric, ext):

    metric_files = ls(path_metric+"/*")
    metric_files = sorted(metric_files)
    df = pd.DataFrame()
    df_chunk = pd.DataFrame()

    for metric in metric_files:
        name_metric = os.path.basename(metric)

   
        df_chunk = pd.read_csv(metric+"/chunks.csv")
        if "siti" in name_metric:
            df_chunk = df_chunk[['si', 'ti']].round(5) 
            df = pd.concat([df, df_chunk['si']], axis=1)
            df = pd.concat([df, df_chunk['ti']], axis=1)
        else:
            df = pd.concat([df, df_chunk[name_metric]], axis=1)

    index = list(range(1, len(df)+1, 1))
    df.insert(loc=0, column='chunk', value=index)
    df.set_index('chunk', inplace=True)

    printFile(df, ext)


def printFile(df, ext):

   if ext == "json":
       df.to_json(path_metric+"/vqmcli_results.json", index=True)
   elif ext == "csv":
       df.to_csv(path_metric+"/vqmcli_results.csv",
               encoding='utf-8', index=True)
   else:
       df.to_xml(path_metric+"/vqmcli_results.xml")


if __name__ == "__main__":

    path_metric, ext = readArgs()
    if path_metric is None:
        print('Error to read path')
    else:
        get_quality_metric(path_metric, ext)
