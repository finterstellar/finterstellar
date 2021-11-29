import numpy as np
import pandas as pd

def __get_period(df):
    df.dropna(inplace=True)
    end_date = df.index[-1]
    start_date = df.index[0]
    days_between = (end_date - start_date).days
    return abs(days_between)


def __annualize(rate, period):
    if period < 360:
        rate = ((rate-1) / period * 365) + 1
    elif period > 365:
        rate = rate ** (365 / period)
    else:
        rate = rate
    return round(rate, 4)


def __get_sharpe_ratio(df, rf_rate):
    '''
    Calculate sharpe ratio
    :param df:
    :param rf_rate:
    :return: Sharpe ratio
    '''
    period = __get_period(df)
    rf_rate_daily = rf_rate / 365 + 1
    df['exs_rtn_daily'] = df['daily_rtn'] - rf_rate_daily
    exs_rtn_annual = (__annualize(df['acc_rtn'][-1], period) - 1) - rf_rate
    exs_rtn_vol_annual = df['exs_rtn_daily'].std() * np.sqrt(365)
    sharpe_ratio = exs_rtn_annual / exs_rtn_vol_annual if exs_rtn_vol_annual>0 else 0
    return round(sharpe_ratio, 4)


def indicator_to_signal(df, factor, buy, sell):
    '''
    Makes buy or sell signals according to factor indicator
    :param df: The dataframe containing stock prices and indicator data
    :param factor: The indicator to determine how to trade
    :param buy: The price level to buy
    :param sell: The price level to sell
    :return: The dataframe containing trading signal
    '''
    df['trade'] = np.nan
    if buy >= sell:
        df['trade'].mask(df[factor]>buy, 'buy', inplace=True)
        df['trade'].mask(df[factor]<sell, 'zero', inplace=True)
    else:
        df['trade'].mask(df[factor]<buy, 'buy', inplace=True)
        df['trade'].mask(df[factor]>sell, 'zero', inplace=True)
    df['trade'].fillna(method='ffill', inplace=True)
    df['trade'].fillna('zero', inplace=True)
    return df['trade']


def band_to_signal(df, buy, sell):
    '''
    Makes buy or sell signal according to band formation
    :param df: The dataframe containing stock prices and band data
    :param buy: The area in band to buy
    :param sell: The area in band to sell
    :return: The dataframe containing trading signal
    '''
    symbol = df.columns[0]
    df['trade'] = np.nan
    # buy
    if buy == 'A':
        df['trade'].mask(df[symbol]>df['ub'], 'buy', inplace=True)
    elif buy == 'B':
        df['trade'].mask((df['ub']>df[symbol]) & (df[symbol]>df['center']), 'buy', inplace=True)
    elif buy == 'C':
        df['trade'].mask((df['center']>df[symbol]) & (df[symbol]>df['lb']), 'buy', inplace=True)
    elif buy == 'D':
        df['trade'].mask((df['lb']>df[symbol]), 'buy', inplace=True)
    # zero
    if sell == 'A':
        df['trade'].mask(df[symbol]>df['ub'], 'zero', inplace=True)
    elif sell == 'B':
        df['trade'].mask((df['ub']>df[symbol]) & (df[symbol]>df['center']), 'zero', inplace=True)
    elif sell == 'C':
        df['trade'].mask((df['center']>df[symbol]) & (df[symbol]>df['lb']), 'zero', inplace=True)
    elif sell == 'D':
        df['trade'].mask((df['lb']>df[symbol]), 'zero', inplace=True)
    df['trade'].fillna(method='ffill', inplace=True)
    df['trade'].fillna('zero', inplace=True)
    return df['trade']


def combine_signal_and(df, *cond):
    '''
    Combine signals as intersection
    :param df: Dataframe containing historical prices
    :param cond: Columns to be combined
    :return: Dataframe of selected signals
    '''
    for c in cond:
        df['trade'].mask((df['trade'] == 'buy') & (df[c] == 'buy'), 'buy', inplace=True)
        df['trade'].mask((df['trade'] == 'zero') | (df[c] == 'zero'), 'zero', inplace=True)
    return df


def combine_signal_or(df, *cond):
    '''
    Combine signals as union
    :param df: Dataframe containing historical prices
    :param cond: Columns to be combined
    :return: Dataframe of selected signals
    '''
    for c in cond:
        df['trade'].mask((df['trade'] == 'buy') | (df[c] == 'buy'), 'buy', inplace=True)
        df['trade'].mask((df['trade'] == 'zero') & (df[c] == 'zero'), 'zero', inplace=True)
    return df


def position(df):
    '''
    Determine the position of portfolio according to trading signals
    :param df: The dataframe containing trading signal
    :return: The dataframe containing trading position
    '''
    df['position'] = ''
    df['position'].mask((df['trade'].shift(1)=='zero') & (df['trade']=='zero'), 'zz', inplace=True)
    df['position'].mask((df['trade'].shift(1)=='zero') & (df['trade']=='buy'), 'zl', inplace=True)
    df['position'].mask((df['trade'].shift(1)=='buy') & (df['trade']=='zero'), 'lz', inplace=True)
    df['position'].mask((df['trade'].shift(1)=='buy') & (df['trade']=='buy'), 'll', inplace=True)
    
    df['position_chart'] = 0
    df['position_chart'].mask(df['trade']=='buy', 1, inplace=True)
    return df['position']


def evaluate(df, cost=.001):
    '''
    Calculate daily returns and MDDs of portfolio
    :param df: The dataframe containing trading position
    :param cost: Transaction cost when sell
    :return: Returns, MDD
    '''
    df['signal_price'] = np.nan
    df['signal_price'].mask(df['position']=='zl', df.iloc[:,0], inplace=True)
    df['signal_price'].mask(df['position']=='lz', df.iloc[:,0], inplace=True)
    record = df[['position','signal_price']].dropna()
    record['rtn'] = 1
    record['rtn'].mask(record['position']=='lz', (record['signal_price']*(1-cost))/record['signal_price'].shift(1), inplace=True)
    record['acc_rtn'] = record['rtn'].cumprod()
    df['signal_price'].mask(df['position']=='ll', df.iloc[:,0], inplace=True)
    df['rtn'] = record['rtn']
    df['rtn'].fillna(1, inplace=True)
    df['daily_rtn'] = 1
    df['daily_rtn'].mask(df['position'] == 'll', df['signal_price'] / df['signal_price'].shift(1), inplace=True)
    df['daily_rtn'].mask(df['position'] == 'lz', (df['signal_price']*(1-cost)) / df['signal_price'].shift(1), inplace=True)
    df['daily_rtn'].fillna(1, inplace=True)
    df['acc_rtn'] = df['daily_rtn'].cumprod()
    df['acc_rtn_dp'] = ((df['acc_rtn']-1)*100).round(2)
    df['mdd'] = (df['acc_rtn'] / df['acc_rtn'].cummax()).round(4)
    df['bm_mdd'] = (df.iloc[:, 0] / df.iloc[:, 0].cummax()).round(4)
    df.drop(columns='signal_price', inplace=True)
    return df


def performance(df, rf_rate=.01):
    '''
    Calculate additional information of portfolio
    :param df: The dataframe with daily returns
    :param rf_rate: Risk free interest rate
    :return: Number of trades, Number of wins, Hit ratio, Sharpe ratio, ...
    '''
    rst = {}
    rst['no_trades'] = (df['position']=='zl').sum()
    rst['no_win'] = (df['rtn']>1).sum()
    rst['acc_rtn'] = df['acc_rtn'][-1].round(4)
    rst['hit_ratio'] = round((df['rtn']>1).sum() / rst['no_trades'], 4) if rst['no_trades']>0 else 0
    rst['avg_rtn'] = round(df[df['rtn']!=1]['rtn'].mean(), 4)
    rst['period'] = __get_period(df)
    rst['annual_rtn'] = __annualize(rst['acc_rtn'], rst['period'])
    rst['bm_rtn'] = round(df.iloc[-1,0]/df.iloc[0,0], 4)
    rst['sharpe_ratio'] = __get_sharpe_ratio(df, rf_rate)
    rst['mdd'] = df['mdd'].min()
    rst['bm_mdd'] = df['bm_mdd'].min()

    print('CAGR: {:.2%}'.format(rst['annual_rtn'] - 1))
    print('Accumulated return: {:.2%}'.format(rst['acc_rtn'] - 1))
    print('Average return: {:.2%}'.format(rst['avg_rtn'] - 1))
    print('Benchmark return : {:.2%}'.format(rst['bm_rtn']-1))
    print('Number of trades: {}'.format(rst['no_trades']))
    print('Number of win: {}'.format(rst['no_win']))
    print('Hit ratio: {:.2%}'.format(rst['hit_ratio']))
    print('Investment period: {:.1f}yrs'.format(rst['period']/365))
    print('Sharpe ratio: {:.2f}'.format(rst['sharpe_ratio']))
    print('MDD: {:.2%}'.format(rst['mdd']-1))
    print('Benchmark MDD: {:.2%}'.format(rst['bm_mdd']-1))
    return


