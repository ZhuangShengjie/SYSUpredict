
import h5py
import numpy as np

# 归一化代码
def Normalize(data):

    data_new = data[:] #复制一个同等规格的列表
    m = np.nanmean(data)
    mx = np.nanmax(data)
    mn = np.nanmin(data)
    rows, cols = data.shape # 获取矩阵行列数
    for i in range(rows): # 按照行来遍历
        for j in range(cols): # 对第i行进行遍历
            data_new[i,j] = (float(data[i,j]) - mn) / (mx - mn)
     
    return data_new

# 根据输入的年份和月计算一共有多少天
def eomday(year,month):
    if  (month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12):
        Day_num = 31
    elif (month == 4 or month == 6 or month == 9 or month == 11 ):
        Day_num = 31
    elif month == 2 and ((year % 4==0 and year % 100!=0) or (year % 400==0)):
        Day_num = 29
    else:
        Day_num = 28

    return Day_num


# 读取已经保存为npy文件的数据库
Sta_name = 'BL'

file_name_1 = 'Month_Areamean_DataBase_' + Sta_name + '.npy'
file_name_2 = 'Month_Areamean_Range_' + Sta_name + '.npy'
file_name_3 = 'TenDayscale_Areamean_DataBase_' + Sta_name + '.npy'


Month_Areamean_Range = np.load(file_name_2,allow_pickle=True)
Month_Areamean_DataBase = np.load(file_name_1,allow_pickle=True)
TenDays_Areamean_DataBase = np.load(file_name_3,allow_pickle=True)
    
# print(type(Month_Areamean_DataBase))
# print(Month_Areamean_DataBase)

# 保存为npy后不能单纯用字典方式读取，得用上述这种.item().get('Temp_DJ_mean_Monthscale')
# print(Month_Areamean_DataBase.item().get('Temp_DJ_mean_Monthscale')) # 根据键取值
# print(Month_Areamean_Range.item().get('Temp_DJ_mean_Monthscale_range'))
# print(TenDays_Areamean_DataBase.item().get('Temp_DJ_mean_TenDayscale'))

# 提取出历史情况下的范围
His_Pre_rate_range = Month_Areamean_Range.item().get('Pre_rate_DJ_mean_Monthscale_range')
His_Prs_range = Month_Areamean_Range.item().get('Prs_DJ_mean_Monthscale_range')
His_Temp_range = Month_Areamean_Range.item().get('Temp_DJ_mean_Monthscale_range')
His_Win_range = Month_Areamean_Range.item().get('WIN_DJ_mean_Monthscale_range')
His_RHU_range = Month_Areamean_Range.item().get('RHU_DJ_mean_Monthscale_range')
His_Runoff_range = Month_Areamean_Range.item().get('Month_mean_Runoff_range')

#print(His_Pre_rate_range[0])
#print(His_Pre_rate_range[1])
#print(His_Win_range[0])
#print(float(His_Win_range[1]))

# 检查是不是数字
#if float(His_Win_range[0]) > 0:
    #print(float(His_Win_range[0]))
    #print(float(0))
#else:
    #print(0)

print(float(His_Prs_range[0]))
print(float(His_Prs_range[1]))

Month_Prs_input = 9999
if (Month_Prs_input != 9999 and Month_Prs_input < float(His_Prs_range[0]) * 0.8) or (Month_Prs_input != 9999 and Month_Prs_input > float(His_Prs_range[1]) * 1.2):
    print("输入的压强数据超越历史阈值")
else:
    print("输入的压强数据在历史阈值内")


# 初始输入变量赋值测试
Month_Pre_input = 9999
Month_Prs_input = 9999
Month_Temp_input = 9999
Month_Win_input = 9999
Month_RHU_input = 9999
Month_RF_input = 900

# 删除对应的变量
# del Month_Areamean_DataBase.item()['Temp_DJ_mean_Monthscale']

# print(Month_Areamean_DataBase_new)

#print(Month_Areamean_DataBase)

# print(Temp_Month_DB_2)

# 显示所有键的名字
print(Month_Areamean_DataBase.item().keys())
print(TenDays_Areamean_DataBase.item().keys())


# 删除缺省变量的历史数据
if Month_Pre_input == 9999:
    del Month_Areamean_DataBase.item()['Pre_rate_DJ_mean_Monthscale']
    del TenDays_Areamean_DataBase.item()['Pre_rate_DJ_mean_TenDayscale']
if Month_Prs_input == 9999:
    del Month_Areamean_DataBase.item()['Prs_DJ_mean_Monthscale']
    del TenDays_Areamean_DataBase.item()['Prs_DJ_mean_TenDayscale']
if Month_Temp_input == 9999:
    del Month_Areamean_DataBase.item()['Temp_DJ_mean_Monthscale']
    del TenDays_Areamean_DataBase.item()['Temp_DJ_mean_TenDayscale']
if Month_Win_input == 9999:
    del Month_Areamean_DataBase.item()['WIN_DJ_mean_Monthscale']
    del TenDays_Areamean_DataBase.item()['WIN_DJ_mean_TenDayscale']
if Month_RHU_input == 9999:
    del Month_Areamean_DataBase.item()['RHU_DJ_mean_Monthscale']
    del TenDays_Areamean_DataBase.item()['RHU_DJ_mean_TenDayscale']
if Month_RF_input == 9999:
    del Month_Areamean_DataBase.item()['Month_mean_Runoff']
    del TenDays_Areamean_DataBase.item()['Tendays_mean_Runoff']

# 验证是否删除
Prs_Month_DB_1 = Month_Areamean_DataBase.item().get('Prs_DJ_mean_Monthscale')
Prs_TenDay_DB_2 = TenDays_Areamean_DataBase.item().get('Tendays_mean_Runoff')
RF_Month_DB_1 = Month_Areamean_DataBase.item().get('Month_mean_Runoff')
RF_TenDay_DB_2 = TenDays_Areamean_DataBase.item().get('Tendays_mean_Runoff')

print(Prs_Month_DB_1)
print(Prs_TenDay_DB_2)
print(RF_Month_DB_1)
print(RF_Month_DB_1)

# 获得变量的名称列表
Varbilty_last_Month = list(Month_Areamean_DataBase.item().keys())
Varbilty_last_TenDays = list(TenDays_Areamean_DataBase.item().keys())

print(list(Varbilty_last_Month))

# 为计算权重做准备
Vars_normolized_Data = {}
for Varible_name in Varbilty_last_Month:
    # 读取变量的历史数据
    Var_data = Month_Areamean_DataBase.item()[Varible_name]
    
    # 计算与输入之间的差值均方根
    if 'Pre' in Varible_name:
        minus_data = np.sqrt((Var_data - Month_Pre_input) ** 2)
    elif 'Prs' in Varible_name:
        minus_data = np.sqrt((Var_data - Month_Prs_input) ** 2)
    elif 'Temp' in Varible_name:
        minus_data = np.sqrt((Var_data - Month_Temp_input) ** 2)
    elif 'WIN' in Varible_name:
        minus_data = np.sqrt((Var_data - Month_Win_input) ** 2)                
    elif 'RHU' in Varible_name:
        minus_data = np.sqrt((Var_data - Month_RHU_input) ** 2)
    elif 'Runoff' in Varible_name:
        minus_data = np.sqrt((Var_data - Month_RF_input) ** 2)     
    # 获得几种变量归一化后的差值均方根
    Vars_normolized_Data[Varible_name] = Normalize(minus_data)

    
print(Vars_normolized_Data[Varible_name].shape)
       

# 将几种变量的归一化结果进行相加
Count = 0;
while Count < len(Varbilty_last_Month):
    if Count == 0:
        Dataset = Vars_normolized_Data[Varbilty_last_Month[Count]]
        Count += 1
    else:
        Dataset_new = Vars_normolized_Data[Varbilty_last_Month[Count]]
        Dataset = Dataset + Dataset_new
        Count += 1

# print(Count)
# print(Dataset)


# 返回最小的3个月索引（一维索引）
# 首先将二维矩阵转为一维，获取到排序后的索引下标
index = np.argsort(Dataset.ravel())[:3]

print(index)

# 将在一维得到的索引，映射到高维，得到在高维数组中的位置索引
pos = np.unravel_index(index, Dataset.shape)
pos_2D = np.column_stack(pos)

print(pos_2D)# 得到的矩阵，第一行为最小值索引，第二行为第二小值索引

print(Dataset[pos_2D[0,0],pos_2D[0,1]])
print(Dataset[pos_2D[1,0],pos_2D[1,1]])
print(Dataset[pos_2D[2,0],pos_2D[2,1]])

# 提取最相似3个月的相似度
Fit_3Monthes = [] # 新建列表
rows, cols = pos_2D.shape # 获取矩阵行列数
for i in range(rows): # 按照行来遍历
    a = Dataset[pos_2D[i,0],pos_2D[i,1]]
    Fit_3Monthes.append(a) 

# 取反的相似度
Fit_3Monthes_inverse = sum(Fit_3Monthes) - Fit_3Monthes
print(Fit_3Monthes_inverse)

# 计算权重
Weight_index = Fit_3Monthes_inverse/sum(Fit_3Monthes_inverse)


# 由于计算的三旬分配比例权重加起来并不是1，考虑只利用旬的数据计算比例(舍弃)
# 首先根据得到的最相似3个月，提取对应三旬变量情况，求和

#TenDays_Sum = {}
#rows, cols = pos_2D.shape # 获取矩阵行列数
#for Varible_name in Varbilty_last_TenDays: #首先根据变量循环得到历史数据（旬尺度）
    
    # 读取变量的历史数据(旬尺度)
#    Var_data = TenDays_Areamean_DataBase.item()[Varible_name]

#    TenDays_Sum_1 = [] # 建立一个空的列表存储计算出来的旬结果

#    for i in range(rows): # 按照相似度的索引进行
#        for m in range(1,4,1): # 对旬进行循环
#            if m == 1: # 上旬
#                b = Var_data[pos_2D[i,0],(pos_2D[i,1]-1) * 3 + m]
#            else:
#                b = Var_data[pos_2D[i,0],(pos_2D[i,1]-1) * 3 + m] + b
  
#        TenDays_Sum_1.append(b) # 存储计算出来的3旬结果

#    TenDays_Sum[Varible_name] = TenDays_Sum_1 # 最后得到一个字典结果

#print(TenDays_Sum)


# 根据历史月份分配方案，重新乘以权重得到全新的分配方案

TenDays_His_Ratio = {}
rows, cols = pos_2D.shape # 获取矩阵行列数
for Varible_name in Varbilty_last_TenDays: #首先根据变量循环得到历史数据（旬尺度）
    
    # 读取变量的历史数据(旬尺度)
    Var_data = TenDays_Areamean_DataBase.item()[Varible_name]
    # Var_data_2 = TenDays_Sum[Varible_name]

    # 根据变量情况，读取历史数据中对应的月平均数据
    if 'Pre' in Varible_name:
        Var_data_2 = Month_Areamean_DataBase.item()['Pre_rate_DJ_mean_Monthscale']
    elif 'Prs' in Varible_name:
        Var_data_2 = Month_Areamean_DataBase.item()['Prs_DJ_mean_Monthscale']
    elif 'Temp' in Varible_name:
        Var_data_2 = Month_Areamean_DataBase.item()['Temp_DJ_mean_Monthscale']
    elif 'WIN' in Varible_name:
        Var_data_2 = Month_Areamean_DataBase.item()['WIN_DJ_mean_Monthscale']               
    elif 'RHU' in Varible_name:
        Var_data_2 = Month_Areamean_DataBase.item()['RHU_DJ_mean_Monthscale']
    elif 'Runoff' in Varible_name:
        Var_data_2 = Month_Areamean_DataBase.item()['Month_mean_Runoff']     

    
    TenDays_Ratio_1 = np.ones((rows,3), dtype='float') # 建立一个空的列表存储计算出来的旬分配比例
    
    for m in range(1,4,1): # 对旬进行循环
        for i in range(rows): # 按照相似度的索引进行
            if m == 1 or m == 2: # 上中旬
                b = (Var_data[pos_2D[i,0],(pos_2D[i,1]) * 3 + m - 1]/ Var_data_2[pos_2D[i,0],pos_2D[i,1]]) * Weight_index[i]
            else:
                b = (Var_data[pos_2D[i,0],(pos_2D[i,1]) * 3 + m - 1]/ Var_data_2[pos_2D[i,0],pos_2D[i,1]]) * Weight_index[i]# 计算该旬在月数据下的比例
  
            TenDays_Ratio_1[i,m-1] = b # 存储计算出来的3旬结果

    TenDays_His_Ratio[Varible_name] = TenDays_Ratio_1 # 最后得到一个字典结果

print(TenDays_His_Ratio)



# 根据三个最小月的索引，对月尺度降水进行分布（旬尺度）

#TenDays_Areamean_Data_DJ = {} #最后利用字典存储结果
#rows, cols = pos_2D.shape # 获取矩阵行列数
#for Varible_name in Varbilty_last_TenDays: #首先根据变量循环得到历史数据（旬尺度）
    # 读取变量的历史数据
#    Var_data = TenDays_Areamean_DataBase.item()[Varible_name]
#    TenDays_Areamean_Data_1 = [] # 建立一个空的列表存储计算出来的旬结果
    
#    for m in range(1,4,1): # 对旬进行循环
#        for i in range(rows): # 按照相似度的索引进行循环
#            if i == 0:
#                b = Var_data[pos_2D[i,0],(pos_2D[i,1]-1) * 3 + m] * Weight_index[i] # 根据月尺度的索引，检索在旬的位置，然后乘以权重
#            else:
#                b = b + Var_data[pos_2D[i,0],(pos_2D[i,1]-1) * 3 + m] * Weight_index[i] # 第二个开始要加上前面的一个

#        TenDays_Areamean_Data_1.append(b) # 存储计算出来的3旬结果

#    TenDays_Areamean_Data_DJ[Varible_name] = TenDays_Areamean_Data_1 # 最后得到一个字典结果


# 重新建立分配比例，然后根据输入得到最后的结果
TenDays_Areamean_Data_DJ = {} #最后利用字典存储结果
for Varible_name in Varbilty_last_TenDays: #首先根据变量循环得到历史数据（旬尺度）
    Ratio_data = TenDays_His_Ratio[Varible_name]

    New_Ratio = np.sum(Ratio_data, axis=1)

            
    # 根据变量情况，将输入的结果重新分配
    if 'Pre' in Varible_name:
        Var_data_3 = New_Ratio * Month_Pre_input
    elif 'Prs' in Varible_name:
        Var_data_3 = New_Ratio * Month_Prs_input
    elif 'Temp' in Varible_name:
        Var_data_3 = New_Ratio * Month_Temp_input
    elif 'WIN' in Varible_name:
        Var_data_3 = New_Ratio * Month_WIN_input              
    elif 'RHU' in Varible_name:
        Var_data_3 = New_Ratio * Month_RHU_input
    elif 'Runoff' in Varible_name:
        Var_data_3 = New_Ratio * Month_RF_input       

    TenDays_Areamean_Data_DJ[Varible_name] = Var_data_3 # 最后得到一个字典结果

print(TenDays_Areamean_Data_DJ)
