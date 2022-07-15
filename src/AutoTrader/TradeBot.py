from datetime import datetime
import pandas as pd
from LevelCalculator import LevelCalculator
from Position import Position
from PositionType import PositionType

class TradeBot:
    
    _moving_window_size = 30

    _use_reversal = False
    
    def __init__(self):
        self.open_position = None   
        self.closed_positions = []
        self.pending_position = None
        self.data_window = pd.DataFrame()
    
    def process_new_candle(self, timestamp: datetime, \
                                 open_price: float, close_price: float, high_price: float, low_price: float):
        """Processes a new 'candle'. Conceptually this happens at the end of
           the candle. The timestamp is the moment the candle was closed, and the 
           price values are representative of the price action time window that
           this candle represents.

            Parameters
            ----------
            timestamp : datetime
                The close datetime of the candle.
            open_price : float
                Opening price for the candle.
            close_price : float
                Closing price for the candle.
            high_price : float
                Highest price for the candle.
            low_price : float
                Lowest price for the candle.
        """
        
        d = {
              'time':  [timestamp], \
              'open':  [open_price], \
              'high':  [high_price], \
              'low':   [low_price], \
              'close': [close_price], \
            }
    
        df = pd.DataFrame(d, index = [timestamp])
        self.data_window = pd.concat([self.data_window, df]).tail(TradeBot._moving_window_size)        
        
        self.last_closed_position = None
    
        if self.pending_position and self.open_position:
            raise Exception("Whaaat? There is a position and we are trying to open a new one!")
        
        # We check if there is an open position and eveluate if would have been closed
        # If it was closed, we add it to the list of closed_positions and make open_position
        # null.
        if self.open_position and self.open_position.evaluate(high_price, low_price, timestamp):
            self.last_closed_position = self.open_position
            self.closed_positions.append(self.open_position)
            self.open_position = None
        
        # If there is a pending order schedule, we execute it.
        if self.pending_position:
            # Unpack type, take profit and stop loss values.
            (position_type, take_profit, stop_loss, was_reversal) = self.pending_position
            self.open_position = Position(timestamp, position_type, open_price, take_profit, stop_loss, was_reversal)
            self.pending_position = None

        # Finally, we evaluate the strategy, to find if we should open a position or not. We do this only
        # if there is not open positions, to avoid doing calculations that we are not going to use.
        if not self.open_position:
            self._evaluate_strategy()
        
    
    def _evaluate_strategy(self):
    
      if (len(self.data_window) < TradeBot._moving_window_size):
        return
    
      (r, s) = LevelCalculator(self.data_window).get_levels()
    
      if r and s:
            
        prev_close = self.data_window['close'].iloc[-2]
        last_close = self.data_window['close'].iloc[-1]
        last_high = self.data_window['high'].iloc[-1]
        last_low = self.data_window['low'].iloc[-1]
        last_date =  self.data_window['time'].iloc[-1]

        support = s[-1][1]
        resistance = r[-1][1]
        
        # Instead of opening the position right away, we assume that after the signal, we put a
        # order that will be completed in the opening of the next candle.
        if TradeBot._use_reversal and self.last_closed_position and self.last_closed_position.profit < 0:
          if self.last_closed_position.type == PositionType.SELL:
            self.pending_position = (PositionType.BUY,  last_close * 1.02, support, True)
          else:
            self.pending_position = (PositionType.SELL,  last_close * 0.98, resistance, True)
        else:
          if last_close < support and prev_close > support:
            self.pending_position = (PositionType.BUY,  last_close * 1.02, last_close * 0.99, False)
          elif last_close > resistance and prev_close < resistance:
            self.pending_position = (PositionType.SELL, last_close * 0.98, last_close * 1.01, False)

