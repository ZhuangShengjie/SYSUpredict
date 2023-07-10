import pandas as pd
import numpy as np
import calendar
import pygrib
def run_model(par_values,inti_data,forcing,xun=None):
    # 读取初始条件
    St_1 = inti_data['St_1'] # 读取初始含水量
    S_km = inti_data['S_km'] # 读取流域面积
    # 读取降水+潜在蒸散发
    P_all = forcing['pre']
    E_0_all = forcing['evp']

    # 读取参数
    K = par_values['K'] # 初始水量损失率（0～1）
    SC = par_values['SC'] # 流域水损失容量(0～2000)
    N = par_values['N'] # 蒸散发参数(0~2)
    Q = np.zeros(len(P_all))
    SMS = np.zeros(len(P_all))
    for i in range(len(P_all)):
        P = P_all[i]
        E_0 = E_0_all[i]

        # 计算实际蒸散发E
        E = E_0*(P+St_1)/(((P+St_1)**N + E_0**N)**(1/N))

        # S_deta
        Y_0 = K * St_1  # 计算总获得水量（初始土壤含水量St_1 + 降雨总量）
        W = P + St_1
        Y_t = ((SC - Y_0)*W + (W - Y_0)*Y_0)/(W + SC - 2*Y_0) # 计算该月——净获得水量
        St = Y_t - E        # 计算当前土壤含水量
        if St < 0:
            St = 0
        S_deta = St - St_1  # 计算水量差异

        # 计算E和S_deta
        if xun is None:
            day = calendar.monthrange(int(forcing['year_time_series'][i]),int(forcing['month_time_series'][i]))[1]
            QQ = P - E - S_deta # 计算出月总径流深
            Q[i] = (QQ * S_km * 1000) / (24 * 3600 * day)
            SMS[i] = St
            # 下一时间步长的初始条件
            St_1 = St
        else:
            day = 10
            QQ = P - E - S_deta # 计算出月总径流深
            Q[i] = (QQ * S_km * 1000) / (24 * 3600 * day)
            SMS[i] = St
            # 下一时间步长的初始条件
            St_1 = St
    return SMS,Q

def get_ll(evp,region,name):
    evp_fsb = evp.data(lat1=region[name]['min_lat'], lat2=region[name]['max_lat'], lon1=region[name]['min_lon'], lon2=region[name]['max_lon'])
    return evp_fsb

def read_inputs(data_file):
    # % ********  Initial Condition  *********
    grbs = pygrib.open(data_file)
    # 获取所有消息
    messages = grbs.select()

    # 读取温度
    tmp = None
    # 查找指定标识符的变量
    for msg in messages:
        if msg.name == '2 metre temperature':  # 月尺度温度
            tmp = msg
            break

    # 创建字典
    region = {
        "东江流域": {
            'min_lon': 113,
            'max_lon': 116,
            'min_lat': 22,
            'max_lat': 25.5
        }
    }
    dd = {
        "枫树坝流域": {
            "evp": None,
            "tmp": None,
        },
        "龙川上游": {
            "evp": None,
            "tmp": None,
        },
        "龙川下游": {
            "evp": None,
            "tmp": None,
        },
        "新丰江集水区": {
            "evp": None,
            "tmp": None,
        },
        "河源-岭下": {
            "evp": None,
            "tmp": None,
        },
        "白盆珠流域": {
            "evp": None,
            "tmp": None,
        },
        "白盘珠、岭下-博罗": {
            "evp": None,
            "tmp": None,
        },
        "month":msg.analDate.month
    }
    # 得到evp
    evp_all = get_ll(tmp,region,'东江流域')
    fsb = evp_all[0][0][2]
    xfj = evp_all[0][1][1]
    bpz = evp_all[0][2][2]
    bpz_lx = evp_all[0][2][1]
    lc_up = (fsb + evp_all[0][1][2]) / 2
    hy_lx = evp_all[0][2][2]
    lc_down = (evp_all[0][1][2] + hy_lx) / 2

    dd['枫树坝流域']['tmp'] = fsb - 273.15
    dd['龙川上游']['tmp'] = lc_up - 273.15
    dd['龙川下游']['tmp'] = lc_down - 273.15
    dd['新丰江集水区']['tmp'] = xfj - 273.15
    dd['白盆珠流域']['tmp'] = bpz - 273.15
    dd['河源-岭下']['tmp'] = hy_lx - 273.15
    dd['白盘珠、岭下-博罗']['tmp'] = bpz_lx - 273.15

    return dd




# 根据月气温得到三旬气温
def tem_xun(month,data,test_month,test_xun):
    # 根据输入数据，找到历史的最接近的旬分配
    month_data = test_month[test_month.index.month == month]
    month_data.drop('month',axis=1)
    diff = abs(month_data - data) # 相减
    closest_index = diff.idxmin() # 找到最接近的索引
    i = closest_index.values[0]
    i = pd.Timestamp(i)  # 转换为 Timestamp 对象
    year_i = i.strftime('%Y')
    year_i = int(year_i) # 得到对应年
    month_i = i.strftime('%m')
    month_i = int(month_i) # 得到对应月
    xun_final = test_xun[test_xun['month'] == month_i][test_xun['year'] == year_i]['T'] # 根据年月找到对应的旬
    return xun_final.values # 返回上中下旬


def evp_xun_ave(month,T_month_ave,E_month_ave,T):
    ETF = 0.001
    # T是一个月的内的三个旬的气温
    PET_array = []
    for i in range(3):
        PET = ( 1 + ETF * ( T[i] - T_month_ave ) ) * E_month_ave[E_month_ave['month']==(int(month))]['E']
        PET = max((PET.values[0], 0))
        PET = PET * 10
        PET_array.append(PET)
    return PET_array

def get_evp(dd,name_now,T_month_his,T_xun_his,E_month_ave,month):
    tem = dd[name_now]['tmp']
    dd[name_now]['tmp_xun'] = tem_xun(month,tem,T_month_his,T_xun_his)
    T = dd[name_now]['tmp_xun']
    return evp_xun_ave(month,tem,E_month_ave,T)


def read_obs(data_folder,xun=None):
    fn = data_folder + '/inflow.inp'
    if xun is None:
        # % ********  Initial Condition  *********
        Qobs=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['inflow'],parse_dates=True)
    else:
        Qobs=pd.read_table(fn,delim_whitespace=True,names=['year','month','xun','inflow'])
        forcing  = Qobs.copy(deep=True)
        forcing['date'] = forcing['year'].astype(str) + '-' + forcing['month'].astype(str)
        forcing['date'] = pd.to_datetime(forcing['date'])
        forcing.index = forcing['date']
        Qobs = forcing.copy(deep=True)
    return Qobs

def read_obs_outflow(data_folder,xun=None):
    fn=data_folder + '/outflow.inp'
    # % ********  Initial Condition  *********
    if xun is None:
        Qobs=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['outflow'],parse_dates=True)
    else:
        Qobs=pd.read_table(fn,delim_whitespace=True,names=['year','month','xun','outflow'])
        forcing  = Qobs.copy(deep=True)
        forcing['day'] = forcing['outflow'].values
        forcing['date'] = forcing['year'].astype(str) + '-' + forcing['month'].astype(str)
        forcing['date'] = pd.to_datetime(forcing['date'])
        forcing.index = forcing['date']
        Qobs = forcing.copy(deep=True)
    return Qobs

# path = '/home/stanlyyp/py/BUET_AA_Modelling-main（复件）/HBV-SASK/Banff_Basin/东江流域/气象数据（降水替代）/龙川上游/旬尺度'
# read_inputs(path,'xun')


def read_obs_outflow_2(data_folder,xun=None):
    if xun is None:
        # % ********  Initial Condition  *********
        fn=data_folder + '/outflow_1.inp'
        Qobs=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['outflow'],parse_dates=True)

        # % ********  Initial Condition  *********
        fn=data_folder + '/outflow_2.inp'
        Qobs_2=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['outflow'],parse_dates=True)
    else:
        fn = data_folder + '/outflow_1.inp'
        Qobs=pd.read_table(fn,delim_whitespace=True,names=['year','month','xun','outflow'])
        forcing  = Qobs.copy(deep=True)
        forcing['date'] = forcing['year'].astype(str) + '-' + forcing['month'].astype(str)
        forcing['date'] = pd.to_datetime(forcing['date'])
        forcing.index = forcing['date']
        Qobs = forcing.copy(deep=True)

        # % ********  Initial Condition  *********
        fn = data_folder + '/outflow_2.inp'
        Qobs_2=pd.read_table(fn,delim_whitespace=True,names=['year','month','xun','outflow'])
        forcing  = Qobs_2.copy(deep=True)
        forcing['date'] = forcing['year'].astype(str) + '-' + forcing['month'].astype(str)
        forcing['date'] = pd.to_datetime(forcing['date'])
        forcing.index = forcing['date']
        Qobs_2 = forcing.copy(deep=True)

    return Qobs,Qobs_2

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

