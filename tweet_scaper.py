import math
import re
import pandas as pd
import numpy as np
import time
import tweepy
from googleapiclient.discovery import build
from google.cloud import language
from google.cloud.language import types
from google.cloud.language import enums
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------------------------------------------------------------------------------------------------------------

date = datetime.today().strftime('%Y-%m-%d')

# authorize tweepy
consumer_key = "OROBANkVOsvva9HETWL4Kovbx"
consumer_secret = "t87379Kk9ANccJDM5a6E6G5eLKDGLnL7s2zld1kXvUCYu9gjnJ"
access_token = "1305689531421786112-FNe1D2tjmvFjzikZYHDyjvRVAVT9gk"
access_token_secret = "G6KV4pfTg6l7BSXxbQZDyYbREmr2taNkYzBzSZZfDyBIa"

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit = True)
api = tweepy.API(auth,wait_on_rate_limit_notify = True)

languages = ["ar","zh","nl","en","fr","de","id","it","ja","ko","pt","es","th","tr"]

# instantiate a client
# api_key = "AIzaSyByLtOhPnAUhnzRDvXmmg5tuMnELC0cHY8"
# api_service_name = 'language'
# api_version = 'v1'
# service = build(api_service_name,api_version,developerKey = api_key)
# client = service.language().client().list().execute()



# Data Collection &  Processing
# ---------------------------------------------------------------------------------------------------------------------

def get_coordinates(filename):
    lat_long = pd.read_csv(filename,usecols = ["latitude","longitude","country"])
    lat_long["country"] = lat_long["country"].astype(str).apply(lambda s: s.strip())
    lat_long["latitude"] = lat_long["latitude"].astype(str).apply(lambda s: s.strip())
    lat_long["longitude"] = lat_long["longitude"].astype(str).apply(lambda s: s.strip())
    lat_long = lat_long[["country","latitude","longitude"]]
    lat_long = lat_long.sort_values(by = "country")

    radius = pd.read_csv("countries of the world.csv",usecols = ["Country","Area (sq. mi.)"])
    radius["Country"] = radius["Country"].astype(str).apply(lambda s: s.strip())
    radius["Area (sq. mi.)"] = radius["Area (sq. mi.)"].astype(float).apply(lambda x: math.sqrt(x))
    radius.columns = ["country","radius"]
        

    coordinates = pd.merge(lat_long,radius,on = ["country"])

    return coordinates


def read_csv_hfi(filename):
    df_byCountry = pd.read_csv(filename,usecols = ["countries","region","hf_score","hf_rank","hf_quartile",
                                         "pf_expression","pf_association_assembly","pf_movement"],na_values = ["-"])

    df_byCountry.loc[:,"hf_score":"pf_movement"] = df_byCountry.loc[:,"hf_score":"pf_movement"].astype(float)

    aggregation_functions = {"region": "first","hf_score": "mean","hf_rank": "max","hf_quartile": "max",
                             "pf_expression": "mean","pf_association_assembly": "mean","pf_movement": "mean"}

    df_byRegion = df_byCountry.groupby(by = ["countries"]).aggregate(aggregation_functions)

    return df_byCountry,df_byRegion


# Twitter Interaction and Feature Extraction
# ---------------------------------------------------------------------------------------------------------------------

# create get_tweets -> takes coordinates, a datetime range to search, result type, maximum number of tweets to scrape
def get_tweets(coordinates,result_type,until_date,count,max_tweets):
    """Takes in 5 parameters, set the max_tweets to 150, count to 25, and result type to 'recent'
    until date as the current date, and the coordinates equal to the 'latitude' and 'longitude'
    values. Returns dataframe with following columns -> text, created_at_date, favorite_count,
    user location, followers count, friends count, and the language used.
    Indexed 0 - 6"""
    tweets = tweepy.Cursor(api.search,geocode = coordinates,result_type = result_type,
                           until = until_date,count = count).items(max_tweets)

    tweets_list = [
         [filter_regex(tweet.text),tweet.created_at,tweet.retweet_count,tweet.favorite_count,
          tweet.user.location,tweet.user.followers_count,tweet.user.friends_count,
          tweet.lang] for tweet in tweets]


    tweets_df = pd.DataFrame(data = tweets_list,columns = ["text","created_at","retweet_count","favorite_count",
                                                           "user_location","followers_count",
                                                           "friends_count","language"])

    return tweets_df

def get_tweets_by_country(coordinates_df):
    """Takes in tweet_df, run the get_tweets to get all those tweets
    Uses latitude, longitude, and radius, return a dataframe with each iteration
    Save into list of dataframes, and merge the list into a single frame
    byCountry -> country, all the columns of tweets_df"""
    # return the dataframe with country, lat, and longitude, radius
    result_type = 'recent'
    max_tweets = 500

    tweets_by_country = pd.DataFrame()

    print(f"retrieving tweets, 5000 tweets remaining")

    # go through the dataframe for the coordinates by country, and retrieve the tweets from each country (~25)
    # save results into dataframe with following characteristics -> country, text
    for coordinate in coordinates_df.itertuples():
        tweets = get_tweets(coordinate[2],result_type,date,150,max_tweets)
        tweets["region"] = coordinate[1]
        tweets_by_country = pd.concat([tweets_by_country,tweets])
        print(f"retrieving tweets, {5000 - len(tweets_by_country)} tweets remaining")
    
    print("All tweets extracted")
    
    return tweets_by_country

# Visualizations
# ---------------------------------------------------------------------------------------------------------------------

def visualizations(dataframe):
        dataframe = dataframe.sort_values(by="hf_score", ascending=False)
    plt.figure(figsize=(20, 6))
    plt.bar(x=dataframe["region"], height=dataframe["hf_score"], label="Average HFI Score")
    plt.ylabel("Average HFI Score")
    plt.xlabel("Region")
    plt.legend()
    plt.show()

    plt.figure()

    bargraph1 = plt.bar(x=dataframe["region"], height=dataframe["hf_rank"], label=" HFI Rank for different regions")
    bargraph1.shoe()
    idx = np.where((dataframe['pf_expression'] >= 8))
    df = dataframe.loc[idx]
    bargraph1 = plt.bar(x=(df["region"]), height=df["hf_score"],
                        label="HFI Score of countries with Freedom of speech ")
    bargraph1.show()

    idi = np.where((dataframe['pf_expression'] < 8))
    df2 = dataframe.loc[idi]
    bargraph2 = plt.bar(x=(df2["region"]), height=df2["hf_score"],
                        label="HFI Score of countries without Freedom of speech ")
    bargraph2.show()

    yes_mean = np.mean(df['hf_rank'])
    no_mean = np.mean(df2['hf_rank'])
    data = pd.DataFrame({
        "Country with Freedom of Speach": yes_mean,
        "Country without Freedom of Speech": no_mean
    })
    data.plot.bar(rot=0)

# Machine Learning and Sentiment Analysis
# ---------------------------------------------------------------------------------------------------------------------

def findSentiment(dataframe):
    dfString = [d for d in dataframe["text"]]
    # iterate through each paragraph of text
    for index,s in enumerate(dfString):
        document = types.Document(
            content = s,
            type = enums.Document.Type.PLAIN_TEXT)

        # Detects the sentiment of the text
        sentiment = client.analyze_sentiment(document = document).document_sentiment
        df["score"][index] = sentiment.score
        df["magnitude"][index] = sentiment.magnitude
    return df

# Final Report and Presentation
# ---------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    df,df_aggregates = read_csv_hfi("hfi_cc_2019.csv")
    df_by_country,df_by_region = read_csv_hfi("hfi_cc_2019.csv")
    df_coordinates = get_coordinates("lat_long_coordinates.csv")

    df_regional_coord = pd.read_csv("regional_coordinates .csv")
    print(df_regional_coord)


    # tweets = get_tweets_by_country(df_regional_coord)
    # print(tweets)
