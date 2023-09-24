import requests
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def set_terms(trade_start, trade_end):
    '''
    :param start: The first term of period
    :param end: The last term of period
    :return: The array of period in quarters format
    '''
    trade_end = pd.to_datetime(trade_end)
    trade_start = pd.to_datetime(trade_start)
    trade_terms = pd.period_range(start=trade_start, end=trade_end, freq='Q').strftime('%YQ%q')

    fiscal_end = pd.to_datetime(trade_end) - pd.DateOffset(months=3)
    fiscal_start = pd.to_datetime(trade_start) - pd.DateOffset(months=3)
    fiscal_terms = pd.period_range(start=fiscal_start, end=fiscal_end, freq='Q').strftime('%YQ%q')

    return fiscal_terms


def fn_consolidated(otp, symbol='', term='', vol=100000, study='N'):
    '''
    :param otp: One time passcode to access the finterstellar.com api
    :param symbol: Symbol or ticker of equity by finance.yahoo.com
    :param term: Term name in quarters format to retrieve financial data
    :param vol: Average volume
    :return: The consolidate financial data of whole equities in designated term
    '''
    if term!='' or symbol!='':
        url = 'https://api.finterstellar.com/api/consolidated?otp={}&symbol={}&term={}&vol={}&study={}'.format(otp, symbol, term, vol, study)
        r = requests.get(url)
        print('\r{}...'.format(term), end='')
        if study=='Y':
            print(' For Study. Freezed at the end of July 2021. ', end='')
        try:
            df = pd.read_json(r.text, orient='index')
            df.set_index('symbol', inplace=True)
            # df = df[~(pd.isna(df['Revenue'])|pd.isna(df['Price']))].fillna(0).copy()
            print('OK')
            return df
        except:
            print('Failed')
    else:
        return 'Either symbol or term is required.'


def fn_single(otp, symbol='', window='T'):
    '''
    :param otp: One time passcode to access the finterstellar.com api
    :param symbol: Symbol or ticker of equity by finance.yahoo.com
    :param window: The way how to summarize financial data (Q:Quarterly, Y:Yearly, T:TTM)
    :return: The financial data of a company
    '''
    url = 'https://api.finterstellar.com/api/single?otp={}&symbol={}&window={}'.format(otp, symbol, window)
    r = requests.get(url)
    try:
        df = pd.read_json(r.text, orient='index')
        if 'Current Debt' in df.columns:
            df['Current Debt'].fillna(0, inplace=True)
        else:
            df['Current Debt'] = 0
        df = df[~(pd.isna(df['Revenue'])|pd.isna(df['Price']))].fillna(0).copy()
        return df
    except:
        print(r.text)


def fn_filter(df, by='PER', floor=-np.inf, cap=np.inf, n=None, asc=True):
    '''
    :param df: Dataframe storing financial data to be filtered
    :param by: Column name to be used a filter
    :param floor: The minimum value of data range to be selected
    :param cap: The maximum value of data range to be selected
    :param n: The size of result data
    :param asc: Sorting order of result data
    :return: The selected data after filtering
    '''
    df[by].replace([-np.inf, np.inf], np.nan, inplace=True)
    rst = df.query(('`{b}`>={f} and `{b}`<={c}').format(b=by,f=floor,c=cap))[['term',by]].sort_values(by=by, ascending=asc)[:n]
    # rst[by].dropna(inplace=True)
    rst.drop(columns='term', inplace=True)
    return rst


def fn_score(df, by='PER', method='relative', floor=None, cap=None, asc=True):
    '''
    :param df: Dataframe storing financial data to be scored
    :param by: Column name to be used to score
    :param method: The way how to score the data. 'relative' scores data according to their rank, 'absolute' scores data according to value
    :param floor: The minimum value of data range to be selected
    :param cap: The maximum value of data range to be selected
    :param asc: Sorting order of result data
    :return: The score data
    '''
    df[by].replace([-np.inf, np.inf], np.nan, inplace=True)
    floor = df[by].min() if floor is None else floor
    cap = df[by].max() if cap is None else cap
    if method == 'absolute':
        rst = df.query(('`{b}`>={f} and `{b}`<={c}').format(b=by,f=floor,c=cap))[['term',by]].sort_values(by=by, ascending=asc)
        if asc is True:
            rst['Score'] = round((1 - (rst[by] - floor) / (cap - floor)), 3) * 100
        else:
            rst['Score'] = round(((rst[by] - floor) / (cap - floor)), 3) * 100
    else:
        rst = df.query(('`{b}`>={f} and `{b}`<={c}').format(b=by,f=floor,c=cap))[['term',by]].sort_values(by=by, ascending=asc)
        rst['Rank'] = rst[by].rank(method='min')
        if asc:
            rst['Score'] = round( ( 1 - (rst['Rank']-1)/rst['Rank'].max() ), 3) * 100
        else:
            rst['Score'] = round(((rst['Rank'] - 1) / rst['Rank'].max()), 3) * 100
        rst.drop(columns=['Rank'], inplace=True)
    rst.drop(columns=['term'], inplace=True)
    return rst


def combine_signal(*signals, how='and', n=None):
    '''
    :param signals: Data set storing trading signal
    :param how: The joining method. Select 'and' for intersection, 'or' for union
    :param n: The size of result data
    :return: Combination of signals
    '''
    how_dict = {'and':'inner', 'or':'outer'}
    signal = signals[0]
    for s in signals[1:]:
        signal = signal.join(s, how=how_dict[how], rsuffix='_').copy()
    return signal[:n]


def combine_score(*signals, n=None):
    '''

    :param signals: Data set storing trading signal
    :param n: The size of result data
    :return: Sum of scores
    '''
    size = len(signals)
    signal = signals[0].copy()
    signal['Score'] = signal['Score']/size
    for s in signals[1:]:
        signal = signal.join(s['Score']/size, how='outer', rsuffix='_').copy()
        # signal['Score'] = round(signal['Score'].add(s['Score']/size, fill_value=0), 2)
    signal.drop(columns=[list(signal.columns)[0]], inplace=True)
    signal['Sum'] = signal.sum(axis=1)
    return signal.sort_values(by='Sum', ascending=False)[:n]


def backtest(signal, data, m=3, cost=.001, rf_rate=.01):
    '''

    :param signal: Data set storing trading signal
    :param data: Dataframe storing financial data to be tested
    :param m: Rebalancing date in month unit after the quarter end
    :param cost: Cost of transaction
    :param rf_rate: Risk free rate
    :return: Trading result such as Return, CAGR, Test period, Sharpe ratio, MDD
    '''
    # 포트폴리오 종목 세팅
    stocks = set()
    for k, v in signal.items():
        for s in v:
            stocks.add(s)

    # 트레이딩 포지션 기록
    trades = pd.DataFrame()
    for k, v in signal.items():
        for s in stocks:
            trades.loc[k, s] = 'l' if s in list(v) else 'z'
    prev = trades.shift(periods=1, axis=0)
    prev.fillna('z', inplace=True)
    position = prev + trades

    # 트레이딩 가격 산출
    pm = {0:'Price', 1:'Price_M1', 2:'Price_M2', 3:'Price_M3'}
    prices = pd.DataFrame()
    for t in position.index:
        # prices[t] = data[t][pm[m]][position.columns]
        prices[t] = data[t][pm[m]].reindex(position.columns).copy()
    prices_filtered = prices.T.copy()

    # 거래별 수익 계산
    position_cal = position.copy()
    position_cal.replace('zz', 0.0, inplace=True)
    position_cal.replace('zl', 1.0, inplace=True)
    position_cal.replace('ll', 1.0, inplace=True)
    position_cal.replace('lz', 1-cost, inplace=True)
    invest = prices_filtered * position_cal

    # 계산반영
    inclusive = position.copy()
    inclusive.replace('zz', .0, inplace=True)
    inclusive.replace('zl', .0, inplace=True)
    inclusive.replace('ll', 1.0, inplace=True)
    inclusive.replace('lz', 1.0, inplace=True)

    # 수익률 계산
    rtn = invest / invest.shift(1, axis=0) * inclusive
    rtn.replace([np.inf, -np.inf, 0.0], 1, inplace=True)
    rtn.fillna(1, inplace=True)
    # rtn[position=='zl'] = 1

    # 기별수익률 계산
    # rtn['term_rtn'] = rtn.replace(1.0, np.nan).mean(axis=1).replace(np.nan, 1.0)
    n = max([len(signal[x]) for x in list(signal.keys())])
    rtn['term_rtn'] = ( rtn.replace(1.0, np.nan).sum(axis=1) + (n - rtn.replace(1.0, np.nan).count(axis=1)) ) / n
    rtn['acc_rtn'] = rtn['term_rtn'].cumprod()
    rtn['dd'] = rtn['acc_rtn'] / rtn['acc_rtn'].cummax()
    rtn['mdd'] = rtn['dd'].cummin()

    # rtn의 term 조정
    tq = []
    for q in rtn.index:
        tq.append((pd.Period(q) + 1).strftime('%YQ%q'))
    rtn.index = tq

    rst = {}
    rst['position'] = position
    rst['rtn'] = rtn

    period = __get_period(rtn)
    rst['period'] = period

    # 포트폴리오전체수익률
    rst['portfolio_rtn'] = rtn['acc_rtn'][-1]
    rst['mdd'] = rtn['mdd'][-1]
    # Sharpe
    rst['sharpe'] = __get_sharpe_ratio(rtn, rf_rate)

    # 연환산
    rst['portfolio_rtn_annual'] = rst['portfolio_rtn'] ** (1/period) if period > 1 \
        else (rst['portfolio_rtn']-1) * (1/period) + 1

    print('CAGR: {:.2%}'.format(rst['portfolio_rtn_annual'] - 1))
    print('Accumulated return: {:.2%}'.format(rst['portfolio_rtn'] - 1))
    print('Investment period: {:.1f}yrs'.format(rst['period']))
    print('Sharpe ratio: {:.2f}'.format(rst['sharpe']))
    print('MDD: {:.2%}'.format(rst['mdd'] - 1))
    return rtn
    # return rtn, prices, position, prices_filtered, position_cal, inclusive


def __get_sharpe_ratio(df, rf_rate=.01):
    period = __get_period(df)
    df['term_exs_rtn'] = (df['term_rtn']-1) - (rf_rate/4)
    # exs_rtn_annual = (df['acc_rtn'][-1]**(1/period) -1) - rf_rate
    # exs_rtn_vol_annual = df['term_exs_rtn'].std() * np.sqrt(4)
    # sharpe_ratio = exs_rtn_annual / exs_rtn_vol_annual if exs_rtn_vol_annual>0 else 0
    total_rtn = df['acc_rtn'][-1]-(1+rf_rate)
    exs_rtn_vol_annual = df['term_exs_rtn'].std() * np.sqrt(4)
    sharpe_ratio = (total_rtn/period) / exs_rtn_vol_annual if exs_rtn_vol_annual>0 else 0
    return round(sharpe_ratio, 4)


def __get_period(df):
    period = (pd.Period(df.index[-1]).end_time - pd.Period(df.index[0]).end_time).days / 365
    return period


def quarters_before(terms, t, n):
    '''
    Return past quarter value
    :param terms: All terms
    :param current: Current term
    :param n: The value of n quarter before current term
    :return:
    '''
    return terms[list(terms).index(t) - n] if list(terms).index(t) >= n else terms[0]


def sector_info(df):
    '''

    :param df: Dataframe storing sector and industry information
    :return: Sectors and industries
    '''
    sector_info = df.groupby(by='sector', axis=0)['industry'].unique()
    return sector_info


def sector_filter(df, sector=None):
    '''

    :param df: Dataframe storing sector and industry information
    :param sector: Sectors to be selected
    :return: The data of selected sector
    '''
    sectors = sector if isinstance(sector, list) else [sector]
    rst = pd.DataFrame()
    for s in sectors:
        rst = pd.concat((rst, df[(df['sector']==s)]), axis=0)
    return rst


def industry_filter(df, industry=None):
    '''

    :param df: Dataframe storing sector and industry information
    :param industry: Industries to be selected
    :return: The data of selected industries
    '''
    industries = industry if isinstance(industry, list) else [industry]
    rst = pd.DataFrame()
    for s in industries:
        rst = pd.concat((rst, df[(df['industry']==s)]), axis=0)
    return rst


def view_portfolio(data, signal, term=None):
    '''

    :param df: Dataframe storing financial data
    :param signal: The stocks selected according to the trading strategies
    :param term: Term name to retrieve data
    :return: The selected stocks of designated term
    '''
    t = term if term else list(data.keys())[-1]
    return data[t].loc[signal[t]][['name','sector','industry','avg_volume']].sort_values(by=['sector','industry'])
