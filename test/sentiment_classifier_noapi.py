from flair.models import TextClassifier
from flair.data import Sentence

import pandas as pd
from datetime import datetime, timedelta
import snscrape.modules.twitter as sntwitter

total_days = 30

end_date = datetime.today()
start_date = end_date - timedelta(days=total_days)

col_names =  ['date', 'account', 'tweet']
users_name = ['binance','elonmusk', 'weekinethnews', 'ethglobal', 'trent_vanepps', 'ethdotorg', 'ayamiyagotchi', 'cirfound']
df  = pd.DataFrame(columns = col_names)

class SentimentClass:
  tag = ""
  score = 0

def to_formatted_date(date):
  date = date.replace(hour=0, minute=0, second=0, microsecond=0)
  return datetime.strftime(date,'%Y-%m-%d')

date_range = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()

query = "ETH"
nTweets = 5


for date in date_range:
  if date.weekday() < 5:
    start_query_date = date
    end_query_date = start_query_date + timedelta(days=1)
    
    tweets_list = []
    for n, k in enumerate(users_name):
      account = users_name[n]
      long_query = query + ' lang:en since:' +  to_formatted_date(start_query_date) + ' until:' + to_formatted_date(end_query_date) + ' -filter:links -filter:replies from:' + account
      raw_tweets = enumerate(sntwitter.TwitterSearchScraper(long_query).get_items())
      for i,tweet in raw_tweets:
        if i > nTweets:
            break
        s = tweet.content
        df.loc[len(df)] = [to_formatted_date(start_query_date), account, s]

df.to_csv('tweets.csv')


classifier = TextClassifier.load('en-sentiment')

for date in date_range:
  if date.weekday() < 5:
    q = "date == '" + str(to_formatted_date(date)) + "'"
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
