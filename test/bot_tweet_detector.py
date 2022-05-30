import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta
import pandas as pd 

query = "ETHUSDT"

total_days = 200
size = 150

col_names =  ['date', 'tweet', 'bot']
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
  df.loc[len(df)] = [tweet.date, tweet.content, 0] #these are probably bots

raw_tweets = enumerate(sntwitter.TwitterSearchScraper(' lang:en since:' +  to_formatted_date(start_date) + ' until:' + to_formatted_date(end_date) + ' -filter:links -filter:replies from:elonmusk').get_items())

for i,tweet in raw_tweets:
  if i > size:
    break
  df.loc[len(df)] = [tweet.date, tweet.content, 1] #these are all elon musks tweets (human)

df.to_csv('tweets_detector.csv')

del df['date']

import numpy as np
import tensorflow as tf

import matplotlib.pyplot as plt
from tensorflow.keras import utils

labels = df.pop('bot')
raw_ds = tf.data.Dataset.from_tensor_slices((df.values, labels.values))

for text_batch, label_batch in raw_ds.take(1):
  for i in range(10):
    print("Question: ", text_batch.numpy()[i])
    print("Label:", label_batch.numpy()[i])

def plot_graphs(history, metric):
  plt.plot(history.history[metric])
  plt.plot(history.history['val_'+metric], '')
  plt.xlabel("Epochs")
  plt.ylabel(metric)
  plt.legend([metric, 'val_'+metric])



