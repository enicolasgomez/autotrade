from flair.models import TextClassifier
from flair.data import Sentence

import tweepy as tw
import pandas as pd
from datetime import datetime, timedelta

read = False

total_days = 30

end_date = datetime.today()
start_date = end_date - timedelta(days=total_days)

col_names =  ['date', 'tweet']
df  = pd.DataFrame(columns = col_names)

def to_formatted_date(date):
  date = date.replace(hour=0, minute=0, second=0, microsecond=0)
  return datetime.strftime(date,'%Y%m%d%H%M')

date_range = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()

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

  for date in date_range:
    if date.weekday() < 5:
      start_query_date = date
      end_query_date = start_query_date + timedelta(days=1)
      
      if end_query_date < datetime.today():
        tweets = api.search_30_day(query="ETHUSDT lang:en"
                          ,label="stage"
                          ,fromDate=to_formatted_date(start_query_date)
                          ,toDate=to_formatted_date(end_query_date) )
        # Collect tweets
        for tweet in tweets:
          s = tweet.text
          df.loc[len(df)] = [to_formatted_date(start_query_date), s]

  df.to_csv('tweets.csv')
else:
  df = pd.read_csv('tweets.csv')

classifier = TextClassifier.load('en-sentiment')

for date in date_range:
  if date.weekday() < 5:
    q = "date == " + str(to_formatted_date(date)) 
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
