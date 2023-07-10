
# 这个文件运行降水分配程序
from History_condition_distribution_RF import Month_Vars_distribution as MO_Dis

# 初始输入变量赋值测试，缺省值请输入9999
Month_Pre_input = 5
Month_Prs_input = 9999
Month_Temp_input = 9999
Month_Win_input = 9999
Month_RHU_input = 9999
Month_RF_input = 200

# 输入对应的径流站点缩写
# 包括站点：博罗（BL）、河源（HY）、龙川（LC）、岭下（LX）
# 还包括三大水库的入（出）库流量：
# 新丰江（XFJ_in、XFJ_out）、枫树坝（FSB_in、FSB_out）、白盆珠(BPZ_in、BPZ_out)
Sta_name = 'LC'

Result = MO_Dis(Month_Pre_input,Month_Prs_input,Month_Temp_input,Month_Win_input,Month_RHU_input,Month_RF_input,Sta_name)

print(Result)
