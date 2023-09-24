import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def fn_single(fn, symbol):
    df = fn[fn['symbol']==symbol]
    df.set_index('term', inplace=True)
    return df.loc['2012Q1':]


def fn_consolidated(fn, master, term, volume=1000000):
    df = fn[fn['term']==term].join(master[master['avg_volume']>=volume].set_index('symbol'), on='symbol', how='inner', rsuffix='_')
    df.set_index('symbol', inplace=True)
    return df[['term', 'Revenue', 'COGS', 'Gross Profit', 'SG&A', 'Operating Income',
            'Net Income', 'EPS', 'EBITDA', 'EBIT', 'Shares', 'Cash & Equivalents',
            'Receivables', 'Inventory', 'Current Assets', 'Long Term Assets',
            'Total Assets', 'Current Debt', 'Current Liabilities', 'Long Term Debt',
            'Long Term Liabilities', 'Total Liabilities', 'Shareholders Equity',
            'Depreciation', 'Operating Cash Flow', 'Capital Expenditure',
            'Investing Cash Flow', 'Dividend', 'Financing Cash Flow', 'Price',
            'Price_M1', 'Price_M2', 'Price_M3', 'name', 'name_kr', 'sector',
            'industry', 'avg_volume']]