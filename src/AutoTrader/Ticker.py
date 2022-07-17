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
    time  = tick_data['Close time']
    open  = tick_data['Open']
    close = tick_data['Close']
    high  = tick_data['High']
    low   = tick_data['Low']
    if self.counter == self.time_frame - 1: #candle closed as the division mod is now lower than before (unix epoch seconds)
      self.candle.do_close(close)
      self.counter = 0
      self._notify(self.candle)
      self.candle = Candle(time, open)
    else:
      if not self.candle :
        self.candle = Candle(time, open)
      self.candle.compare(low, high)

    self.counter = self.counter + 1








