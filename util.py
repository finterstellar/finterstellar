# -*- coding: utf-8 -*-

import re
import pandas as pd


def str_to_usd(s):
    '''
    Convert number to dollar value
    :param s: Number
    :return: Dollar value
    '''
    if is_number(s):
        return '{:,.2f}'.format(float(s))


def str_to_krw(s):
    '''
    Convert number to Korea won value
    :param s: Number
    :return: Integer
    '''
    if is_number(s):
        return '{:,}'.format(int(s))


def is_number(s):
    '''
    Check wheter string is numeric
    :param s: String
    :return: True/False
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False


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


def str_to_num(str_num):
    '''
    Convert big number units to numbers
    :param str_num: Big number unit
    :return: Float
    '''
    powers = {'B': 10 ** 9, 'M': 10 ** 6, 'K': 10 ** 3, '': 1}
    m = str_num.replace(',', '')
    m = re.search('([0-9\.]+)(M|B|K|)', m)
    if m:
        val = m.group(1)
        mag = m.group(2)
        return float(val) * powers[mag]
    return 0.0


# 날짜 관련

def days_before(date, n):
    '''
    Get date n days before given date
    :param date: Base date
    :param n: N days
    :return: Date
    '''
    d = pd.to_datetime(date) - pd.DateOffset(days=n)
    if d.weekday() > 4:
        adj = d.weekday() - 4
        d += pd.DateOffset(days=adj)
    else:
        d = d
    return d.date()


def days_after(date, n):
    '''
    Get date n days after given date
    :param date: Base date
    :param n: N days
    :return: Date
    '''
    d = pd.to_datetime(date) + pd.DateOffset(days=n)
    if d.weekday() > 4:
        adj = 7 - d.weekday()
        d += pd.DateOffset(days=adj)
    else:
        d = d
    return d.date()


def months_before(date, n):
    '''
    Get date n months before given date
    :param date: Base date
    :param n: N months
    :return: Date
    '''
    d = pd.to_datetime(date) - pd.DateOffset(months=n)
    if d.weekday() > 4:
        adj = d.weekday() - 4
        d += pd.DateOffset(days=adj)
    else:
        d = d
    return d.date()
