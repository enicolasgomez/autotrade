class Candle:

  def __init__(self, time, open):
    self.time = time
    self.low = float('inf')
    self.high = 0
    self.open = open
    self.close = 0

  def compare(self, low, high):
    if low < self.low:
      self.low = low 
    if high > self.high:
      self.high = high

  def do_close(self, close):
    self.close = close 

  def literal(self):
    return '%f %f %f %f'% (self.low, self.open, self.high, self.close)
