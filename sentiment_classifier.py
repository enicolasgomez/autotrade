from flair.models import TextClassifier
from flair.data import Sentence

import tweepy as tw
import pandas as pd
import datetime 

read = False

start_date = 202204011200
end_date = 202204021200

add_day = 10000

col_names =  ['date', 'tweet']
df  = pd.DataFrame(columns = col_names)

if read:
  # Your app's API/consumer key and secret can be found under the Consumer Keys
  # section of the Keys and Tokens tab of your app, under the
  # Twitter Developer Portal Projects & Apps page at
  # https://developer.twitter.com/en/portal/projects-and-apps
  consumer_key = "h6UNIPAAKNfsM72mZDUfhH6HX"
  consumer_secret = "YEdwe8L5fHHHAuvizn4GL2KHX91qw7pzOqt5ZonJgpkfRgHbrd"

  # Your account's (the app owner's account's) access token and secret for your
  # app can be found under the Authentication Tokens section of the
  # Keys and Tokens tab of your app, under the
  # Twitter Developer Portal Projects & Apps page at
  # https://developer.twitter.com/en/portal/projects-and-apps
  access_token = "1128480572-1Gspgyqmd3eMRZshDFuoYiTowb6E5l7JQD0BhRz"
  access_token_secret = "8Je3a6tIjf0Wf16Dxlh0S24kpyotPUMmNcRMUt3K0uMWi"

  auth = tw.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tw.API(auth, wait_on_rate_limit=True)

  for i in range(0, 25):
    start_date = start_date + add_day
    end_date = end_date + add_day
    tweets = api.search_30_day(query="ETHUSDT lang:en"
                      ,label="stage"
                      ,fromDate=start_date
                      ,toDate=end_date)
    # Collect tweets
    for tweet in tweets:
      s = tweet.text
      df.loc[len(df)] = [start_date, s]

  df.to_csv('tweets.csv')
else:
  df = pd.read_csv('tweets.csv')

classifier = TextClassifier.load('en-sentiment')
for date in range(start_date, end_date + ( add_day * 30 ), add_day):
  q = "date == " + str(date)
  date_tweets=df.query(q)
  sentiment = 0
  for n in range(0, len(date_tweets)):
    tweet = date_tweets["tweet"].iloc[n]
    sentence = Sentence(tweet)
    classifier.predict(sentence)
    # print sentence with predicted labels
    if sentence.tag == 'NEGATIVE':
      sentiment = sentiment - sentence.score
    else:
      sentiment = sentiment + sentence.score
  print(str(date) + ":" + str(sentiment))
