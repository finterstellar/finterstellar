import requests
import pandas as pd

# 데이터 포맷팅
pd.options.display.float_format = '{:,.2f}'.format
pd.set_option('mode.chained_assignment', None)

# url: 서버 주소
url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
# header: 브라우저 정보
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Origin': 'http://data.krx.co.kr',
    'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201',
}

# 종목마스터
data = {
    'menuId': 'MDC0201020201',
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT01901',
    'locale': 'ko_KR',
    'mktId': 'ALL',
    'share': '1',
    'csvxls_isNo': 'false',
}
raw = requests.post(url, headers=headers, data=data)
rst = raw.json()['OutBlock_1']
ln = []
for r in rst:
    ln.append([c for c in r.values()])
df_master = pd.DataFrame(ln)
df_master.columns = r.keys()

def historical_price(symbol='000660', start_date=None, end_date=None):
    # 종목정보 선택
    stock = df_master[df_master['ISU_SRT_CD']==symbol]
    # 입력인자 세팅
    start_date = pd.to_datetime(start_date).strftime('%Y%m%d') if start_date else (pd.Timestamp.today()-pd.DateOffset(days=7)).strftime('%Y%m%d')
    end_date = pd.to_datetime(end_date).strftime('%Y%m%d') if end_date else pd.Timestamp.today().strftime('%Y%m%d')
    print(start_date, end_date)
    data = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT01701',
        'locale': 'ko_KR',
        'tboxisuCd_finder_stkisu0_0': '{}/{}'.format(stock['ISU_SRT_CD'].iloc[0], stock['ISU_ABBRV'].iloc[0]),
        'isuCd': '{}'.format(stock['ISU_CD'].iloc[0]),
        'isuCd2': '{}'.format(stock['ISU_CD'].iloc[0]),
        'codeNmisuCd_finder_stkisu0_0': '{}'.format(stock['ISU_ABBRV'].iloc[0]),
        'param1isuCd_finder_stkisu0_0': 'ALL',
        'strtDd': start_date,
        'endDd': end_date,
        'adjStkPrc_check': 'Y',
        'adjStkPrc': 2,
        'share': 1,
        'money': 1,
        'csvxls_isNo': 'false'
    }
    raw = requests.post(url, headers=headers, data=data)
    rst = raw.json()['output']
    ln = []
    for r in rst:
        ln.append([c for c in r.values()])
    df = pd.DataFrame(ln)
    df.columns = r.keys()
    df.drop(columns=['FLUC_TP_CD', 'CMPPREVDD_PRC', 'FLUC_RT'], inplace=True)
    df.rename(columns={'TRD_DD': 'Date', 'TDD_OPNPRC': 'Open', 'TDD_HGPRC': 'High', 'TDD_LWPRC': 'Low', 'TDD_CLSPRC': 'Close', 'ACC_TRDVOL': 'Volume', 'ACC_TRDVAL': 'Value', 'MKTCAP': 'MarketCap', 'LIST_SHRS': 'Shares', }, inplace=True)

    df['Date'] = pd.to_datetime(df['Date'])
    df['Open'] = df['Open'].str.replace(',', '').astype(float)
    df['High'] = df['High'].str.replace(',', '').astype(float)
    df['Low'] = df['Low'].str.replace(',', '').astype(float)
    df['Close'] = df['Close'].str.replace(',', '').astype(float)
    df['Volume'] = df['Volume'].str.replace(',', '').astype(int)
    df['Value'] = df['Value'].str.replace(',', '').astype(float)
    df['MarketCap'] = df['MarketCap'].str.replace(',', '').astype(float)
    df['Shares'] = df['Shares'].str.replace(',', '').astype(int)

    df.set_index('Date', inplace=True)
    return df


if __name__ == '__main__':
    df = historical_price()
    print(df)