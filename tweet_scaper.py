import tweepy
import math

import pandas as pd
import numpy as np
from google.cloud import language
from google.cloud.language import types
from google.cloud.language import enums
# from collections import Counter,defaultdict
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



# Data Collection &  Processing
# ---------------------------------------------------------------------------------------------------------------------

def get_coordinates(filename):
    lat_long = pd.read_csv(filename,usecols = ["latitude","longitude","country"])
    lat_long["country"] = lat_long["country"].astype(str).apply(lambda s: s.strip())
    lat_long = lat_long[["country","latitude","longitude"]]
    lat_long = lat_long.sort_values(by = "country")

    radius = pd.read_csv("countries of the world.csv",usecols = ["Country","Area (sq. mi.)"])
    radius["Country"] = radius["Country"].astype(str).apply(lambda s: s.strip())
    radius["Area (sq. mi.)"] = radius["Area (sq. mi.)"].astype(float).apply(lambda x: math.sqrt(x))
    radius.columns = ["country","area"]
        

    coordinates = pd.merge(lat_long,radius,on = ["country"])

    return coordinates


def read_csv_hfi(filename):
    df = pd.read_csv(filename,usecols = ["countries","region","hf_score","hf_rank","hf_quartile",
                                         "pf_expression","pf_association_assembly","pf_movement"],na_values = ["-"])

    df.loc[:,"hf_score":"pf_movement"] = df.loc[:,"hf_score":"pf_movement"].astype(float)

    aggregation_functions = {"region": "first","hf_score": "mean","hf_rank": "max","hf_quartile": "max",
                             "pf_expression": "mean","pf_association_assembly": "mean","pf_movement": "mean"}

    df_aggregate = df.groupby(by = ["countries"]).aggregate(aggregation_functions)

    return df,df_aggregate


# Twitter Interaction and Feature Extraction
# ---------------------------------------------------------------------------------------------------------------------

# get_tweet(max = 100, location = api.geosearch(df["lat].....df["area"])
# return tweets


# Visualizations
# ---------------------------------------------------------------------------------------------------------------------

def visualizations(dataframe):
    dataframe = dataframe.sort_values(by = "hf_score",ascending = False)

    plt.figure(figsize = (20,6))
    plt.bar(x = dataframe["region"],height = dataframe["hf_score"],label = "Average HFI Score")

    plt.ylabel("Average HFI Score")
    plt.xlabel("Region")

    plt.legend()
    plt.show()

# Machine Learning and Sentiment Analysis
# ---------------------------------------------------------------------------------------------------------------------

# Final Report and Presentation
# ---------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    df,df_aggregates = read_csv_hfi("hfi_cc_2019.csv")
    df_coordinates = get_coordinates("lat_long_coordinates.csv")
    # visualizations(df_aggregates)
    print(df_coordinates)
