from PositionType import PositionType

class Position:
    
  def __init__(self, open_date: float, position_type: PositionType, open_price: float, take_profit: float, stop_loss: float, was_reversal: bool):
    
    if not (open_price > 0):
        raise Exception("Can't open a position with a price not a positive integer")
        
    self.open_date = open_date
    self.open_price = open_price 
    self.type = position_type
    self.stop_loss = stop_loss
    self.take_profit = take_profit
    self.close_date = None
    self.close_price = None
    self.profit = None
    self.profitAsPerc = None
    self.was_reversal = was_reversal

  def close(self, price, date):
    
    if self.is_closed():
        raise Exception("Position already closed")
    
    if self.open_date >= date:
        raise Exception("Woooow! You're trying to close a position that has open date in the future yet!")

    self.close_price = price
    self.close_date = date
    self._calculate_profit()

  def _calculate_profit(self):

    if self.type == PositionType.BUY:
      self.profit = self.close_price - self.open_price
    else:
      self.profit = self.open_price - self.close_price

    self.profitAsPerc = self.profit / self.open_price

  def evaluate(self, high, low, date) -> bool:

    if self.type == PositionType.BUY:
      if low < self.stop_loss:
        self.close(self.stop_loss, date)
      elif high > self.take_profit:
        self.close(self.take_profit, date)
    elif self.type == PositionType.SELL:
      if high > self.stop_loss:
        self.close(self.stop_loss, date)
      elif low < self.take_profit:
        self.close(self.take_profit, date)
        
    return self.is_closed()

  def is_closed(self):
    return self.close_price != None 