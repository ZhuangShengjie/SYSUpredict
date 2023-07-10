import h5py
import numpy as np
from .History_condition_distribution.History_condition_distribution import Month_Vars_distribution


def tendays_divide(sub_basin_name, list_data, mode='average'):
    # 初始输入变量赋值测试，缺省值请输入9999
    # mm/d  # hpa # ℃ # m/s # %
    # 输入子流域名称
    # 枫树坝集水区-FSB、枫树坝-河源片区-FH
    # 新丰江集水区-XFJ、河源岭下片区-HL
    # 白盆珠集水区-BPZ、白盆珠、岭下-博罗片区-BLB
    # 博罗下游片区-BL
    if mode == 'average':
        Month_Pre_input = 9999
        Month_Prs_input = 9999
        Month_Temp_input = 9999
        Month_Win_input = 9999
        Month_RHU_input = 9999
        aa = None
        for i in list_data:
            Month_Pre_input = i/30  # 输入为总降水可否修改
            result_i = Month_Vars_distribution(Month_Pre_input, Month_Prs_input,
                                             Month_Temp_input, Month_Win_input, Month_RHU_input, sub_basin_name)
            result_i = np.array(result_i['Pre_rate_DJ_mean_TenDayscale']).reshape([1, 3])
            if aa is None:
                aa = result_i
            else:
                aa = np.concatenate([aa, result_i], axis=1)
    elif mode == 'all':
        aa = list_data
    else:
        assert False, 'no mode'
    return aa


if __name__ == '__main__':
    list_data = [7.9121857, 15]
    Result = tendays_divide('FSB', list_data)
    print(Result)


