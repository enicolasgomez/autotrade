import operator
import mpl_finance

import matplotlib.pyplot as plt
from AutoTrader.TradeBot import TradeBot
from itertools import accumulate

class Simulator:

  def __init__(self, stock, size, start, end):
    self.bot = TradeBot()

    plt.rcParams['figure.figsize'] = [12, 7]
    plt.rc('font', size=14) 
    self.df = self.retrieve_data(stock, size, start, end)

  def plot_all(df, levels):
    fig, ax = plt.subplots()

    mpl_finance.candlestick_ohlc(ax,df.values,width=0.6, \
                    colorup='green', colordown='red', alpha=0.8)

    date_format = mpl_dates.timeFormatter('%d %b %Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    fig.tight_layout()

    for level in levels:
      plt.hlines(level[1],xmin=df['time'][level[0]],\
                xmax=max(df['time']),colors='blue')

  def plot_profit(p):
    x_axis = range(0, len(p))

    label = 'Profit - Max: {}'.format(str(p[-1]))
    plt.plot(x_axis, p, 'k', label=label )
    plt.legend()
    plt.show()


  def run(self):

    l = len(self.df)
    next_report = 0

    for i in range(0, l):
      
      percProgress = i * 1.0 / l

      if percProgress >= next_report:
        print(f'Progress {round(percProgress * 100, 5)}')
        next_report = percProgress + 0.05

      self.bot.process_new_candle(self.df['time'].iloc[i], self.df['open'].iloc[i], self.df['close'].iloc[i], self.df['high'].iloc[i], self.df['low'].iloc[i])

    closed_positions_only_reversal    = filter(lambda x: x.was_reversal     , self.bot.closed_positions) 
    closed_positions_without_reversal = filter(lambda x: not x.was_reversal , self.bot.closed_positions) 

    profit_vector_full              = list(accumulate([1 + p.profitAsPerc for p in self.bot.closed_positions          ], operator.mul))
    profit_vector_only_reversal     = list(accumulate([1 + p.profitAsPerc for p in closed_positions_only_reversal     ], operator.mul))
    profit_vector_without_reversal  = list(accumulate([1 + p.profitAsPerc for p in closed_positions_without_reversal  ], operator.mul))

    self.plot_profit(profit_vector_full)
    self.plot_profit(profit_vector_only_reversal)
    self.plot_profit(profit_vector_without_reversal)
