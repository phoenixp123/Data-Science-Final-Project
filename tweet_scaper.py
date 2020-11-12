import tweepy
import json
import csv
import pandas as pd
import numpy as np
from google.cloud import language
from google.cloud.language import types
from google.cloud.language import enums
import requests
from bs4 import BeautifulSoup
from collections import Counter,defaultdict
import matplotlib.pyplot as plt

consumer_key = "OROBANkVOsvva9HETWL4Kovbx"
consumer_secret = "t87379Kk9ANccJDM5a6E6G5eLKDGLnL7s2zld1kXvUCYu9gjnJ"
access_token = "1305689531421786112-FNe1D2tjmvFjzikZYHDyjvRVAVT9gk"
access_token_secret = "G6KV4pfTg6l7BSXxbQZDyYbREmr2taNkYzBzSZZfDyBIa"

# instantiate a client
client = language.LanguageServiceClient.from_service_account_json \
    ("/Users/phoenix/Downloads/My First Project-4361e522b85a.json")

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit = True)

class TweetScraper():
    def __init__(self, ):
        


def read_csv(filename):
    df = pd.read_csv(filename,usecols = ["countries","region","hf_score","hf_rank","hf_quartile",
                                         "pf_expression","pf_association_assembly","pf_movement"],na_values = ["-"])

    df.loc[:,"hf_score":"pf_movement"] = df.loc[:,"hf_score":"pf_movement"].astype(float)

    aggregation_functions = {"region": "first","hf_score": "mean","hf_rank": "max","hf_quartile": "max",
                             "pf_expression": "mean","pf_association_assembly": "mean","pf_movement": "mean"}

    df_aggregate = df.groupby(by = ["countries"]).aggregate(aggregation_functions)

    return df, df_aggregate


def eda_visualizations(dataframe):
    dataframe = dataframe.sort_values(by = "hf_score",ascending = False)

    plt.figure(figsize = (20,6))
    plt.bar(x = dataframe["region"],height = dataframe["hf_score"], label= "Average HFI Score")
    # plt.plot(dataframe["region"],dataframe["hf_rank"], label = "HFI Rank")

    plt.ylabel("Average HFI Score")
    plt.xlabel("Region")

    plt.legend()
    plt.show()


if __name__ == "__main__":
    df, df_aggregate = read_csv("hfi_cc_2019.csv")
    print(df_aggregate)
    eda_visualizations(df_aggregate)
