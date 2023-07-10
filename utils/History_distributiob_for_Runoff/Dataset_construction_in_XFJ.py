
# coding=utf-8
# 根据提取出来的数据库数据，尝试读取进PY

import h5py
import numpy as np

file_name_1 = 'Month_Areamean_DataBase_BPZ_out.mat'
file_name_2 = 'Month_Areamean_Range_BPZ_out.mat'
file_name_3 = 'TenDayscale_Areamean_DataBase_BPZ_out.mat'

# 读取流域平均变量（月尺度）的历史数据范围
# 读取得到的应该是一种字典类型，按照字典类型的进行索引
Month_Areamean_Range = h5py.File(file_name_2,'r+') # 后面为文件读取的模式，包括'r', 'r+', 'w', 'w-'/'x', 'a'

Month_Areamean_Range_new = {}
for VariBPZ_oute_name in Month_Areamean_Range.keys():
    a = Month_Areamean_Range[VariBPZ_oute_name]
    Month_Areamean_Range_new[VariBPZ_oute_name] = np.matrix(a) # 这里要转为矩阵，不然保存下来的只是几个字符串

# 由于就只有一维数据，所以没有转置的问题
np.save('Month_Areamean_Range_BPZ_out.npy', Month_Areamean_Range_new)


# 读取流域平均变量（月尺度）数据
Month_Areamean_DataBase = h5py.File(file_name_1,'r') # 后面为文件读取的模式，包括'r', 'r+', 'w', 'w-'/'x', 'a'

print(Month_Areamean_DataBase.keys()) # 我设置的几个matlab变量就成了字典里面的键

# 注意，这里看到的shape信息与你在matlab打开的不同
# 这里的矩阵是matlab打开时矩阵的转置
# 所以，我们需要将它转置回来
# 由于存在转置问题，因此通过循环将所有的二维列表转置一遍

Month_Areamean_DataBase_new = {}
for VariBPZ_oute_name in Month_Areamean_DataBase.keys():
    a = Month_Areamean_DataBase[VariBPZ_oute_name] # 可以通过键-值对的方式进行索引，得到的是一个二维的列表
    Month_Areamean_DataBase_new[VariBPZ_oute_name] = np.transpose(a)
# 再将其存为npy格式文件
np.save('Month_Areamean_DataBase_BPZ_out.npy', Month_Areamean_DataBase_new)


# 尝试验证转换的正确性
# print(Month_Areamean_DataBase_new.keys())

# b = Month_Areamean_DataBase_new['WIN_DJ_mean_Monthscale']
# print(b.shape)

# 读取矩阵特定位置数值
# print(b[1,1])



# 读取流域平均变量（旬尺度）数据
TenDays_Areamean_DataBase = h5py.File(file_name_3,'r') # 后面为文件读取的模式，包括'r', 'r+', 'w', 'w-'/'x', 'a'

print(TenDays_Areamean_DataBase.keys()) # 我设置的几个matlab变量就成了字典里面的键

# 注意，这里看到的shape信息与你在matlab打开的不同
# 这里的矩阵是matlab打开时矩阵的转置
# 所以，我们需要将它转置回来
# 由于存在转置问题，因此通过循环将所有的二维列表转置一遍

TenDays_Areamean_DataBase_new = {}
for VariBPZ_oute_name in TenDays_Areamean_DataBase.keys():
    a = TenDays_Areamean_DataBase[VariBPZ_oute_name] # 可以通过键-值对的方式进行索引，得到的是一个二维的列表
    TenDays_Areamean_DataBase_new[VariBPZ_oute_name] = np.transpose(a)
# 再将其存为npy格式文件
np.save('TenDayscale_Areamean_DataBase_BPZ_out.npy', TenDays_Areamean_DataBase_new)



# 保存为npy文件，读取方便
# matrix = np.load('yourfile.npy')
