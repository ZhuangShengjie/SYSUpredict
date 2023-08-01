# -*- coding: utf-8 -*-
# Time    : 2023/05/23 12:55
# Author  : Zhuang ShengJ
# File    : DownloadFunc.py
import requests
from tqdm import tqdm
import time
import os
from . import DateListFunc as DLF


def download(url: str, fname: str):
    try:
        resp = requests.get(url, stream=True)
    except Exception as e:
        assert False, f'dont need vpn : {e}'
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(desc=fname, unit='iB', unit_scale=True, unit_divisor=1024,) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def download_check(url1, url2, path):
    download(url1, path)
    file_size = os.path.getsize(path)  # 获取文件大小（以字节为单位）
    if file_size < 10 * 1024:  # 如果文件大小小于10KB（10 * 1024字节）
        os.remove(path)
        download(url2, path)
        file_size = os.path.getsize(path)
        if file_size < 10 * 1024:
            os.remove(path)
            print('每月最后一天，预报可能出现问题，没有当月，从相邻日期借')
        else:
            print("save url2 use url2 download")
    else:
        print("save url1 use url1 download")


def ncep_cfs(date_dif, scale, date_l):
    """
    param date_dif: 数据下载访问ncep的日期文件夹
    param scale: 尺度  可能设置3个尺度
    param date_l: 下载文件日期长度
    param path_ori: 数据库存储相对路径
    """
    path_ori = os.getcwd()
    YY = '06'  # 起报时间
    date_dif_n = DLF.calculate_date(date_dif, -1)  # 起报时间差
    save_path_m = f'{path_ori}/data/database/forecast/monthly_ori/{date_dif}'  # 文件保存路径
    save_path_d = f'{path_ori}/data/database/forecast/6hrly_ori/{date_dif}'
    if scale == 'monthly':
    # 1、monthly download
        if not os.path.exists(save_path_m):
            os.makedirs(save_path_m)  # eg:./database/forecast/monthly_ori/20230522/
        for date_m in date_l:
            # ############## 下载文件url获取 ###################
            file = f"pgbf.01.{date_dif_n}{YY}.{date_m}.avrg.grib.grb2"
            req_url1 = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod" \
                       f"/cfs.{date_dif_n}/{YY}/monthly_grib_01/" + file  # 获取下载url
            req_url2 = f"https://www.ncei.noaa.gov/data/climate-forecast-system/access/operational-9-month-forecast" \
                       f"/monthly-means/{date_dif_n[0:4]}/{date_dif_n[0:6]}/{date_dif_n}/{date_dif_n}06/" + file
            # ############# 数据下载保存路径 ###################
            path_m = f'{save_path_m}/{file}'
            if not os.path.exists(path_m):
                download_check(req_url1, req_url2, path_m)
            else:
                file_size = os.path.getsize(path_m)
                if file_size < 16 * 1024 * 1024:
                    download_check(req_url1, req_url2, path_m)
            print(f'存储date: {date_dif} >>> 预测日期: {date_m} >>> 尺度: monthly')
            print(f'finish {file} download')
    elif scale == 'daily':
        # 2、daily download use 6hrly replace
        if not os.path.exists(save_path_d):
            os.makedirs(save_path_d)
        for date_d in date_l:
            # ############## 下载文件url获取 ###################
            file = f"pgbf{date_d}.01.{date_dif_n}{YY}.grb2"
            req_url1 = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod" \
                       f"/cfs.{date_dif_n}/{YY}/6hrly_grib_01/" + file  # 获取下载url
            req_url2 = f"https://www.ncei.noaa.gov/data/climate-forecast-system/access/operational-9-month-forecast" \
                       f"/6-hourly-by-pressure/{date_dif_n[0:4]}/{date_dif_n[0:6]}/{date_dif_n}/{date_dif_n}06/" + file
            # ############# 数据下载文件路径 ###################
            path_d = f'{save_path_d}/{file}'
            if not os.path.exists(path_d):
                download_check(req_url1, req_url2, path_d)
            else:
                file_size = os.path.getsize(path_d)
                if file_size < 16 * 1024 * 1024:
                    download_check(req_url1, req_url2, path_d)
            print(f'存储date: {date_dif} >>> 预测日期: {date_d} >>> 尺度: daily')
            print(f'finish {file} download')
    else:
        assert False, 'no such scale'


def ncep_cfs_flx(date_dif, scale, date_l):
    path_ori = os.getcwd()
    YY = '06'  # 起报时间
    date_dif_n = DLF.calculate_date(date_dif, -1)  # 起报时间差
    save_path_m = f'{path_ori}/data/database/forecast/monthly_ori/{date_dif}/flxf/'  # 文件保存路径
    save_path_d = f'{path_ori}/data/database/forecast/6hrly_ori/{date_dif}/flxf/'
    if scale == 'monthly':
        # 1、monthly download
        if not os.path.exists(save_path_m):
            os.makedirs(save_path_m)  # eg:./database/forecast/monthly_ori/20230522/
        for date_m in date_l:
            # ############## 下载文件url获取 ###################
            file = f"flxf.01.{date_dif_n}{YY}.{date_m}.avrg.grib.grb2"
            req_url1 = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod" \
                       f"/cfs.{date_dif_n}/{YY}/monthly_grib_01/" + file  # 获取下载url
            req_url2 = f"https://www.ncei.noaa.gov/data/climate-forecast-system/access/operational-9-month-forecast" \
                       f"/monthly-means/{date_dif_n[0:4]}/{date_dif_n[0:6]}/{date_dif_n}/{date_dif_n}06/" + file
            # ############# 数据下载保存路径 ###################
            path_m = f'{save_path_m}/{file}'
            if not os.path.exists(path_m):
                download_check(req_url1, req_url2, path_m)
            else:
                file_size = os.path.getsize(path_m)
                if file_size < 3 * 1024 * 1024:
                    download_check(req_url1, req_url2, path_m)
            print(f'存储date: {date_dif} >>> 预测日期: {date_m} >>> 尺度: monthly >>> 变量: flxf')
            print(f'finish {file} download')
    elif scale == 'daily':
        # 2、daily download use 6hrly replace
        if not os.path.exists(save_path_d):
            os.makedirs(save_path_d)
        for date_d in date_l:
            # ############## 下载文件url获取 ###################
            file = f"flxf{date_d}.01.{date_dif_n}{YY}.grb2"
            req_url1 = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod" \
                       f"/cfs.{date_dif_n}/{YY}/6hrly_grib_01/" + file  # 获取下载url
            req_url2 = f"https://www.ncei.noaa.gov/data/climate-forecast-system/access/operational-9-month-forecast" \
                       f"/6-hourly-flux/{date_dif_n[0:4]}/{date_dif_n[0:6]}/{date_dif_n}/{date_dif_n}06/" + file
            # ############# 数据下载文件路径 ###################
            path_d = f'{save_path_d}/{file}'
            if not os.path.exists(path_d):
                download_check(req_url1, req_url2, path_d)
            else:
                file_size = os.path.getsize(path_d)
                if file_size < 3 * 1024 * 1024:
                    download_check(req_url1, req_url2, path_d)
            print(f'存储date: {date_dif} >>> 预测日期: {date_d} >>> 尺度: daily >>> 变量: flxf')
            print(f'finish {file} download')
    else:
        assert False, 'no such scale'


def date_predict_need(date_dif, scale, date_l):
    path_ori = os.getcwd()
    YY = '06'
    if scale == 'monthly' or scale == 'tendays':
        scale = 'monthly'
        # ########## 每日数据存储路径 #############
        save_path = f'{path_ori}/data/database/forecast/{scale}_ori/{date_dif}'
        if not os.path.exists(save_path):
            os.makedirs(save_path)  # eg:./database/forecast/monthly_ori/20230522/
        for date_m in date_l:
            file = f"pgbf.01.{date_m}{YY}.{date_m[:-2]}.avrg.grib.grb2"
            req_url1 = f"https://www.ncei.noaa.gov/data/climate-forecast-system/access/operational-9-month-forecast/" \
                       f"monthly-means/{date_m[0:4]}/{date_m[0:6]}/{date_m}/{date_m}06/" + file
            date_new = DLF.calculate_date(date_m, 1)
            file_new = f"pgbf.01.{date_new }{YY}.{date_new [:-2]}.avrg.grib.grb2"
            req_url2 = f"https://www.ncei.noaa.gov/data/climate-forecast-system/access/operational-9-month-forecast/" \
                       f"monthly-means/{date_new[0:4]}/{date_new[0:6]}/{date_new}/{date_new}06/" + file_new
            # ############# 数据下载文件路径 ###################
            path = f'{save_path}/{file}'  # 可能需要修改，日期最好对上
            if not os.path.exists(path):
                download_check(req_url1, req_url2, path)
            else:
                file_size = os.path.getsize(path)
                if file_size < 16 * 1024 * 1024:
                    download_check(req_url1, req_url2, path)
            print(f'存储date: {date_dif} >>> 日期: {date_m} >>> 尺度: {scale} >>> extra')
            print(f'finish {file} download')

    elif scale == 'daily' or scale == '6hrly':
        scale = '6hrly'
        save_path = f'{path_ori}/data/database/forecast/{scale}_ori/{date_dif}'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        for date_m in date_l:
            file = f"pgbf{date_m}.01.{date_m[:-2]}{YY}.grb2"
            req_url1 = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/" \
                       f"cfs.{date_m[0:8]}/{YY}/6hrly_grib_01/{file}"  # 获取下载url
            req_url2 = f"https://www.ncei.noaa.gov/data/climate-forecast-system/access/operational-9-month-forecast/" \
                      f"6-hourly-by-pressure/{date_m[0:4]}/{date_m[0:6]}/{date_m[0:8]}/{date_m}/" + file
            # ############# 数据下载文件路径 ###################
            path = f'{save_path}/{file}'
            if not os.path.exists(path):
                download_check(req_url1, req_url2, path)
            else:
                file_size = os.path.getsize(path)
                if file_size < 16 * 1024 * 1024:
                    download_check(req_url1, req_url2, path)
            print(f'存储date: {date_dif} >>> 日期: {date_m} >>> 尺度: {scale} >>> extra')
            print(f'finish {file} download')
    else:
        assert False, 'no such scale'


def download_ncep_all(start_date, end_date, ):
    print('start <<< monthly')
    date_l_m, _ = DLF.date_list('monthly', start_date, end_date)
    date_i = DLF.date_dif_today(start_date)
    greater_list_m, smaller_list_m = DLF.date_list_div('monthly', start_date, end_date)
    ncep_cfs(date_i, 'monthly', greater_list_m)
    ncep_cfs_flx(date_i, 'monthly', greater_list_m)
    date_predict_need(date_i, 'monthly', smaller_list_m)

    print('start <<< daily')
    date_l_d, _ = DLF.date_list('daily', start_date, end_date)
    date_i = DLF.date_dif_today(start_date)
    greater_list_d, smaller_list_d = DLF.date_list_div('daily', start_date, end_date)
    ncep_cfs(date_i, 'daily', greater_list_d)
    date_predict_need(date_i, 'daily', smaller_list_d)
    ncep_cfs_flx(date_i, 'daily', greater_list_d)
    print('finish all download')


if __name__ == '__main__':
    os.chdir('C:/ZSJ/test_py1/SYSU_predict')
    download_ncep_all('20230704', None, )

