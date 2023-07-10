import pandas as pd
import numpy as np
import calendar
import pygrib
def ku_fe(aaa, ku_time, fe_time,month_list):
    outflow_list = []
    month = month_list[0]
    # 丰水枯水计算时间
    ku_jintian = ku_time / 24
    ku_zuotian = 1 - ku_jintian
    if fe_time <= 24:
        fe_jintian = fe_time / 24
        fe_zuotian = 1 - fe_jintian
    else:
        fe_jintian = (48 - fe_time)/24 # 实际上是昨天
        fe_zuotian = 1 - fe_jintian # 实际上是前天
    a_a = np.array(aaa)
    # 如果是丰水季节
    if (month >= 4) and (month<=9):
        a_a_jintian = a_a * fe_jintian
        a_a_zuotian = a_a * fe_zuotian
        a_a_zuotian= np.roll(a_a_zuotian, 1)
        a_a_final = a_a_jintian + a_a_zuotian
    else:
        a_a_jintian = a_a * ku_jintian
        a_a_zuotian = a_a * ku_zuotian
        a_a_zuotian= np.roll(a_a_zuotian, 1)
        a_a_final = a_a_jintian + a_a_zuotian

    return a_a_final

def outflow_routing(Qobs_outflow,name,month_list,Qobs_outflow_2=None):
    # 1
    if name == '龙川上游':
        ku_time = 7
        fe_time = 9
        Qobs_outflow = ku_fe(Qobs_outflow,ku_time,fe_time,month_list)
        return Qobs_outflow
    elif name == '河源-岭下':
        ku_time = 17
        fe_time = 18
        Qobs_outflow = ku_fe(Qobs_outflow,ku_time,fe_time,month_list)
        return Qobs_outflow
    # 2
    elif name == '龙川下游':
        ku_time = 6
        fe_time = 18
        Qobs_outflow = ku_fe(Qobs_outflow,ku_time,fe_time,month_list)
        ku_time = 1
        fe_time = 1
        Qobs_outflow_2 = ku_fe(Qobs_outflow_2,ku_time,fe_time,month_list)
        
        return Qobs_outflow+Qobs_outflow_2
    elif name == '白盘珠、岭下-博罗':
        # 岭下-菠萝
        ku_time = 5
        fe_time = 15
        Qobs_outflow = ku_fe(Qobs_outflow,ku_time,fe_time,month_list)
        # 白盆珠-菠萝
        ku_time = 17
        fe_time = 41
        Qobs_outflow_2 = ku_fe(Qobs_outflow_2,ku_time,fe_time,month_list)
        return Qobs_outflow+Qobs_outflow_2

def get_evp(dd,name_now,E_month_ave,T_month_ave):
    month = dd['month']
    T = dd[name_now]['tmp']
    return evp_xun_ave(month,T_month_ave,E_month_ave,T)

def evp_xun_ave(month_number,ave_T,ave_E,T):
    ETF = 0.01
    # T是一个月的内的三个旬的气温
    PET_array = []
    PET = ( 1 + ETF * ( T - ave_T[ave_E['month']==(int(month_number))]['E'] ) ) * ave_E[ave_E['month']==(int(month_number))]['E']
    PET = max((PET.values[0], 0))
    PET_array.append(PET)
    return PET_array

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
        "month": msg.analDate.month
    }
    # 得到evp
    evp_all = get_ll(tmp, region, '东江流域')
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

def run_model(par_values, ini_values, forcing_data):
    # Unpack parameters:
    ETF = par_values['ETF']
    LP = par_values['LP']
    FC = par_values['FC']
    beta = par_values['beta']
    FRAC = par_values['FRAC']
    K1 = par_values['K1']
    alpha = par_values['alpha']
    K2 = par_values['K2']
    UBAS = par_values['UBAS']
    PM = par_values['PM']

    # Unpack initial conditions and forcing
    watershed_area = ini_values[0]
    initial_SMS = ini_values[1]
    initial_S1 = ini_values[2]
    initial_S2 = ini_values[3]

    P = PM * forcing_data['pre']
    PET = forcing_data['evp']
    period_length = len(P)

    SMS = np.zeros(period_length+1)
    SMS[0] = initial_SMS;

    S1 = np.zeros(period_length+1)
    S1[0] = initial_S1

    S2 = np.zeros(period_length+1)
    S2[0] = initial_S2

    ponding = np.zeros(period_length)
    Q1 = np.zeros(period_length)
    Q2 = np.zeros(period_length)
    AET = np.zeros(period_length)

    for t in range(period_length):
        ponding[t] = P[t]
        AET[t] = evapotranspiration_module(SMS[t], t, PET, ETF, LP)
        SMS[t + 1], S1[t + 1], S2[t + 1], Q1[t], Q2[t] = soil_storage_routing_module(ponding[t], SMS[t],
                                                                                     S1[t], S2[t], AET[t],
                                                                                     FC, beta, FRAC, K1, alpha, K2)

    Q1_routed = triangle_routing(Q1, UBAS)
    Q = Q1_routed + Q2
    Q_cms = (Q * watershed_area * 1000) / (24 * 3600)

    return AET, Q_cms, Q1, Q2, Q1_routed, ponding, SMS, S1, S2

def evapotranspiration_module(SMS,t,PE, ETF, LP):
    # % *****  T: Temperature - model forcing *****
    # % *****  month_number: the current month number - for Jan=1, ..., Dec=12 *****
    # % *****  SMS: Soil Moisture Storage - model state variable *****
    # % *****  ETF - This is the temperature anomaly correction of potential evapotranspiration - model parameters
    # % *****  LP: This is the soil moisture content below which evaporation becomes supply-limited - model parameter
    # % *****  PET: Potential EvapoTranspiration - model parameter
    # % *****  AET: Actual EvapoTranspiration - model

    # Potential Evapotranspiration:
    PET = ETF * PE[t]
    PET = max((PET, 0))

    if SMS > LP:
        AET = PET
    else:
        AET = PET * (SMS / LP)

    AET = min((AET, SMS))  # to avoid evaporating more than water available

    return AET


def soil_storage_routing_module(ponding, SMS, S1, S2, AET, FC, beta, FRAC, K1, alpha, K2):
    #     % *****  T: Temperature - model forcing *****
    #     % *****  month_number: the current month number - for Jan=1, ..., Dec=12 *****
    #     % *****  SMS: Soil Moisture Storage - model state variable *****
    #     % *****  ETF - This is the temperature anomaly correction of potential evapotranspiration - model parameters
    #     % *****  LP: This is the soil moisture content below which evaporation becomes supply-limited - model parameter
    #     % *****  PET: Potential EvapoTranspiration - model parameter

    #     % *****  FC: Field Capacity - model parameter ---------
    #     % *****  beta: Shape Parameter/Exponent - model parameter ---------
    #     % This controls the relationship between soil infiltration and soil water release.
    #     % The default value is 1. Values less than this indicate a delayed response, while higher
    #     % values indicate that runoff will exceed infiltration.

    if SMS < FC:
        soil_release = ponding * ((SMS / FC) ** beta)  # release of water from soil
    else:
        soil_release = ponding  # release of water from soil

    SMS_new = SMS - AET + ponding - soil_release
    if SMS_new < 0:
        SMS_new = 0

    soil_release_to_fast_reservoir = FRAC * soil_release
    soil_release_to_slow_reservoir = (1 - FRAC) * soil_release

    Q1 = K1 * S1 ** alpha
    if Q1 > S1:
        Q1 = S1

    S1_new = S1 + soil_release_to_fast_reservoir - Q1

    Q2 = K2 * S2

    S2_new = S2 + soil_release_to_slow_reservoir - Q2

    return SMS_new, S1_new, S2_new, Q1, Q2



def triangle_routing(Q, UBAS):
    UBAS = max((UBAS, 0.1))
    length_triangle_base = int(np.ceil(UBAS))
    if UBAS == length_triangle_base:
        x = np.array([0, 0.5 * UBAS, length_triangle_base])
        v = np.array([0, 1, 0])
    else:
        x = np.array([0, 0.5 * UBAS, UBAS, length_triangle_base])
        v = np.array([0, 1, 0, 0])

    weight = np.zeros(length_triangle_base)

    for i in range(1, length_triangle_base + 1):
        if (i - 1) < (0.5 * UBAS) and i > (0.5 * UBAS):
            weight[i - 1] = 0.5 * (np.interp(i - 1, x, v) + np.interp(0.5 * UBAS, x, v)) * (
                        0.5 * UBAS - i + 1) + 0.5 * (np.interp(0.5 * UBAS, x, v) + np.interp(i, x, v)) * (
                                        i - 0.5 * UBAS)
        elif i > UBAS:
            weight[i - 1] = 0.5 * (np.interp(i - 1, x, v)) * (UBAS - i + 1)
        else:
            weight[i - 1] = np.interp(i - 0.5, x, v)

    weight = weight / np.sum(weight)

    Q_routed = np.zeros(len(Q))
    for i in range(1, len(Q) + 1):
        temp = 0
        for j in range(1, 1 + min((i, length_triangle_base))):
            temp = temp + weight[j - 1] * Q[i - j]
        Q_routed[i - 1] = temp
    return Q_routed


def read_obs(data_folder):
    fn = data_folder + '/inflow.inp'
    # % ********  Initial Condition  *********
    Qobs=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['inflow'],parse_dates=True)
    return Qobs

def read_obs_outflow(data_folder,xun=None):
    fn=data_folder + '/outflow.inp'
    # % ********  Initial Condition  *********
    Qobs=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['outflow'],parse_dates=True)
    return Qobs

def read_obs_outflow_2(data_folder):
    # % ********  Initial Condition  *********
    fn=data_folder + '/outflow_1.inp'
    Qobs=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['outflow'],parse_dates=True)
    
    # % ********  Initial Condition  *********
    fn=data_folder + '/outflow_2.inp'
    Qobs_2=pd.read_table(fn,delimiter=' ',header=None,index_col=0,names=['outflow'],parse_dates=True)

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



