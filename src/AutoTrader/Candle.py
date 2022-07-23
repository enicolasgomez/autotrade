import time

class Candle:

  def __init__(self, open, date):
    self.date = date/1000
    self.date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.date))
    self.low = float('inf')
    self.high = 0
    self.open = open
    self.close = 0
    self.close_date = 0
    self.close_date_str = ""

  def compare(self, low, high):
    if low < self.low:
      self.low = low 
    if high > self.high:
      self.high = high

  def do_close(self, close, date):
    self.close = close
    self.close_date = date/1000
    self.close_date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.close_date))
    
  def literal(self):
    return '%s %s- L:%f O:%f H:%f C:%f'% (self.date_str, self.close_date_str, self.low, self.open, self.high, self.close)
