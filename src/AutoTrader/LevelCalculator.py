import numpy as np
import pandas as pd

class LevelCalculator:

  def __init__(self, window: pd.DataFrame):
    self._window = window
    self._spread =  np.mean(self._window['high'] - self._window['low'])

  def _is_support(self, i: int):

    if (len(self._window) <= i + 2):
      raise Exception("Trying to calculate support too close to the window end.")

    # Returns true if a V shape is going to be formed around current i, taking the lows as reference.
    # TODO: Think if it is not better to use high, low and close, to take into consideridation if it is a red or green candle.
    return \
      self._window['low'].iloc[i]   < self._window['low'].iloc[i-1] and \
      self._window['low'].iloc[i]   < self._window['low'].iloc[i+1] and \
      self._window['low'].iloc[i+1] < self._window['low'].iloc[i+2] and \
      self._window['low'].iloc[i-1] < self._window['low'].iloc[i-2]

  def _is_resistance(self, i: int):

    if (len(self._window) <= i + 2):
      raise Exception("Trying to calculate resistance too close to the window end.")

    # Returns true if an inverted V shape is going to be formed around current i, taking the highs as reference.
    # TODO: Think if it is not better to use high, low and close, to take into consideridation if it is a red or green candle.
    return \
      self._window['high'].iloc[i]   > self._window['high'].iloc[i-1] and \
      self._window['high'].iloc[i]   > self._window['high'].iloc[i+1] and \
      self._window['high'].iloc[i+1] > self._window['high'].iloc[i+2] and \
      self._window['high'].iloc[i-1] > self._window['high'].iloc[i-2] 

  def _isFarFromLevel(self, value, levels):
    return np.sum([abs(value - x) < self._spread for i, x in levels]) == 0

  def get_levels(self):

    resistances = []
    supports = []
    
    for i in range(2, self._window.shape[0] - 2):
      
      if self._is_support(i):
        value = self._window['low'].iloc[i]

        if self._isFarFromLevel(value, supports):
          supports.append((i, value))

      elif self._is_resistance(i):
        value = self._window['high'].iloc[i]

        if self._isFarFromLevel(value, resistances):
          resistances.append((i, value))

    return (resistances, supports)
