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

# 주식 종목마스터
payload = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT01901',
    'mktId': 'ALL',
}
raw = requests.post(url, data=payload)    # 서버와 통신
rst = raw.json()['OutBlock_1']    # 딕셔너리로 변환 후 'output' 의 value만 추출
df_equity = pd.DataFrame.from_dict(rst)

# ETF 종목마스터
payload = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT04601',
}
raw = requests.post(url, data=payload)    # 서버와 통신
rst = raw.json()['output']    # 딕셔너리로 변환 후 'output' 의 value만 추출
df_etf = pd.DataFrame.from_dict(rst)

# ETN 종목마스터
payload = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT06701',
}
raw = requests.post(url, data=payload)    # 서버와 통신
rst = raw.json()['output']    # 딕셔너리로 변환 후 'output' 의 value만 추출
df_etn = pd.DataFrame.from_dict(rst)

# ELW 종목마스터
payload = {
    'bld': 'dbms/MDC/STAT/standard/MDCSTAT08501',
}
raw = requests.post(url, data=payload)    # 서버와 통신
rst = raw.json()['output']    # 딕셔너리로 변환 후 'output' 의 value만 추출
df_elw = pd.DataFrame.from_dict(rst)

# 종합
df_master = pd.concat([df_equity, df_etf, df_etn, df_elw])
df_master = df_master[['ISU_CD', 'ISU_SRT_CD', 'ISU_ABBRV']]


def get_ohlc_kr(symbol='000660', start_date=None, end_date=None):
    # 종목정보 선택
    stock = df_master[df_master['ISU_SRT_CD']==symbol] if len(df_master[df_master['ISU_ABBRV']==symbol.upper()])<1 else df_master[df_master['ISU_ABBRV']==symbol.upper()]
    if len(stock) > 0:
        # 입력인자 세팅
        start_date = pd.to_datetime(start_date).strftime('%Y%m%d') if start_date else (pd.Timestamp.today()-pd.DateOffset(days=7)).strftime('%Y%m%d')
        end_date = pd.to_datetime(end_date).strftime('%Y%m%d') if end_date else pd.Timestamp.today().strftime('%Y%m%d')
        data = {
            'bld': 'dbms/MDC/STAT/standard/MDCSTAT01701',
            'isuCd': '{}'.format(stock['ISU_CD'].iloc[0]),
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
        df = pd.DataFrame.from_dict(rst)    # 딕셔너리를 데이터프레임으로 변환

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
    else:
        return 'No matched result'


def get_price_kr(symbol='000660', start_date=None, end_date=None):
    # 종목정보 선택
    stock = df_master[df_master['ISU_SRT_CD']==symbol] if len(df_master[df_master['ISU_ABBRV']==symbol.upper()])<1 else df_master[df_master['ISU_ABBRV']==symbol.upper()]
    if len(stock) > 0:
        # 입력인자 세팅
        start_date = pd.to_datetime(start_date).strftime('%Y%m%d') if start_date else (pd.Timestamp.today()-pd.DateOffset(days=7)).strftime('%Y%m%d')
        end_date = pd.to_datetime(end_date).strftime('%Y%m%d') if end_date else pd.Timestamp.today().strftime('%Y%m%d')
        data = {
            'bld': 'dbms/MDC/STAT/standard/MDCSTAT01701',
            'isuCd': '{}'.format(stock['ISU_CD'].iloc[0]),
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
        df = pd.DataFrame.from_dict(rst)    # 딕셔너리를 데이터프레임으로 변환

        df.drop(columns=['FLUC_TP_CD', 'CMPPREVDD_PRC', 'FLUC_RT', 'TDD_OPNPRC','TDD_HGPRC','TDD_LWPRC', 'ACC_TRDVAL', 'MKTCAP', 'LIST_SHRS'], inplace=True)
        df.rename(columns={'TRD_DD': 'Date', 'TDD_CLSPRC': 'Close', 'ACC_TRDVOL': 'Volume', }, inplace=True)

        df['Date'] = pd.to_datetime(df['Date'])
        df['Close'] = df['Close'].str.replace(',', '').astype(float)
        df.rename(columns={'Close':stock['ISU_ABBRV'].iloc[0],}, inplace=True)
        df.set_index('Date', inplace=True)
        return df
    else:
        return 'No matched result'

if __name__ == '__main__':
    df = get_price_kr()
    print(df)