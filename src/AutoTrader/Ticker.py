import pandas as pd
import time 
from AutoTrader.Candle import Candle

class Ticker:

  def __init__(self, time_frame):
    self.time_frame = time_frame #seconds
    self.observers = []
    self.candle = None 
    self.counter = 0 

  def _notify(self, candle, modifier = None):
    """Alert the observers"""
    for observer in self.observers:
        if modifier != observer:
            observer(candle)
 
  def attach(self, observer):
      """If the observer is not in the list,append it into the list"""
      if observer not in self.observers:
          self.observers.append(observer)
 
  def detach(self, observer):
      """Remove the observer from the observer list"""
      try:
          self.observers.remove(observer)
      except ValueError:
          pass

  def add_tick(self, tick_data):
    open_time = tick_data['Open Time']
    close_time  = tick_data['Close time']
    open  = tick_data['Open']
    close = tick_data['Close']
    high  = tick_data['High']
    low   = tick_data['Low']

    if not self.candle :
      self.candle = Candle(open, open_time)

    if self.counter == self.time_frame - 1 : 
      self.candle.compare(low, high)
      self.candle.do_close(close, close_time)
      self.counter = 0
      self._notify(self.candle)
      self.candle = None
    else:
      self.counter = self.counter + 1
      self.candle.compare(low, high)









