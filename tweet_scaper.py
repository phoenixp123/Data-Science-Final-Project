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

consumer_key = "u3rjsE7Xz0Fj0EgP57g7NlXks"
consumer_secret = "qB8RrfFJ9mOusIdM4rTcStCjqKgDS8iAIWtNK4zCxtFSQOxCwY"
access_token = "1305689531421786112-v5mwJbrNRFYbbhS5Xf9N7e62oROcno"
access_token_secret = "vXsMk129W5FhQzQThGtnVJgLbRx7Op3UwQLGy2h6iyner"

# instantiate a client
client = language.LanguageServiceClient.from_service_account_json \
    ("/Users/phoenix/Downloads/My First Project-4361e522b85a.json")

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit = True)


def read_csv(filename):
    df = pd.read_csv(filename,usecols = ["countries","region","hf_score","hf_rank","hf_quartile",
                                         "pf_expression","pf_association_assembly","pf_movement"],na_values = ["-"])

    df.loc[:,"hf_score":"pf_movement"] = df.loc[:,"hf_score":"pf_movement"].astype(float)

    aggregation_functions = {"region": "first","hf_score": "mean","hf_rank": "max","hf_quartile": "max",
                             "pf_expression": "mean","pf_association_assembly": "mean","pf_movement": "mean"}

    df = df.groupby(by = ["countries"]).aggregate(aggregation_functions)

    return df


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
    df_byRegion = read_csv("hfi_cc_2019.csv")
    eda_visualizations(df_byRegion)
