import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
# 先不用机器学习
# from tensorflow.keras.models import load_model
import json
import sys
# grib
def get_name_fan(string_name):
    if string_name == '白盆珠、岭下-博罗':
        name = 'bpzlx'
    elif string_name == '白盆珠流域':
        name = 'bpz'
    elif string_name =='枫树坝流域':
        name = 'fsb'
    elif string_name =='新丰江集水区':
        name = 'xfj'
    elif string_name == '龙川上游':
        name = 'lcup'
    elif string_name == '龙川下游':
        name = 'lcdw'
    else:
        name = 'hylx'
    return name
# 白盘珠、岭下-博罗 = bpzlx ; 白盆珠流域 = bpz ; 枫树坝流域 = fsb ; 新丰江集水区 = xfj ; 龙川上游 =  lcup ; 龙川下游 = lcdw 
# 河源-岭下 = hylx 
def get_name(string_name):
    if string_name == 'bpzlx':
        name = '白盆珠、岭下-博罗'
    elif string_name == 'bpz':
        name = '白盆珠流域'
    elif string_name =='fsb':
        name = '枫树坝流域'
    elif string_name =='xfj':
        name = '新丰江集水区'
    elif string_name == 'lcup':
        name = '龙川上游'
    elif string_name == 'lcdw':
        name = '龙川下游'
    elif string_name == 'fsbre':
        name = '枫树坝水库'
    elif string_name == 'xfjre':
        name = '新丰江水库'
    elif string_name == 'bpzre':
        name = '白盆珠水库'
    else:
        name = '河源-岭下'
    return name
def get_time_value(string):
    return string.split(".")[3]

def fill_nan_with_nearest(arr):
    mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[0]), 0)
    np.maximum.accumulate(idx, out=idx)
    return arr[idx]

def convert_numpy_arrays_to_lists(data):
    if isinstance(data, dict):
        return {key: convert_numpy_arrays_to_lists(value) for key, value in data.items()}
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data

def run_HHBBVV(start_date):
    import os
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
    import glob
    import pandas as pd
    # 先不用机器学习
    # from tensorflow.keras.models import load_model
    import json
    import sys
    # 读取文件的路径
    # 函数库的路径
    # 数据库的路径
    # 驱动数据的路径
    # 输出的路径
    path_now = os.getcwd()
    path_forcing = path_now +'/data/database/forecast/6hrly_ori/'
    file_forcing = os.listdir(path_forcing)
    for name in file_forcing:
        if name == start_date:
            file_forcing = name
    path_forcing = path_forcing + file_forcing + '/flxf/'
    path_model = path_now +'/models/'
    path_model_parameter = path_now +'/models/parameter/hmflow/HBV/'
    path_constant = path_now +'/data/constant/'
    path_result = path_now +'/results/'
    # os.chdir(path_model)
    import models.HBV_model as HBV
    import models.reservoir_model as reservoir
    # 导入HBV率定好的参数
    os.chdir(path_model_parameter)
    print(os.getcwd())
    npy = glob.glob('*.npy')
    par_values = {}
    f_level = {}
    ini_data = {}
    month_list = []
    for npy_file in npy:
        data = np.load(npy_file,allow_pickle=True).item()
        # 使用 split 方法将字符串按下划线分割成子字符串列表
        substrings = npy_file.split('_')
        # 获取下划线之前的子字符串
        name = substrings[0]
        name = get_name(name)
        par_values[name] = data
    # 先不用
    # par_values['新丰江水库'] = load_model('新丰江水库.h5')

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
        data = pd.read_table(inp_file,delimiter=' ',header=None)
        # 使用 split 方法将字符串按下划线分割成子字符串列表
        substrings = inp_file.split('_')
        # 获取下划线之前的子字符串
        name = substrings[0]
        name = get_name(name)
        ini_data[name] = data.loc[:,1]

    # 读取文件夹里面的grb
    os.chdir(path_forcing)
    grb_list = glob.glob('flxf*grb2')
    grb_list = sorted(grb_list, key=get_time_value)

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
            "白盆珠、岭下-博罗": {
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
    json_file_path = path_result
    os.chdir(json_file_path)
    json_file = os.listdir(json_file_path)
    json_file_path = [s for s in json_file if "rainfall_daily_average" in s]
    json_file_path = json_file_path[0]

    # 读取JSON文件
    with open(json_file_path, "r") as file:
        json_data = file.read()

    # 将JSON数据解析为字典
    pre = json.loads(json_data)

    P_E_dic['新丰江集水区']['pre'] = fill_nan_with_nearest(np.array(pre['DLM']['XFJ']))
    P_E_dic['枫树坝流域']['pre'] = fill_nan_with_nearest(np.array(pre['DLM']['FSB']))
    P_E_dic['白盆珠流域']['pre'] = fill_nan_with_nearest(np.array(pre['DLM']['BPZ']))
    P_E_dic['龙川上游']['pre'] = fill_nan_with_nearest(np.array(pre['DLM']['FH']))
    P_E_dic['龙川下游']['pre'] = fill_nan_with_nearest(np.array(pre['DLM']['FH']))
    P_E_dic['河源-岭下']['pre'] = fill_nan_with_nearest(np.array(pre['DLM']['HL']))
    P_E_dic['白盆珠、岭下-博罗']['pre'] = fill_nan_with_nearest(np.array(pre['DLM']['BLB']))

    # 循环输入每个grb
    for grb in grb_list:
        month_list.append(int(grb.split(".")[2][4:6]))
        os.chdir(path_forcing)
         # 读取相应位置的温度
        dd_tem = HBV.read_inputs(grb)
        os.chdir(path_constant) # 数据库位置
        for name_now in list(dd_tem.keys()):
            if name_now != 'month':
                name_e = get_name_fan(name_now)
                E_month_ave_file = name_e + '_E_ave_monthly.txt' # E_ave_monthly=历史多年平均月蒸散发
                T_month_ave_file = name_e + '_T_ave_monthly.inp' # T_ave_monthly=历史多年平均月气温
                E_month_ave = pd.read_table(E_month_ave_file,delimiter=' ',parse_dates=True,names=['month','E'],header=None)
                T_month_ave = pd.read_table(T_month_ave_file,delimiter=' ',parse_dates=True,names=['month','E'],header=None)# ETF率定
                E_month_ave['E'] = E_month_ave['E']/30
                # 根据温度计算蒸散发
                evp_final = HBV.get_evp(dd_tem,name_now,E_month_ave,T_month_ave)
                # 判断数组是否为空
                if P_E_dic[name_now]["evp"] is None:
                    P_E_dic[name_now]["evp"] = evp_final
                else:
                    P_E_dic[name_now]["evp"] = np.concatenate((P_E_dic[name_now]["evp"], evp_final)) # 加到后面
                    # float不能直接链接，否则是零维数组

    # 得到所有的产流
    for name_now in list(par_values.keys()):
        if name_now[-2:] != '水库':
            inti_data_now = ini_data[name_now]
            forcing_now = P_E_dic[name_now]
            par_values_now = par_values[name_now]
            AET, Q_cms, Q1, Q2, Q1_routed, ponding, SMS, S1, S2 = HBV.run_model(par_values_now,inti_data_now,forcing_now)
            P_E_dic[name_now]['streamflow'] = Q_cms

    # streamflow_days 旬天数 一致
    # 得到除了枫树坝水库的出流
    for name_now in list(par_values.keys()):
        outflow_now = []
        if name_now == '枫树坝水库':
            inflow = P_E_dic['枫树坝流域']['streamflow']
            outflow_di[name_now]['inflow'] = inflow
            par_values_rese = par_values[name_now]
            H = 159
            f_level_now = f_level['fsb_level']
            for i in range(len(inflow)):
                outflow,H = reservoir.rese_1(H,inflow,par_values_rese,f_level_now)
                outflow_now.append(outflow)
            outflow_di['枫树坝水库']['outflow'] = outflow_now
        if name_now == '白盆珠水库':
            inflow = P_E_dic['白盆珠流域']['streamflow']
            outflow_di[name_now]['inflow'] = inflow
            par_values_rese = par_values[name_now]
            H = 65
            f_level_now = f_level['bpz_level']
            for i in range(len(inflow)):
                outflow,H = reservoir.rese_1(H,inflow,par_values_rese,f_level_now)
                outflow_now.append(outflow)
            outflow_di['白盆珠水库']['outflow'] = outflow_now
        # 先用WRF-HYDRO的
        if name_now == '新丰江水库':
            inflow = P_E_dic['新丰江集水区']['streamflow']
            outflow_di[name_now]['inflow'] = inflow
            par_values_rese = par_values[name_now]
            H = 93
            f_level_now = f_level['xfj_level']
            for i in range(len(inflow)):
                outflow,H = reservoir.rese_1(H,inflow,par_values_rese,f_level_now)
                outflow_now.append(outflow)
            outflow_di['新丰江水库']['outflow'] = outflow_now

    # 汇流
    name_huiliu = '龙川上游'
    outflow_di.setdefault('龙川站', {})['streamflow'] = P_E_dic[name_huiliu]['streamflow'] + HBV.outflow_routing(outflow_di['枫树坝水库']['outflow'],name_huiliu,month_list)

    # # 新丰江水库出流模型
    # heyuan_baseflow = P_E_dic['龙川下游']['streamflow']
    # xfj_inflow = P_E_dic['新丰江集水区']['streamflow']
    # outflow_di['新丰江水库']['inflow'] = xfj_inflow
    # longchuan_upstream = P_E_dic['龙川上游']['streamflow']
    # xfj_inflow_before = np.roll(xfj_inflow,1)
    # month = month_list # 数据格式
    # month = np.array(month)
    # data = np.stack([heyuan_baseflow,xfj_inflow,longchuan_upstream,xfj_inflow_before,month],axis=1)
    # data = np.array(data)
    # data = data.reshape(data.shape[0], data.shape[1], 1)
    # outflow_di['新丰江水库']['outflow'] = par_values['新丰江水库'].predict(data).flatten()

    name_huiliu = '龙川下游'
    outflow_di['河源站'] = {}
    outflow_di['河源站']['streamflow'] = P_E_dic[name_huiliu]['streamflow'] + HBV.outflow_routing(outflow_di['龙川站']['streamflow'],name_huiliu,outflow_di['新丰江水库']['outflow'],month_list)

    name_huiliu = '河源-岭下'
    outflow_di['岭下站'] = {}
    outflow_di['岭下站']['streamflow'] = P_E_dic[name_huiliu]['streamflow'] + HBV.outflow_routing(outflow_di['河源站']['streamflow'],name_huiliu,month_list)

    name_huiliu = '白盆珠、岭下-博罗'
    outflow_di['博罗站'] = {}
    outflow_di['博罗站']['streamflow'] = P_E_dic[name_huiliu]['streamflow'] + HBV.outflow_routing(outflow_di['岭下站']['streamflow'],name_huiliu,outflow_di['白盆珠水库']['outflow'],month_list)

    # 三大区间来水
    outflow_di['枫树坝-河源片区区间来水'] = {}
    outflow_di['枫树坝-河源片区区间来水']['streamflow'] = P_E_dic['龙川下游']['streamflow'] +  P_E_dic['龙川上游']['streamflow']

    outflow_di['河源-岭下片区区间来水'] = {}
    outflow_di['河源-岭下片区区间来水']['streamflow'] = P_E_dic['河源-岭下']['streamflow']

    outflow_di['白盆珠、岭下-博罗片区区间来水'] = {}
    outflow_di['白盆珠、岭下-博罗片区区间来水']['streamflow'] = P_E_dic['白盆珠、岭下-博罗']['streamflow']

    # 将字典中的所有NumPy数组转换为列表
    converted_dict = convert_numpy_arrays_to_lists(outflow_di)
    # 将字典转换为JSON字符串
    json_str = json.dumps(converted_dict, ensure_ascii=False)

    os.chdir(path_result)
    # 输出JSON字符串到文件
    file_path = "streamflow_daily_HBV.json"
    with open(file_path, "w") as f:
        f.write(json_str)
    print('HBV输出完毕，结果保留在:', path_result + file_path)
    os.chdir(path_now)
