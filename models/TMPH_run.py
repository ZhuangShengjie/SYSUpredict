import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
import json
import re
from tensorflow.keras.models import load_model
import json


def fill_nan_with_nearest(arr):
    mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[0]), 0)
    np.maximum.accumulate(idx, out=idx)
    return arr[idx]

def get_time_value(string):
    return string.split(".")[3]

def convert_numpy_arrays_to_lists(data):
    if isinstance(data, dict):
        return {key: convert_numpy_arrays_to_lists(value) for key, value in data.items()}
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data

# 读取文件的路径
# 函数库的路径
# 数据库的路径
# 驱动数据的路径
# 输出的路径
def run_TTMMPPHH():
    import os
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
    import glob
    import pandas as pd
    import json
    import re
    from tensorflow.keras.models import load_model
    import json
    path_now = os.getcwd()
    path_forcing = path_now +'/data/database/forecast/monthly_ori/'
    file_forcing = os.listdir(path_forcing)[0]
    path_forcing = path_forcing + file_forcing + '/flxf/'
    path_model = path_now +'/models/'
    path_model_parameter = path_now +'/models/parameter/hmflow/TMPH/'
    path_constant = path_now +'/data/constant/'
    path_result = path_now +'/results/'

    import models.TMPH_model as TMPH
    import models.reservoir_model as reservoir

    # 导入HBV率定好的参数
    os.chdir(path_model_parameter)
    npy = glob.glob('*.npy')
    par_values = {}
    f_level = {}
    ini_data = {}
    for npy_file in npy:
        data = np.load(npy_file,allow_pickle=True).item()
        # 使用 split 方法将字符串按下划线分割成子字符串列表
        substrings = npy_file.split('_')
        # 获取下划线之前的子字符串
        name = substrings[0]
        par_values[name] = data

    # c = load_model('新丰江水库.h5')

    pix = glob.glob('*.pickle')
    for pix_file in pix:
        data = np.load(pix_file,allow_pickle=True)
        # 使用 split 方法将字符串按下划线分割成子字符串列表
        substrings = pix_file.split('.')
        # 获取下划线之前的子字符串
        name = substrings[0]
        f_level[name] = data

    inp = glob.glob('*.inp')
    for inp_file in inp:
        data = pd.read_table(inp_file,delimiter=' ')
        # 使用 split 方法将字符串按下划线分割成子字符串列表
        substrings = inp_file.split('_')
        # 获取下划线之前的子字符串
        name = substrings[0]
        ini_data[name] = {'S_km':{},'St_1':{}}
        ini_data[name]['S_km'] = data['S_km'][0]
        ini_data[name]['St_1'] = data['St_1'][0]

    # 读取了一个月份和月尺度温度
    os.chdir(path_forcing)
    grb_list = glob.glob('flxf*grb2')
    grb_list = sorted(grb_list, key=get_time_value)
    grb_list = grb_list[3:-1]

    P_E_dic = {
            "枫树坝流域": {
                "evp": None,
                "pre": None,
            },
            "龙川上游": {
                "evp": None,
                "pre": None,
            },
            "龙川下游": {
                "evp": None,
                "pre": None,
            },
            "新丰江集水区": {
                "evp": None,
                "pre": None,
            },
            "河源-岭下": {
                "evp": None,
                "pre": None,
            },
            "白盆珠流域": {
                "evp": None,
                "pre": None,
            },
            "白盘珠、岭下-博罗": {
                "evp": None,
                "pre": None,
            }
    }

    outflow_di= {
            "枫树坝水库": {
                "inflow":None,
                "outflow": None,
            },
            "新丰江水库": {
                "inflow":None,
                "outflow": None,
            },
            "白盆珠水库": {
                "inflow":None,
                "outflow": None,
            }
    }

    # 指定JSON文件路径
    # 指定JSON文件路径
    json_file_path = path_result
    os.chdir(json_file_path)
    json_file = os.listdir(json_file_path)
    json_file_path = [s for s in json_file if "rainfall_tendays" in s]
    json_file_path = json_file_path[0]
    # 读取JSON文件
    with open(json_file_path, "r") as file:
        json_data = file.read()

    # 将JSON数据解析为字典
    pre = json.loads(json_data)

    P_E_dic['新丰江集水区']['pre'] = (fill_nan_with_nearest(np.array(pre['DLM']['XFJ'])))*10
    P_E_dic['枫树坝流域']['pre'] = (fill_nan_with_nearest(np.array(pre['DLM']['FSB'])))*10
    P_E_dic['白盆珠流域']['pre'] = (fill_nan_with_nearest(np.array(pre['DLM']['BPZ'])))*10
    P_E_dic['龙川上游']['pre'] = (fill_nan_with_nearest(np.array(pre['DLM']['FH'])))*10
    P_E_dic['龙川下游']['pre'] = (fill_nan_with_nearest(np.array(pre['DLM']['FH'])))*10
    P_E_dic['河源-岭下']['pre'] = (fill_nan_with_nearest(np.array(pre['DLM']['HL'])))*10
    P_E_dic['白盘珠、岭下-博罗']['pre'] = (fill_nan_with_nearest(np.array(pre['DLM']['BLB'])))*10

    # 月份序列
    month_list = []
    for grb in grb_list:
        month_list.append(int(grb.split(".")[3][4:]))

    i = 0
    for grb in grb_list:
        os.chdir(path_forcing)
        dd_tem = TMPH.read_inputs(grb)
        os.chdir(path_constant)
        for name_now in list(dd_tem.keys()):
            if name_now != 'month':
                month = month_list[i]
                T_month_file = name_now + '_历史月温度.inp'
                T_xun_file = name_now + '_历史旬温度.inp'
                E_month_ave_file = name_now + '_历史多年平均月蒸散发.txt'
                T_month_ave_file = name_now + '_多年月平均温度.inp'
                T_month_his = pd.read_table(T_month_file,delimiter=' ',parse_dates=True,index_col=0,header=None)
                T_month_his['month'] = T_month_his.index.month
                T_xun_his = pd.read_table(T_xun_file,delimiter=' ',parse_dates=True,names=['year','month','xun','T'],header=None)
                E_month_ave = pd.read_table(E_month_ave_file,delimiter=' ',parse_dates=True,names=['month','E'],header=None)
                E_month_ave['E'] = E_month_ave['E']/30
                T_month_ave = pd.read_table(T_month_ave_file,delimiter=' ',parse_dates=True,names=['month','E'],header=None)# ETF率定
                evp_final = TMPH.get_evp(dd_tem,name_now,T_month_his,T_xun_his,E_month_ave,month)
                # 判断数组是否为空
                if P_E_dic[name_now]["evp"] is None:
                    P_E_dic[name_now]["evp"] = evp_final
                else:
                    P_E_dic[name_now]["evp"] = np.concatenate((P_E_dic[name_now]["evp"], evp_final))
        i = i + 1
    print('蒸散发数据读取完毕')

    # 得到所有的产流
    for name_now in list(par_values.keys()):
        if name_now[-2:] != '水库':
            inti_data_now = ini_data[name_now]
            forcing_now = P_E_dic[name_now]
            par_values_now = par_values[name_now]
            SMS,Q = TMPH.run_model(par_values_now,inti_data_now,forcing_now,'xun')
            P_E_dic[name_now]['streamflow'] = Q

    # streamflow_days 旬天数 一致
    # 得到除了枫树坝水库的出流
    for name_now in list(par_values.keys()):
        outflow_now = []
        if name_now == '枫树坝水库':
            inflow = P_E_dic['枫树坝流域']['streamflow']
            outflow_di[name_now]['inflow'] = inflow
            inflow_xun_day = np.repeat(inflow,10)
            par_values_rese = par_values[name_now]
            H = 159
            f_level_now = f_level['fsb_level']
            for i in range(len(inflow_xun_day)):
                outflow,H = reservoir.rese_1(H,inflow_xun_day,par_values_rese,f_level_now)
                outflow_now.append(outflow)
            # 每隔10个数字求平均值
            outflow_now_list = []
            for i in range(0, len(outflow_now), 10):
                segment = outflow_now[i:i+10]
                segment_mean = np.mean(segment)
                outflow_now_list.append(segment_mean)
            outflow_di[name_now]['outflow'] = outflow_now_list

        if name_now == '白盆珠水库':
            inflow = P_E_dic['白盆珠流域']['streamflow']
            outflow_di[name_now]['inflow'] = inflow
            inflow_xun_day = np.repeat(inflow,10)
            par_values_rese = par_values[name_now]
            H = 65
            f_level_now = f_level['bpz_level']
            for i in range(len(inflow_xun_day)):
                outflow,H = reservoir.rese_1(H,inflow_xun_day,par_values_rese,f_level_now)
                outflow_now.append(outflow)
            # 每隔10个数字求平均值
            outflow_now_list = []
            for i in range(0, len(outflow_now), 10):
                segment = outflow_now[i:i+10]
                segment_mean = np.mean(segment)
                outflow_now_list.append(segment_mean)
            outflow_di[name_now]['outflow'] = outflow_now_list
        if name_now == '新丰江水库':
            inflow = P_E_dic['新丰江集水区']['streamflow']
            outflow_di[name_now]['inflow'] = inflow
            inflow_xun_day = np.repeat(inflow, 10)
            par_values_rese = par_values[name_now]
            H = 93
            f_level_now = f_level['xfj_level']
            for i in range(len(inflow)):
                outflow,H = reservoir.rese_1(H,inflow,par_values_rese,f_level_now)
                outflow_now.append(outflow)
            # 每隔10个数字求平均值
            outflow_now_list = []
            for i in range(0, len(outflow_now), 10):
                segment = outflow_now[i:i+10]
                segment_mean = np.mean(segment)
                outflow_now_list.append(segment_mean)
            outflow_di['新丰江水库']['outflow'] = outflow_now

    # 汇流
    name_huiliu = '龙川上游'
    outflow_di.setdefault('龙川站', {})['streamflow'] = P_E_dic[name_huiliu]['streamflow'] + outflow_di['枫树坝水库'][
        'outflow']

    name_huiliu = '龙川下游'
    outflow_di['河源站'] = {}
    outflow_di['河源站']['streamflow'] = P_E_dic[name_huiliu]['streamflow'] + outflow_di['新丰江水库']['outflow'] + outflow_di['龙川站']['streamflow']

    name_huiliu = '河源-岭下'
    outflow_di['岭下站'] = {}
    outflow_di['岭下站']['streamflow'] = P_E_dic[name_huiliu]['streamflow']  + outflow_di['河源站']['streamflow']

    name_huiliu = '白盘珠、岭下-博罗'
    outflow_di['博罗站'] = {}
    outflow_di['博罗站']['streamflow'] = P_E_dic[name_huiliu]['streamflow']  + outflow_di['岭下站']['streamflow'] + outflow_di['白盆珠水库']['outflow']

    # 将字典中的所有NumPy数组转换为列表
    converted_dict = convert_numpy_arrays_to_lists(outflow_di)

    import json
    # 将字典转换为JSON字符串
    json_str = json.dumps(converted_dict, ensure_ascii=False)

    os.chdir(path_result)
    # 输出JSON字符串到文件
    file_path = "streamflow_tendays_TMPH.json"
    with open(file_path, "w") as f:
        f.write(json_str)
    print('TMPH输出完毕，结果保留在:',path_result+file_path)
