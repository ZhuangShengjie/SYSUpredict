# -*- coding: utf-8 -*-
# Time    : 2023/06/14 21:12
# Author  : Zhuang ShengJ
# File    : DLdictFunc.py
import torch
import torch.nn as nn
import numpy as np
import os


class LstmPr(nn.Module):
    def __init__(self, input_size, out_size, hidden_size=128):
        super(LstmPr, self).__init__()  # 首先找到LstmPr的父类，就是nn.Module，LstmPr里面的对象都可以在nn.Module实现
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=4, dropout=0, batch_first=True)
        # True，输入格式(batch, seq_len, feature)，False，输入(seq_len, batch, feature) bidirectional=false  # 默认是false，代表不用双向LSTM
        self.relu = nn.ReLU()
        self.hidden_out = nn.Linear(hidden_size, out_size)
        self.h_s = None
        self.h_c = None

    def forward(self, x):  # x是输入数据集
        r_out, (h_s, h_c) = self.lstm(x)  # 如果不导入h_s和h_c，默认每次都进行0初始化
        # h_s和h_c的格式均是(num_layers * num_directions, batch, HIDDEN_SIZE) # 如果是双向LSTM，num_directions是2，单向是1
        r_out = r_out[:, -1, :]
        output = self.relu(r_out)
        output = self.hidden_out(output)
        # output = self.relu(output)
        output = torch.unsqueeze(output, dim=1)  # r_out = r_out[:, -1, :]减少纬度？
        return output


def get_model(state_dict, scale):
    if scale == 'monthly' or scale == 'tendays':
        nn_model = LstmPr(26, 7)
    elif scale == 'daily' or scale == '6hrly':
        nn_model = LstmPr(25, 7)
    else:
        assert False, 'no such scale'
    nn_model.load_state_dict(state_dict)
    nn_model.eval()
    print('model-load-successfully')
    return nn_model


def predict_model(input_data, scale, mode='average'):
    """
    :param input_data: 处理原始输入
    :param scale: 尺度
    :param mode: 模式
    :return: 输出
    注意模型更改可进行添加
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 构建访问数据的相对路径
    if mode == 'average':
        device = 'cpu'
        if scale == 'tendays' or scale == 'monthly':
            model_path = f'torch_lstm_sub_monthly.pth'
        else:
            model_path = f'torch_lstm_sub_daily.pth'
        model_path = os.path.join(current_dir, model_path)
        saved_dict = torch.load(model_path, map_location=device)
        state_dict = saved_dict['model_state_dict']

        nn_model = get_model(state_dict, scale)
        feature_params = saved_dict['feature_params']
        feature_mean = feature_params['feature_mean']
        feature_std = feature_params['feature_std']

        try:
            if scale == 'tendays' or scale == 'monthly':
                sta = (input_data - feature_mean)/feature_std
            else:
                input_data = input_data[:, :, 1:]
                sta = (input_data - feature_mean) / feature_std
        except Exception as e:
            assert False, f"检查输入daily25，monthly26, Error occurred when applying nn_model: {e}"

        sta_nn = torch.from_numpy(sta).type(torch.float32)
        model_pr = nn_model(sta_nn).detach().numpy()
        label_params = saved_dict['label_params']
        label_mean = label_params['label_mean']
        label_std = label_params['label_std']

        model_pr_new = model_pr*label_std + label_mean
        model_pr_new = np.squeeze(model_pr_new, axis=1)
        model_pr_new = np.where(model_pr_new > 0, model_pr_new, 0)
    elif mode == 'all':
        # 添加格点预测
        model_pr_new = input_data
    else:
        assert False, 'no such mode'
    return model_pr_new


if __name__ == '__main__':
    input_data = np.random.random([1, 4, 26])
    scale = 'monthly'
    output_pr = predict_model(input_data, scale)
    print('complete calculate')
