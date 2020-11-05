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


# --------------------------------------------------------------------------------

class TextObject:
    def __init__(self,url,language):  # initialize our TextObject
        self.url = url
        self.language = language  # support will be added later for this feature -> multilingual sentiment analysis

    def extractText(self):
        r1 = requests.get(self.url)
        coverpage = r1.content

        text_data = BeautifulSoup(coverpage,'html.parser')

        paragraph_text = [p.text for p in text_data.find_all('p')]
        df = pd.DataFrame({"text": paragraph_text,"score": np.nan,"magnitude": np.nan})

        return df

    def findSentiment(self,df):
        dfString = [d for d in df["text"]]
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


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    print("bruh")
