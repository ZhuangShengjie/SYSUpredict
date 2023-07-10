# -*- coding: utf-8 -*-
# Time    : 2023/06/28 17:23
# Author  : Zhuang ShengJ
# File    : GetPredictFunc.py
import numpy as np
from . import DateListFunc as DLF
import os
import pygrib


class GetPredict:
    def __init__(self, date_dif, scale, mode, path_ori=os.getcwd()):
        """
        param date: 预测目标 哪一天或者哪一个月
        param scale: 预测尺度 日尺度或者旬尺度    要
        param date_dif: 起报日期 哪一天ncep的运行结果    要
        param mode: 预测模式 面平均或者格点
        """
        self.path_ori = path_ori  # 必须得英文路径
        self.clip = (22, 26, 113, 116)  # 改区域
        if scale == 'tendays' or scale =='monthly':
            # 数据库起报日期
            self.dir_data_dif = f'{path_ori}/data/database/forecast/monthly_ori/{date_dif}/'
            # 文件夹中的所有文件
            # 不一定是所有文件 listdir用dist_l_all
            self.list_dir = sorted(os.listdir(self.dir_data_dif), key=lambda x: x[19:-15])
            self.list_dir = [file for file in self.list_dir if file.endswith('.grb2')]
            # 预报时间列表
            self.key_value = [item[19:-15] for item in self.list_dir]
            if mode == 'average':
                # 所有输出
                self.all_input = self.get_all_input(self.list_dir, scale)
        elif scale == 'daily' or scale =='6hrly':
            self.dir_data_dif = f'{path_ori}/data/database/forecast/6hrly_ori/{date_dif}/'
            self.list_dir = sorted(os.listdir(self.dir_data_dif), key=lambda x: x[4:-19])
            self.list_dir = [file for file in self.list_dir if file.endswith('.grb2')]
            self.key_value = [item[4:-19] for item in self.list_dir]
            if mode == 'average':
                self.all_input = self.get_all_input(self.list_dir, scale)
        else:
            assert False, 'no such scale'

    @staticmethod
    # pygrib选择区域
    def select_grib(input_path, name, type, level=None, clip=None):
        """
        :param input_path: 选择文件路径
        :param name: 变量名
        :param type: 变量名类型
        :param level: 气压水平
        :param clip: 剪裁区域
        :return 返回单个变量的ndarry
        """
        (lat1, lat2, lon1, lon2) = clip
        try:
            grbs = pygrib.open(input_path)
        except Exception as e:
            assert False, f'先检查是否英文路径: {e}'
        # name = Geopotential Height、Relative humidity、U component of wind、V component of wind、Temperature
        # Total Precipitation、Convective precipitation、typeOfLevel=isobaricInhPa
        if level:
            var_list = grbs.select(name=name, typeOfLevel=type, level=level)
        else:
            var_list = grbs.select(name=name, typeOfLevel=type)
        array_list = []
        for grb in var_list:
            if clip:
                data, _, _ = grb.data(lat1=lat1, lat2=lat2, lon1=lon1, lon2=lon2)
            else:
                data = grb.values
            array_list.append(data)
        array_list = np.array(array_list)
        return array_list

    def get_one_data(self, file):
        clip = self.clip
        input_path = f'{self.dir_data_dif}/{file}'
        """
        get_one_data该函数处理单个grb2文件变为一个时间纬度的输入，但是lstm需要4个还需要转换
        """
        name_l = ['Geopotential Height', 'Relative humidity', 'Mean sea level pressure',
                  'Temperature', 'U component of wind', 'V component of wind']
        type_l = ['isobaricInhPa', 'isobaricInhPa', 'meanSea',
                  'isobaricInhPa', 'isobaricInhPa', 'isobaricInhPa']
        level_l = [[200, 500, 700, 850, 925], [200, 500, 700, 850, 925], None,
                   [200, 500, 700, 850, 925], [200, 500, 700, 850, 925], [200, 500, 700, 850, 925]]

        all_var = np.zeros((1, 5, 4))  # ncep的形状
        for name, type, level in zip(name_l, type_l, level_l):
            var_l = self.select_grib(input_path, name=name, type=type, level=level, clip=clip)
            print(f'{name}  >>>  {level}  >>>  shape: {var_l.shape}')
            all_var = np.concatenate([all_var, var_l], axis=0)
        all_var = all_var[1:, :, :]
        all_var[0:5] = all_var[0:5]*9.8  #  变化geo单位
        return all_var

    def get_all_input(self, list_dir, scale):
        all_input_dict = {}
        for file in list_dir:
            seq = self.get_one_data(file)
            if scale == 'tendays' or scale =='monthly':
                all_input_dict[file[19:-15]] = seq
            elif scale == 'daily' or scale == '6hrly':
                all_input_dict[file[4:-19]] = seq
        return all_input_dict

    def pr_input(self, date):
        # 降雨面平均输出
        key_value = self.key_value
        i = key_value.index(date)
        seq1 = self.all_input[key_value[i - 3]]
        seq2 = self.all_input[key_value[i - 2]]
        seq3 = self.all_input[key_value[i - 1]]
        seq4 = self.all_input[key_value[i - 0]]
        input = np.concatenate([seq1[np.newaxis, :], seq2[np.newaxis, :],
                                seq3[np.newaxis, :], seq4[np.newaxis, :], ], axis=0)
        input = np.mean(input, axis=(2, 3))
        input = input[np.newaxis, :]
        return input

    def sf_input(self, date):
        # 径流面平均输出
        key_value = self.key_value
        i = key_value.index(date)
        seq4 = self.all_input[key_value[i - 0]]
        seq4 = seq4[np.newaxis, :]
        return seq4

    def all_predict(self, date):
        # 降雨格点输出可以在这里修改降水产品的输出
        list_dir = self.list_dir
        file = [i for i in list_dir if i[4:14] == date][0]
        input_path = f'{self.dir_data_dif}/{file}'
        output = self.select_grib(input_path, 'Total Precipitation',
                                  'surface', level=None, clip=self.clip)
        return output


def get_model_input(scale, start_date, end_date, mode):
    date_l, date_l_all = DLF.date_list(scale, start_date, end_date)
    date_dif = DLF.date_dif_today(start_date)
    aa = GetPredict(date_dif, scale, mode)
    # , path_ori=r'C:\ZSJ\test_py1\SYSU_predict'
    # nn_降水输入
    data_input = None
    for date in date_l:
        if mode == 'average':
            if data_input is None:
                data_input = aa.pr_input(date)
            else:
                data_input1 = aa.pr_input(date)
                data_input = np.concatenate([data_input1, data_input], axis=0)
        elif mode == 'all':
            if data_input is None:
                try:
                    data_input = aa.all_predict(date)
                except Exception as e:
                    assert False, f"确保输入为daily格点：{e}"
            else:
                data_input1 = aa.all_predict(date)
                data_input = np.concatenate([data_input1, data_input], axis=0)
        else:
            assert False, 'no mode'
    # np.save(f'./data/forcing/{start_date}_{scale}_{mode}_pr.npy', data_input)

    # nn_径流输入
    data_input11 = None
    for date1 in date_l_all:
        if mode == 'average':
            if data_input11 is None:
                data_input11 = aa.sf_input(date1)
            else:
                data_input111 = aa.sf_input(date1)
                data_input11 = np.concatenate([data_input111, data_input11], axis=0)
        # else:
        #     assert False, 'no mode'
    # np.save(f'./data/forcing/{start_date}_{scale}_{mode}_pr.npy', data_input)
    return data_input, data_input11


def all_input_npy(start_date, end_date):
    pr_input_m, sf_input_m = get_model_input('monthly', start_date, end_date, 'average')
    pr_input_d, sf_input_d = get_model_input('daily', start_date, end_date, 'average')
    pr_input_d_a, _ = get_model_input('daily', start_date, end_date, 'all')
    np.save(f'./data/forcing/{start_date}_monthly_average_pr.npy', pr_input_m)
    np.save(f'./data/forcing/{start_date}_monthly_average_sf.npy', sf_input_m)
    np.save(f'./data/forcing/{start_date}_daily_average_pr.npy', pr_input_d)
    np.save(f'./data/forcing/{start_date}_daily_average_sf.npy', sf_input_d)
    np.save(f'./data/forcing/{start_date}_daily_all_pr.npy', pr_input_d_a)


if __name__ == '__main__':
    scale = 'daily'
    start_date = '20230704'
    end_date = None
    mode = 'average'
    date_l, _ = DLF.date_list(scale, start_date, end_date)
    date_dif = DLF.date_dif_today(start_date)
    # aa = GetPredict(date_dif, scale, mode, path_ori=r'C:\ZSJ\test_py1\SYSU_predict')
    # pr_input_m, sf_input_m = get_model_input('monthly', start_date, end_date, 'average')
    all_input_npy(start_date, end_date)



