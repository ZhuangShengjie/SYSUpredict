# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 21:51:51 2023

@author: 11519
"""


import json
import numpy as np
import torch
import torch.nn as nn
from torch.nn.utils import weight_norm
import copy

from utils.History_distributiob_for_Runoff.History_condition_distribution_RF import Month_Vars_distribution as MO_Dis

class predict_model(torch.nn.Module):
    def __init__(self):
        super(predict_model, self).__init__()
        self.lstm1 = torch.nn.Sequential(        
            torch.nn.LSTM(26, 520, 2, batch_first=True),
        )        
        self.linear1 = torch.nn.Sequential(
            torch.nn.Linear(520, 1),
        )
        
    def forward(self, x):        
        out, _ = self.lstm1(x)
        y = self.linear1(out[:,-1,:])
        
        return y


def nnflow(forcing, precipitation=None):
    
    stationList = ['BaiPanZhu_in','BaiPanZhu_out','FengShuBa_in','FengShuBa_out','XinFengJiang_in','XinFengJiang_out',
                   'BoLuo','HeYuan','LingXia','LongChuan']
    subareaList = ['白盆珠流域','白盆珠流域','枫树坝集雨区', '枫树坝集雨区', '新丰江水库集雨区','新丰江水库集雨区',
                   '岭下_白盆珠_博罗区间','新丰江_枫树坝_河源区间',  '河源_岭下区间',   '博罗以下区间']
    RFstationList = ['BPZ_in','BPZ_out','FSB_in','FSB_out','XFJ_in','XFJ_out','BL','HY','LX','LC']

    # =====================================================================
    # =====================================================================
    monthly_result={}
    for station in stationList:
        
        lag = 4
        
        allX1 = forcing.mean(3).mean(2)
        allX2 = []
        for i in range(len(allX1)-lag):
            allX2.append(allX1[i:i+lag+1,:])
        allX2 = np.array(allX2, dtype=np.float32)
        allX1 = np.array(allX1[lag:], dtype=np.float32)
        
        xtest = allX2
     
        # 归一化=======================================
        minmaxInfo = np.load('./data/constant/minmaxInfo.npy', allow_pickle=True).item()
        xmax = minmaxInfo[station]['xmax']
        xmin = minmaxInfo[station]['xmin']
        ymax = minmaxInfo[station]['ymax']
        ymin = minmaxInfo[station]['ymin']
        
        xtest01 = (xtest - xmin) / (xmax - xmin)
        
        DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model = predict_model().to(DEVICE)
        bestParam = torch.load('./models/parameter/nnflow/monthly_%s_%s.pth'%(station, 'bestNSE'),map_location=DEVICE)
        model.load_state_dict(bestParam)  # 还原最佳参数
        model.eval()
        
        xtestv = torch.from_numpy(xtest01).to(DEVICE)
        ymodel01 = model(xtestv).cpu().detach().numpy()
        ytest_ = (ymodel01 * (ymax - ymin)) + ymin  # 反归一化
        ytest_[ytest_<0] = 0
        
        monthly_result[station] = ytest_.reshape(-1,).tolist()
        
    with open('./results/streamflow_monthly.json', 'w') as f:
        json.dump(monthly_result,f)
        
    
    # =====================================================================
    # =====================================================================
    if not precipitation: return
    
    prec = precipitation.copy()
    for key in prec['DLM'].keys():
        for i in range(forcing.shape[0]-lag):
            prec['DLM'][key][i] = prec['DLM'][key][i]/30
    
    tenday_result={}
    
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['BPZ'][i],9999,9999,9999,9999,monthly_result['BaiPanZhu_in'][i],"BPZ_in")['Tendays_mean_Runoff'])
    tenday_result['BaiPanZhu_in'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['BPZ'][i],9999,9999,9999,9999,monthly_result['BaiPanZhu_out'][i],"BPZ_out")['Tendays_mean_Runoff'])
    tenday_result['BaiPanZhu_out'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['FSB'][i],9999,9999,9999,9999,monthly_result['FengShuBa_in'][i],"FSB_in")['Tendays_mean_Runoff'])
    tenday_result['FengShuBa_in'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['FSB'][i],9999,9999,9999,9999,monthly_result['FengShuBa_out'][i],"FSB_out")['Tendays_mean_Runoff'])
    tenday_result['FengShuBa_out'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['XFJ'][i],9999,9999,9999,9999,monthly_result['XinFengJiang_in'][i],"XFJ_in")['Tendays_mean_Runoff'])
    tenday_result['XinFengJiang_in'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['XFJ'][i],9999,9999,9999,9999,monthly_result['XinFengJiang_out'][i],"XFJ_out")['Tendays_mean_Runoff'])
    tenday_result['XinFengJiang_out'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['BPZ'][i]+prec['DLM']['FSB'][i]+prec['DLM']['XFJ'][i]+
                            prec['DLM']['BLB'][i]+prec['DLM']['FH'][i]+prec['DLM']['HL'][i]
                            ,9999,9999,9999,9999,monthly_result['BoLuo'][i],"BL")['Tendays_mean_Runoff'])
    tenday_result['BoLuo'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['FSB'][i]+prec['DLM']['FH'][i]
                            ,9999,9999,9999,9999,monthly_result['HeYuan'][i],"HY")['Tendays_mean_Runoff'])
    tenday_result['HeYuan'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['FSB'][i]+prec['DLM']['XFJ'][i]+
                            prec['DLM']['FH'][i]+prec['DLM']['HL'][i]
                            ,9999,9999,9999,9999,monthly_result['LingXia'][i],"LX")['Tendays_mean_Runoff'])
    tenday_result['LingXia'] = temp
    temp=[]
    for i in range(forcing.shape[0]-lag):
        temp.extend(MO_Dis(prec['DLM']['FSB'][i]+prec['DLM']['FH'][i]
                            ,9999,9999,9999,9999,monthly_result['LongChuan'][i],"LC")['Tendays_mean_Runoff'])
    tenday_result['LongChuan'] = temp
    
    with open('./results/streamflow_tenday.json', 'w') as f:
        json.dump(tenday_result,f)

