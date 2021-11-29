from . import util
import pandas as pd
import numpy as np
import pandas_datareader.data as web


def get_price(symbol, start_date=None, end_date=None, decimal_duex=True):
    '''
    :param symbol: Symbol or ticker of equity by finance.yahoo.com
    :param start_date: The first date of period
    :param end_date: The last date of period
    :param decimal_duex: Set false not to round up
    :return: Historical close prices
    '''
    symbol = util.str_to_list(symbol)
    end_date = pd.to_datetime(end_date).date() if end_date else pd.Timestamp.today().date()
    start_date = pd.to_datetime(start_date).date() if start_date else util.months_before(end_date, 12)
    df = web.DataReader(symbol, 'yahoo', start=start_date, end=end_date)['Close']
    __decimal_formatter(decimal_duex)
    return df[symbol]


def get_ohlc(symbol, start_date=None, end_date=None, decimal_duex=True):
    '''
    :param symbol: Symbol or ticker of equity by finance.yahoo.com
    :param start_date: The first date of period
    :param end_date: The last date of period
    :param decimal_duex: Set false not to round up
    :return: historical open, high, low, close prices and trade volume
    '''
    end_date = pd.to_datetime(end_date).date() if end_date else pd.Timestamp.today().date()
    start_date = pd.to_datetime(start_date).date() if start_date else util.months_before(end_date, 12)
    df = web.DataReader(symbol, 'yahoo', start=start_date, end=end_date)
    __decimal_formatter(decimal_duex)
    return df


def _get_multiple_prices(symbols, dates):
    prices = pd.DataFrame()
    for s in symbols:
        tmp = web.DataReader(s, 'yahoo', start=dates[0], end=dates[-1])['Close']
        tmp.rename(s, inplace=True)
        prices = pd.concat([prices, tmp], axis=1)
        prices.index = pd.to_datetime(prices.index)
    return prices.loc[dates]


def __get_month_ends(start_date=None, end_date=None):
    checker = web.DataReader('SPY', 'yahoo', start=start_date, end=end_date)['Close']
    month_ends = checker[checker.groupby([checker.index.year, checker.index.month]).apply(lambda s: np.max(s.index))].index
    return month_ends


def __get_month_end_prices(symbols, start_date=None, end_date=None):
    checker = web.DataReader('SPY', 'yahoo', start=start_date, end=end_date)['Close']
    month_ends = checker[checker.groupby([checker.index.year, checker.index.month]).apply(lambda s: np.max(s.index))].index
    prices = pd.DataFrame()
    for s in symbols:
        tmp = web.DataReader(s, 'yahoo', start=month_ends.min(), end=month_ends.max())['Close']
        tmp.rename(s, inplace=True)
        prices = pd.concat([prices, tmp], axis=1)
        prices.index = pd.to_datetime(prices.index)
    return prices.loc[month_ends]


def __decimal_formatter(duex):
    if duex:
        pd.options.display.float_format = '{:,.2f}'.format
    else:
        pd.options.display.float_format = '{:,.6f}'.format


