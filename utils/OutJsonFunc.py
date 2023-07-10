# -*- coding: utf-8 -*-
# Time    : 2023/07/05 15:25
# Author  : Zhuang ShengJ
# File    : OutJsonFunc.py
import numpy as np
from . import DateListFunc as DLF
from .TendaysDivideFunc import tendays_divide
import json


def json_dict(scale, start_date, end_date, mode, output):
    """
    输出不同尺度json_dict
    """
    output = np.array(output, dtype='float64')
    date_l, _ = DLF.date_list(scale, start_date, end_date)
    column = ['BL', 'BLB', 'FH', 'XFJ', 'FSB', 'HL', 'BPZ']
    if mode == 'average':
        DLM = {}
        for i, key in enumerate(column):
            DLM[key] = list(output[:, i])
        rainfall_out = {}
        rainfall_out['scale'] = scale
        rainfall_out['date'] = date_l
        rainfall_out['DLM'] = DLM
        if scale == 'tendays':
            DLM_tens = {}
            for basin, pr in DLM.items():
                aa = tendays_divide(basin, pr).reshape(-1)
                DLM_tens[basin] = list(aa)
                rainfall_out = {}
                rainfall_out['scale'] = scale
                date_l1 = sorted(date_l*3)
                date_l2 = ['01', '11', '21']*6
                date_lst = [x + y for x, y in zip(date_l1, date_l2)]
                rainfall_out['date'] = date_lst
                rainfall_out['DLM'] = DLM_tens
    elif mode == "all":
        rainfall_out = {}
        rainfall_out['scale'] = scale
        rainfall_out['date'] = date_l
        rainfall_out['clip'] = [22, 26, 113, 116]
        node = output.tolist()
        rainfall_out['DLM'] = node
    else:
        assert False, 'no mode'
    return rainfall_out


def get_out_json(scale, start_date, end_date, mode, output):
    """
    输出json
    """
    rainfall_out = json_dict(scale, start_date, end_date, mode, output)
    with open(f"./results/{start_date}_rainfall_{scale}_{mode}_json.json", "w") as fp:
        json.dump(rainfall_out, fp, ensure_ascii=False)
    fp.close()
    return rainfall_out


if __name__ == '__main__':
    scale = 'tendays'
    start_date = '20230701'
    end_date = None
    mode = 'average'

    date_l, _ = DLF.date_list(scale, start_date, end_date)
    output = np.random.random([6, 7])
    rainfall_out = json_dict(scale, start_date, end_date, mode, output)

