# -*- coding: utf-8 -*-
# Time    : 2023/06/28 17:13
# Author  : Zhuang ShengJ
# File    : PredictModule.py
import numpy as np
import json
import pandas as pd
from utils.DLdictFunc.DLdictFunc import predict_model
from utils.OutJsonFunc import get_out_json, json_dict

with open('输入.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(data)
scale = data['scale']
start_date = data['start_date']
end_date = data['end_date']
mode = data['mode']
# #####################降水预测输出########################
input_pr_m = np.load(f'./data/forcing/{start_date}_monthly_average_pr.npy')
output_pr_m = predict_model(input_pr_m, 'monthly', 'average')
input_pr_d = np.load(f'./data/forcing/{start_date}_daily_average_pr.npy')
output_pr_d = predict_model(input_pr_d, 'daily', 'average')
input_pr_d_a = np.load(f'./data/forcing/{start_date}_daily_all_pr.npy')
output_pr_d_a = predict_model(input_pr_m, 'daily', 'all')

rainfall_out_m = get_out_json('monthly', start_date, end_date, 'average', output_pr_m)
rainfall_out_t = get_out_json('tendays', start_date, end_date, 'average', output_pr_m)
rainfall_out_d = get_out_json('daily', start_date, end_date, 'average', output_pr_d)
rainfall_out_d_a = get_out_json('daily', start_date, end_date, 'all', output_pr_d_a)


from models.NNflow import nnflow
# 旬月
forcing = np.load('./data/forcing/%s_monthly_average_sf.npy' % start_date)
nnflow(forcing, rainfall_out_m)

import models.TMPH_run as TMPH
TMPH.run_TTMMPPHH()
import models.HBV_run as HBV
HBV.run_HHBBVV()






# 输入子流域名称
# 枫树坝集水区-FSB、枫树坝-河源片区-FH
# 新丰江集水区-XFJ、河源岭下片区-HL
# 白盆珠集水区-BPZ、白盆珠、岭下-博罗片区-BLB
# 博罗下游片区-BL
# df = pd.DataFrame(result,
#                   columns=['上旬', '中旬', '下旬'],
#                   index=['博罗以下区间', '岭下_白盆珠_博罗区间', '新丰江_枫树坝_河源区间', '新丰江水库集雨区',
#                          '枫树坝集雨区', '河源_岭下区间', '白盆珠流域'])
# df['date'] = [date_l[i], date_l[i], date_l[i], date_l[i], date_l[i], date_l[i], date_l[i],]
# print(df)






