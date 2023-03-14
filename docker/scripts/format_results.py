#!/usr/bin/env python3
import os
import sys
import argparse
import json
import numpy as np
from glob import glob
import pandas as pd
import json
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


def get_itu(path_chunks):

    chunk_files = ls(path_chunks+"/*")
    mean_chunk = []

    for chunk in chunk_files:

        with open(chunk) as f:
            data = json.load(f)
        mos = list(list(data.items())[0][1]['video'].items())[0][1]

        mean_chunk.append(np.mean(mos))

    df = pd.DataFrame(mean_chunk, columns=['itu'])
    return df


def get_quality_metric(path_metric, ext):

    metric_files = ls(path_metric+"/*")
    metric_files = sorted(metric_files)
    df = pd.DataFrame()
    df_chunk = pd.DataFrame()

    if len(metric_files) == 1 and 'itu' in metric_files[0]:
       
        df_itu = get_itu(metric_files[0])
        index = list(range(1, len(df_itu)+1, 1))
        df_itu.insert(loc=0, column='chunk', value=index)
        df_itu.set_index('chunk', inplace=True)
        printFile(df_itu, ext, "itu")

    else:
        for metric in metric_files:
            name_metric = os.path.basename(metric)

            if name_metric == "itu":
                df_itu = get_itu(metric)
                index = list(range(1, len(df_itu)+1, 1))
                df_itu.insert(loc=0, column='chunk', value=index)
                df_itu.set_index('chunk', inplace=True)
                printFile(df_itu, ext, "itu")

            else:
                df_chunk = pd.read_csv(metric+"/chunks.csv")
                df = pd.concat([df, df_chunk[name_metric]], axis=1)

        index = list(range(1, len(df)+1, 1))
        df.insert(loc=0, column='chunk', value=index)
        df.set_index('chunk', inplace=True)

        printFile(df, ext, "vqm")


def printFile(df, ext, name):

    if name == "vqm":
        if ext == "json":
            df.to_json(path_metric+"/vqmcli_results.json", index=True)
        elif ext == "csv":
            df.to_csv(path_metric+"/vqmcli_results.csv",
                      encoding='utf-8', index=True)
        else:
            df.to_xml(path_metric+"/vqmcli_results.xml")
    else:
        if ext == "json":
            df.to_json(path_metric+"/vqmcli_itu.json", index=True)
        elif ext == "csv":
            df.to_csv(path_metric+"/vqmcli_itu.csv",
                      encoding='utf-8', index=True)
        else:
            df.to_xml(path_metric+"/vqmcli_itu.xml")


if __name__ == "__main__":

    path_metric, ext = readArgs()
    if path_metric is None:
        print('Error to read path')
    else:
        get_quality_metric(path_metric, ext)
