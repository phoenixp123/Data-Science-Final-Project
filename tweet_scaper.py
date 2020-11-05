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
    data = []
    with open(filename,encoding = "utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)

    byCountry = defaultdict(list)
    for d in data:
        byCountry[d["countries"]].append(d)

    # byCountry = sorted(byCountry, key = lambda c: c.lower())

    return byCountry


def jprint(data):
    print(json.dumps(data,indent = 4))


if __name__ == "__main__":
    country_data = read_csv("hfi_cc_2019.csv")
    jprint(country_data)

