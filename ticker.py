import csv
import random
import StringIO

import pyqtgraph as pg
import numpy as np

from PyQt4 import QtCore, QtGui
import requests

class RealTimeTicker(object):
    """
    symbol(str): symbol of stock
    pricing(str): bid of ask (also b or a)
    title(str): Title of window and chart
    scope(int): max scope of the chart, mem management
    sma_period(int): period considering SMA
    ema_period(int): period considering EMA
    std_period(int): period considering standard dev
    """
    def __init__(self, symbol, pricing, title, scope, sma_period,
                 ema_period, std_period, test_run=False):
        self.title = title
        self.scope = scope
        self.sma_period = sma_period
        self.ema_period = ema_period
        self.std_period = std_period
        self.data = np.array([])
        self.datasma = np.array([])
        self.dataema = np.array([])
        self.datastd = np.array([])
        self.win = pg.GraphicsWindow(title=self.title)

        self.chart = self.win.addPlot(title=self.title)

        self.curve =self. chart.plot(pen='y')
        self.curvesma = self.chart.plot(pen='b')
        self.curveema = self.chart.plot(pen='r')
        self.curvestd = self.chart.plot(pen='w')
        self.symbol = symbol
        self.pricing = pricing[:1]
        self.test_run = test_run

    def get_price(self):
        if self.test_run:
            return random.randint(1, 100)
        url = 'http://finance.yahoo.com/d/quotes.csv?s={0}&f=n{1}'.format(
            self.symbol, self.pricing)
        price = requests.get(url)
        f = StringIO.StringIO(price.text)
        gen = csv.reader(f, delimiter=',')
        return float(gen.next()[-1])

    def get_sma(self, all_data, period):
        assert period <= self.scope
        return np.mean(all_data[-period:])

    def get_ema(self, price, period, dataema):
        assert period <= self.scope
        last_ema = price
        if dataema.any():
            last_ema = dataema[-1]
        k = 2.0 / (period + 1)
        return (price * k) + (last_ema * (1-k))

    def get_std(self, all_data, period):
        assert period <= self.scope
        return np.std(all_data[-period:])

    def update(self):
        price = self.get_price()
        self.data = np.append(self.data[-self.scope:], price)
        self.curve.setData(self.data)
        if self.data.any():
            self.datasma = np.append(self.datasma[-self.scope:],
                                     self.get_sma(self.data, self.sma_period))
            self.curvesma.setData(self.datasma)
            self.dataema = np.append(self.dataema[-self.scope:],
                                     self.get_ema(price, self.ema_period,
                                                  self.dataema))
            self.curveema.setData(self.dataema)
            self.datastd = np.append(self.datastd[-self.scope:],
                                     self.get_std(self.data, self.std_period))
            self.curvestd.setData(self.datastd)

ticker = RealTimeTicker('GOOG', 'ask', 'Tick', 20, 20, 10, 10, test_run=True)

timer = QtCore.QTimer()
timer.timeout.connect(ticker.update)
timer.start(2000)


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
