import pandas as pd

def rsi(df, w=14):
    '''
    Calculate RSI indicator
    :param df: Dataframe containing historical prices
    :param w: Window size
    :return: Series of RSI values
    '''
    pd.options.mode.chained_assignment = None
    symbol = df.columns[0]
    df.fillna(method='ffill', inplace=True)  # 들어온 데이터의 구멍을 메꿔준다
    if len(df) > w:
        df['diff'] = df.iloc[:,0].diff()   # 일별 가격차이 계산
        df['au'] = df['diff'].where(df['diff']>0, 0).rolling(w).mean()
        df['ad'] = df['diff'].where(df['diff']<0, 0).rolling(w).mean().abs()
        for r in range(w+1, len(df)):
            df['au'][r] = ( df['au'][r-1]*(w-1) + df['diff'].where(df['diff']>0,0)[r] ) / w
            df['ad'][r] = ( df['ad'][r-1]*(w-1) + df['diff'].where(df['diff']<0,0).abs()[r] ) / w
        df['rsi'] = (df['au'] / (df['au'] + df['ad']) * 100).round(2)
        return df[[symbol, 'rsi']]
    else:
        return None


def macd(df, short=12, long=26, signal=9):
    '''
    Calculate MACD indicators
    :param df: Dataframe containing historical prices
    :param short: Day length of short term MACD
    :param long: Day length of long term MACD
    :param signal: Day length of MACD signal
    :return: Dataframe of MACD values
    '''
    symbol = df.columns[0]
    df['ema_short'] = df[symbol].ewm(span=short).mean()
    df['ema_long'] = df[symbol].ewm(span=long).mean()
    df['macd'] = (df['ema_short'] - df['ema_long']).round(2)
    df['macd_signal'] = df['macd'].ewm(span=signal).mean().round(2)
    df['macd_oscillator'] = (df['macd'] - df['macd_signal']).round(2)
    return df[[symbol, 'macd','macd_signal','macd_oscillator']]


def envelope(df, w=50, spread=.05):
    '''
    Calculate Envelope indicators
    :param df: Dataframe containing historical prices
    :param w: Window size
    :param spread: % difference from center line to determine band width
    :return: Dataframe of Envelope values
    '''
    symbol = df.columns[0]
    df['center'] = df[symbol].rolling(w).mean()
    df['ub'] = df['center']*(1+spread)
    df['lb'] = df['center']*(1-spread)
    return df[[symbol, 'center','ub','lb']]


def bollinger(df, w=20, k=2):
    '''
    Calculate bollinger band indicators
    :param df: Dataframe containing historical prices
    :param w: Window size
    :param k: Multiplier to determine band width
    :return: Dataframe of bollinger band values
    '''
    symbol = df.columns[0]
    df['center'] = df[symbol].rolling(w).mean()
    df['sigma'] = df[symbol].rolling(w).std()
    df['ub'] = df['center'] + k * df['sigma']
    df['lb'] = df['center'] - k * df['sigma']
    return df[[symbol, 'center','ub','lb']]


def stochastic(df, symbol, n=14, m=3, t=3):
    '''
    Calculate stochastic indicators
    :param df: Dataframe containing historical prices
    :param symbol: Symbol or ticker of equity by finance.yahoo.com
    :param n: Day length of fast k stochastic
    :param m: Day length of slow k stochastic
    :param t: Day length of slow d stochastic
    :return: Dataframe of stochastic values
    '''
    try:
        df['fast_k'] = ( ( df['Close'] - df['Low'].rolling(n).min() ) / ( df['High'].rolling(n).max() - df['Low'].rolling(n).min() ) ).round(4) * 100
        df['slow_k'] = df['fast_k'].rolling(m).mean().round(2)
        df['slow_d'] = df['slow_k'].rolling(t).mean().round(2)
        df.rename(columns={'Close':symbol}, inplace=True)
        df.drop(columns=['High','Open','Low','Volume','Adj Close','fast_k'], inplace=True)
        return df[[symbol, 'slow_k', 'slow_d']]
    except:
        return 'Error. The stochastic indicator requires OHLC data and symbol. Try get_ohlc() to retrieve price data.'

