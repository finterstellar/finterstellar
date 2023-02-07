from . import data_prep
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FixedLocator


ScalarFormatter().set_scientific(False)
font = 'NanumSquareRound, AppleGothic, Malgun Gothic, DejaVu Sans'
plt.style.use('bmh')
plt.rcParams['font.family'] = font
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.grid'] = True
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7
plt.rcParams['lines.antialiased'] = True
plt.rcParams['figure.figsize'] = [10.0, 5.0]
plt.rcParams['savefig.dpi'] = 96
plt.rcParams['font.size'] = 12
plt.rcParams['legend.fontsize'] = 'medium'
plt.rcParams['figure.titlesize'] = 'medium'
plt.rcParams['axes.formatter.useoffset'] = True
plt.rcParams['axes.formatter.use_mathtext'] = True


def draw_chart(df, left=None, right=None, log=False):
    '''
    Draw chart on each y-axis
    :param df: Dataframe that contains data to plot
    :param left: Columns to use left y-axis ticks
    :param right: Columns to use right y-axis ticks
    :param log: Plot in log scale
    :return: Line chart
    '''
    fig, ax1 = plt.subplots()
    x = df.index
    if left is not None:
        left = str_to_list(left)
        i = 6
        for c in left:
            ax1.plot(x, df[c], label=c, color='C'+str(i), alpha=1)
            i += 1
        if log:
            ax1.set_yscale('log')
            ax1.yaxis.set_major_formatter(ScalarFormatter())
            ax1.yaxis.set_minor_formatter(ScalarFormatter())
    else:
        ax1.axes.yaxis.set_visible(False)
    # secondary y
    if right is not None:
        right = str_to_list(right)
        ax2 = ax1.twinx()
        i = 1
        for c in right:
            ax2.plot(x, df[c], label=c+'(R)', color='C'+str(i), alpha=1)
            ax1.plot(np.nan, label=c+'(R)', color='C'+str(i))
            i += 1
        ax1.grid(False, axis='y')
        if log:
            ax2.set_yscale('log')
            ax2.yaxis.set_major_formatter(ScalarFormatter())
            ax2.yaxis.set_minor_formatter(ScalarFormatter())
    ax1.legend(loc=2)
    # plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)


def draw_band_chart(df, band=['lb','center','ub'], log=False):
    '''

    :param df: Dataframe that contains data to plot
    :param band: List of columns to be plotted as [lower band, center line, upper band]
    :param log: Plot in log scale
    :return: Band chart
    '''
    symbol = df.columns[0]
    fig, ax1 = plt.subplots()
    x = df.index
    ax1.axes.yaxis.set_visible(False)
    # secondary y
    ax2 = ax1.twinx()

    ax2.fill_between(x, df[band[0]], df[band[2]], color='C0', alpha=.2)
    ax2.plot(x, df[band[1]], label=band[1], color='C0', alpha=.7)
    ax2.plot(x, df[symbol], label=symbol, color='C1', alpha=1)
    ax1.grid(False, axis='y')
    if log:
        ax2.set_yscale('log')
        ax2.yaxis.set_major_formatter(ScalarFormatter())
        ax2.yaxis.set_minor_formatter(ScalarFormatter())
    ax2.legend(loc=2)
    # plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)


def draw_trade_results(df):
    '''
    Draw portfolio return and position changes
    :param df: Dataframe that contains data to plot
    :return: Portfolio return and position chart
    '''
    fig, ax1 = plt.subplots()
    x = df.index
    ax1.plot(x, df['acc_rtn_dp'], label='Return', color='C6', alpha=.7)
    ax1.grid(False, axis='y')
    # secondary y
    ax2 = ax1.twinx()
    ax2.plot(x, df.iloc[:,0], label=df.columns[0], color='C1', alpha=1)
    ax1.plot(np.nan, label=df.columns[0]+'(R)', color='C1')
    # 3rd y
    ax3 = ax1.twinx()
    ax3.fill_between(x, 0, df['position_chart'], color='C2', alpha=.5)
    ax3.set_ylim(0, 10)
    ax3.axes.yaxis.set_visible(False)
    ax1.legend(loc=2)
    # plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    
def draw_price_multiple_band(df, multiple='PER', acct='EPS', log=False):
    '''
    Draw price multiple band chart
    :param df: Dataframe that contains data to plot
    :param multiple: Price multiple
    :param acct: Financial account to be used to calculate price multiple
    :param log: Plot in log scale
    :return: Price multiple band chart
    '''
    fig, ax1 = plt.subplots()
    x = df.index
    i_max = round((df['Price']/df[acct]).max(),1)
    i_min = round((df['Price']/df[acct]).min(),1)
    i_3 = round(i_min+(i_max-i_min)/4*3,1)
    i_2 = round(i_min+(i_max-i_min)/2,1)
    i_1 = round(i_min+(i_max-i_min)/4,1)
    ax1.plot(x, i_max*df[acct], label=multiple+str(i_max), color='C2', linewidth=1, alpha=.7)
    ax1.plot(x, i_3*df[acct], label=multiple+str(i_3), color='C3', linewidth=1, alpha=.7)
    ax1.plot(x, i_2*df[acct], label=multiple+str(i_2), color='C4', linewidth=1, alpha=.7)
    ax1.plot(x, i_1*df[acct], label=multiple+str(i_1), color='C5', linewidth=1, alpha=.7)
    ax1.plot(x, i_min*df[acct], label=multiple+str(i_min), color='C6', linewidth=1, alpha=.7)
    ax1.plot(x, df['Price'], label='Price', color='C1', alpha=1)

    if log:
        ax1.set_yscale('log')
        ax1.yaxis.set_major_formatter(ScalarFormatter())
        ax1.yaxis.set_minor_formatter(ScalarFormatter())

    ax1.legend(loc=2)


def draw_return(df, bm='^GSPC'):
    '''
    Draw portfolio return with benchmark return
    :param df: Dataframe that contains data to plot
    :param bm: Symbol of benchmark to be plotted together
    :return: Portfolio return chart
    '''
    end = (pd.to_datetime(df.index[-1]) + pd.tseries.offsets.QuarterEnd(0)).date()
    bm_ = data_prep.get_price(symbol=bm, start_date='2006-01-01', end_date=end)
    month_ends = bm_.loc[bm_.groupby([bm_.index.year, bm_.index.month]).apply(lambda s: np.max(s.index))]
    quarter_ends = bm_.loc[bm_.groupby([bm_.index.year, bm_.index.quarter]).apply(lambda s: np.max(s.index))]
    bm_idx = bm_.head(1)
    bm_idx = bm_idx.append(quarter_ends)
    bm_idx['term_rtn'] = bm_idx.pct_change() + 1
    bm_idx = bm_idx.loc[df.index[0]:df.index[-1]]
    bm_idx['acc_rtn'] = bm_idx[bm] / bm_idx[bm][0]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    x = df.index
    x_ = np.arange(len(df))
    ax1.bar(x_-.2, (df['term_rtn']-1)*100, width=.4, label='Portfolio Rtn (term)', color='C5', linewidth=1, alpha=.5)
    ax1.bar(x_+.2, (bm_idx['term_rtn']-1)*100, width=.4, label='BM Rtn (term)', color='C6', linewidth=1, alpha=.5)
    ax2.plot(x_, (df['acc_rtn']-1)*100, label='Portfolio Rtn', color='C1', alpha=1)
    ax2.plot(x_, (bm_idx['acc_rtn']-1)*100, label='BM Rtn', color='C0', alpha=1, linestyle='dotted')
    ax1.plot(np.nan, label='Portfolio Rtn (R)', color='C1', alpha=1)
    ax1.plot(np.nan, label='BM Rtn (R)', color='C0', alpha=1, linestyle='dotted')
    ax1.axhline(0, linestyle='dotted', linewidth=1, color='k')
    ax1.legend(loc=2)
    ax1.grid(False)
    ax1.set_ylim(-100,100)
    plt.xticks(x_, x)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=90)


def str_to_list(s):
    '''
    Convert string to list
    :param s: String or List
    :return: List
    '''
    if type(s) == list:
        cds = s
    else:
        cds = []
        cds.append(s)
    return cds
