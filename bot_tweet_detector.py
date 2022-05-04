import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta
import pandas as pd 

query = "ETHUSDT"

total_days = 30
size = 150

col_names =  ['date', 'tweet']
df  = pd.DataFrame(columns = col_names)

end_date = datetime.today()
start_date = end_date - timedelta(days=total_days)

def to_formatted_date(date):
  date = date.replace(hour=0, minute=0, second=0, microsecond=0)
  return datetime.strftime(date,'%Y-%m-%d')

tweets_list = []
raw_tweets = enumerate(sntwitter.TwitterSearchScraper(query + ' lang:en since:' +  to_formatted_date(start_date) + ' until:' + to_formatted_date(end_date) + ' -filter:links -filter:replies').get_items())

for i,tweet in raw_tweets:
  if i > size:
    break
  df.loc[len(df)] = [tweet.date, tweet.content]

df.to_csv('tweets_detector.csv')
