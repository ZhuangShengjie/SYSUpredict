# -*- coding: utf-8 -*-
# Time    : 2023/06/14 19:36
# Author  : Zhuang ShengJ
# File    : DateListFunc.py
from datetime import datetime, timedelta
import pandas as pd


def calculate_date(date_str, diff):
    date = datetime.strptime(date_str, '%Y%m%d')
    new_date = date + timedelta(days=diff)
    new_date_str = new_date.strftime('%Y%m%d')
    return new_date_str


def date_dif_today(start_date):
    """
    判断输入起始日期与当天日期的差别，例如今天20230520，想看20230620的数据就只能通过20230520进行预报；否则，看20230420数据就通过0420看
    param start_date: 输入起始日期
    """
    today = datetime.today().strftime("%Y%m%d")

    delta = datetime.strptime(start_date, '%Y%m%d').date() - \
            datetime.strptime(today, '%Y%m%d').date()
    delta = delta.days
    assert delta < 200, "error: start_date too long, smaller than 200"

    if datetime.strptime(start_date, "%Y%m%d").date() >= datetime.strptime(today, "%Y%m%d").date():
        date = today
    else:
        date = start_date
    return date


def date_list(scale, start_date, end_date=None):
    """
    param start_date: 设置起始日期
    param end_date: 设置终止日期，可选
    param scale: 预测尺度 monthly、tendays、daily
    """
    if end_date:
        delta = datetime.strptime(end_date, '%Y%m%d').date()-datetime.strptime(start_date, '%Y%m%d').date()
        delta = delta.days
        assert delta < 200, "error: end_date too long, smaller than 200"

        if scale == 'monthly' or scale == 'tendays':
            date_l = [datetime.strftime(x, '%Y%m')
                      for x in list(pd.date_range(start=start_date, end=end_date, freq='1M'))]
            n_months = 4
            date_l_need = [datetime.strftime(x, '%Y%m')
                           for x in list(pd.date_range(end=start_date, periods=n_months, freq='MS'))]
        elif scale == 'daily' or scale == '6hrly':
            start_date = start_date+'06'+'0000'
            end_date = end_date+'06'+'0000'
            date_l = [datetime.strftime(x, '%Y%m%d%H')
                      for x in list(pd.date_range(start=start_date, end=end_date, freq='6H'))]
            n_days = 4
            date_l_need = [datetime.strftime(x, '%Y%m%d%H')
                           for x in list(pd.date_range(end=start_date, periods=n_days * 4, freq='6H'))]
        else:
            assert False, 'no scale'
    else:
        if scale == 'monthly' or scale == 'tendays':
            date_l = [datetime.strftime(x, '%Y%m')
                      for x in list(pd.date_range(start=start_date, periods=6, freq='1M'))]
            n_months = 5
            date_l_need = [datetime.strftime(x, '%Y%m')
                           for x in list(pd.date_range(end=start_date, periods=n_months, freq='MS'))]
        elif scale == 'daily' or scale == '6hrly':
            start_date = start_date+'06'+'0000'
            date_l = [datetime.strftime(x, '%Y%m%d%H')
                      for x in list(pd.date_range(start=start_date, periods=24, freq='6H'))]
            n_days = 5
            date_l_need = [datetime.strftime(x, '%Y%m%d%H')
                           for x in list(pd.date_range(end=start_date, periods=n_days * 4, freq='6H'))]
        else:
            assert False, 'no scale'

    if scale == 'monthly' or scale == 'tendays':
        date_l_all = date_l_need + date_l[1:]  # 整合，可调间隔
    elif scale == 'daily' or scale == '6hrly':
        date_l_need = date_l_need[3::4][:-1]
        date_l = date_l[::4]
        date_l_all = date_l_need + date_l  # 整合，可调间隔
    else:
        assert False, 'no scale'
    return date_l, date_l_all


def convert_to_first_date(date_list, scale):
    if scale == 'tendays' or scale == 'monthly':
        new_date_list = []
        for date in date_list:
            date_obj = datetime.strptime(date, "%Y%m")
            first_date_of_month = date_obj.replace(day=1)
            formatted_date = first_date_of_month.strftime("%Y%m%d")
            new_date_list.append(formatted_date)
        return new_date_list

    return date_list


def date_list_div(scale, start_date, end_date=None):
    date_i = date_dif_today(start_date)
    _, date_l_all = date_list(scale, start_date, end_date)  # 输出了两个列表
    specified_date = datetime.strptime(date_i, "%Y%m%d")
    greater_list = []
    smaller_list = []
    for date in date_l_all:
        date_format = "%Y%m%d%H" if len(date) == 10 else "%Y%m"
        date_obj = datetime.strptime(date, date_format)
        if scale == 'tendays' or scale == 'monthly':
            if date_obj >= specified_date \
                    or date_obj.month == specified_date.month:
                greater_list.append(date_obj.strftime(date_format))
            else:
                smaller_list.append(date_obj.strftime(date_format))
        else:
            if date_obj >= specified_date:
                greater_list.append(date_obj.strftime(date_format))
            else:
                smaller_list.append(date_obj.strftime(date_format))
    smaller_list = convert_to_first_date(smaller_list, scale)
    return greater_list, smaller_list


if __name__ == '__main__':
    start_date = '20230704'
    end_date = None
    scale = 'monthly'
    bb = calculate_date(start_date, 12)
    date_i = date_dif_today(start_date)
    date_l, date_l_all = date_list(scale, start_date, end_date)
    greater_list, smaller_list = date_list_div(scale, start_date, end_date)
    print(date_i)
    print(date_l)
    print(date_l_all)


