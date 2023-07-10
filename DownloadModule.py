# -*- coding: utf-8 -*-
# Time    : 2023/07/05 14:18
# Author  : Zhuang ShengJ
# File    : DownloadModule.py
import numpy as np
import json
import utils.GetPredictFunc as GPF
import utils.DownloadFunc as DLF

with open('输入.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

scale = data['scale']
start_date = data['start_date']
end_date = data['end_date']
mode = data['mode']
# 下载数据
DLF.download_ncep_all(start_date, end_date)
# 处理数据
GPF.all_input_npy(start_date, end_date)

