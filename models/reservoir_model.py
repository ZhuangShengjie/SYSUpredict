import random
import numpy as np
import pandas as pd
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import minimize
from sympy import symbols, solve
def read_flow(folder):
    os.chdir(folder)
    inflow =pd.read_csv('inflow.inp',delim_whitespace=True,index_col=0,parse_dates=True,names=['inflow'],header=None)
    outflow = pd.read_csv('outflow.inp', delim_whitespace=True, index_col=0, parse_dates=True, names=['outflow'],header=None)
    print('入流，出流数据读取完毕','当前路径为:',folder)
    return inflow,outflow

from sympy import symbols, sqrt, solve
def f_q_v(f_level, v):
    a = f_level.coeffs[0]
    b = f_level.coeffs[1]
    c = f_level.coeffs[2]
    for i in range(len(v)):
        v_n = v[i]
        d = (-b + math.sqrt(b**2 - 4*a*(c - v_n))) / (2*a)
    return d


def shuiwei_liuliang(a):
    level = a['水位(m)'].values
    v = a['蓄水量(亿m3)'].values
    p_level = np.polyfit(level, v, 2)
    f_level = np.poly1d(p_level)
    return f_level

def liuliang_shuiwei(a):
    level = a['水位(m)'].values
    v = a['蓄水量(亿m3)'].values
    p_q = np.polyfit(v, level, 2)
    f_q = np.poly1d(p_q)
    return f_q

def rese_1(H,inflow,par_values,f_level):
    we = par_values['we']
    wc = par_values['wc']
    wl = par_values['wl']
    dl = par_values['dl']
    oe = par_values['oe']
    oc = par_values['oc']
    oa = par_values['oa']
    maxh = par_values['maxh']
    qi1 = inflow
    maxWeirDepth = maxh - we
    dh = H - we
    if dh>maxWeirDepth:
        dh = maxWeirDepth
    if (dh > 0):
        tmp1 = oc * oa * math.sqrt(2. * 9.81 * (H - oe))
        tmp2 = wc * wl * (dh ** (3. / 2.))
    elif (H - oe)>0:
        tmp1 = oc * oa * math.sqrt(2. * 9.81 * (H - oe))
        tmp2 = 0
    else:
        tmp1 = 0
        tmp2 = 0
    if (H > maxh):
        discharge = tmp1 + tmp2 + (wc * (wl * dl) * (H - maxh) ** (3. / 2.))
        # 保证不超过洪水位的情况下多放点水阿！！!!!!!!!!!!!!!!!!!!!!
    elif(dh>0):
        discharge = tmp1 + tmp2
    # elif (H > oe):
    elif (H  - oe) > 0:
        discharge = oc * oa * math.sqrt(2. * 9.81 * (H - oe))
    else:
        discharge = 0.0
    qo1 = discharge # 最终输出结合dh1,dh3,H
    if discharge is not None:
        qo1 = discharge
    qdiff_vol = (qi1  - qo1) * 3600 * 24
    v_now  = qdiff_vol/1e8 + f_level(H)###
    H = f_q_v(f_level,(v_now))###
    return qo1,H

def fun_reservoir_and_month(par_values,rese_1,Qobs,f_level):
    inflow = Qobs['inflow'].values
    we = par_values['we']
    wc = par_values['wc']
    wl = par_values['wl']
    dl = par_values['dl']
    oe = par_values['oe']
    oc = par_values['oc']
    oa = par_values['oa']
    maxh = par_values['maxh']
    HHH = []
    QQQ = []
    B = 70
    for i in range(len(inflow)):  # A是出流，B是水位
        A, B = rese_1(B, inflow[i], we, wc, wl, dl, oe, oc, oa, maxh,f_level)
        QQQ.append(A)
        HHH.append(B)
    mod = Qobs.copy(deep=True)
    mod['outflow'] = QQQ
    mod['level'] = HHH
    # 平均为月
    mod_month = mod.resample('M').mean()
    mod_month['year_month'] = mod_month.index.strftime('%Y-%m')
    mod_month.set_index('year_month', inplace=True)
    return mod,mod_month
def run_optimization(Qobs, dates, metric, par_bounds, par_values, pn, pv,f_level,name):
    # Qobs观测值，dates时间，metric误差衡量方法，par_bounds参数范围，par_values参数数值，pn随机取值，pv输出值
    # read inputs
    Qobs = Qobs[dates['start_calib']:dates['end_calib']]
    inflow = Qobs['inflow'].values
    outflow = Qobs['outflow'].values
    # Truncate par_bounds to only those parameters being optimized:
    # pn取值
    pb = tuple([par_bounds[i] for i in pn])
    # Run optimization
    print(pv)
    print(pn)
    # 最小化error，其中的error_fun包括了水库模型，不断重复error_fun
    output = minimize(error_fun, pv,
                      args=(pn, par_values, metric, inflow, outflow, f_level,name),
                      bounds=pb)
    # 输出最后取值
    pv = output['x']
    for n, v in zip(pn, pv): par_values[n] = v

    return par_values, pv

def error_fun(pv, pn, par_values, metric, inflow, outflow, f_level,name):
    for n, v in zip(pn, pv): par_values[n] = v
    we = par_values['we']
    wc = par_values['wc']
    wl = par_values['wl']
    dl = par_values['dl']
    oe = par_values['oe']
    oc = par_values['oc']
    oa = par_values['oa']
    maxh = par_values['maxh']
    fff = []
    bbb = []
    if name == '枫树坝水库':
        B = 150
    elif name == '白盆珠水库':
        B = 70
    else:
        B = 110
    for i in range(len(inflow)):  # A是出流，B是水位
        A, B = rese_1(B, inflow[i], we, wc, wl, dl, oe, oc, oa, maxh, f_level)
        fff.append(A)
        bbb.append(B)
    err = eval_metric(outflow, fff, metric)
    err = 1 - err
    return err

def eval_metric(yobs,y,metric):
    # Make sure the data sent in here are not in dataframes

    if metric.upper() == 'NSE':
        # Use negative NSE for minimization
        denominator = ((yobs-yobs.mean())**2).sum()
        numerator = ((yobs - y)**2).sum()
        negativeNSE = 1 - numerator/denominator
        return negativeNSE

    elif metric.upper() == 'NSE_LOG':
        # Use negative NSE for minimization
        yobs=np.log(yobs)
        y=np.log(y)
        denominator = ((yobs-yobs.mean())**2).mean()
        numerator = ((yobs - y)**2).mean()
        negativeNSE = -1*(1 - numerator / denominator)
        return negativeNSE

    elif metric.upper() == 'ABSBIAS':
        return np.abs((y-yobs).sum()/yobs.sum())

    elif metric.upper() == 'ME':
        return (yobs-y).mean()

    elif metric.upper() == 'MAE':
        return (np.abs(yobs-y)).mean()

    elif metric.upper() == 'MSE':
        return ((yobs-y)**2).mean()

    elif metric.upper() == 'RMSE':
        return np.sqrt(((yobs-y)**2).mean())
