#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tian'
__data__ = '2021/3/26 10:25'
# software: PyCharm


import os
import django
import datetime
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangointerfacetestplatform.settings")  # project_name 项目名称
django.setup()

"""
处理可视化相关
"""
from app01 import models


class ShowTabOpt:
    """
    处理图标所需要的数据
    """

    def pie(self):
        """处理饼图"""
        data = {
            "pass_pie": {
                "title": ["通过", "失败"],
                "data": [
                    {"value": 0, "name": "通过"},
                    {"value": 0, "name": "失败"}
                ]
            },
            "execute_pie": {
                "title": ["已执行", "未执行"],
                "data": [
                    {"value": 0, "name": "已执行"},
                    {"value": 0, "name": "未执行"}
                ]
            }
        }
        # 数据库取数据
        # 通过it表查
        it_obj = models.It.objects.all()  # 获取所有的项目
        for item in it_obj:
            # 已通过 和 失败
            data["pass_pie"]["data"][0]["value"] += item.api_set.filter(api_pass_status=1).count()
            data["pass_pie"]["data"][1]["value"] += item.api_set.filter(api_pass_status=0).count()
            # 已执行和未执行
            data["execute_pie"]["data"][0]["value"] += item.api_set.filter(api_run_status=1).count()
            data["execute_pie"]["data"][1]["value"] += item.api_set.filter(api_run_status=0).count()
        print(data)
        return data

    def line_simple(self):
        """折线图
        近一年，通过每个月用例数据走势图2020年3月到2021年3月,根据it_start_time进行过滤
        """
        data_dict = {
            "line_simple": {
                "title": [],
                "data": []
            }
        }
        end_time = datetime.date.today()
        # 获取去年的今天
        start_time = end_time - timedelta(days=365)
        # print(end_time,start_time)
        it_obj = models.It.objects.filter(it_start_time__range=(start_time, end_time))
        # print(it_obj)
        d = {}
        for item in it_obj:
            # print(item.it_start_time,item.api_set.count())
            m = item.it_start_time.strftime("%Y-%m")
            # print(m, item.api_set.count())
            if d.get(m, None):  # 月份存在，加value值即可
                d[m] += item.api_set.count()
            else:
                d[m] = item.api_set.count()
        # print(d.items())
        # 问题，如果根据字典key排序
        new_d = sorted(d.items(), key=lambda x: x[0])
        # print(new_d)
        for i in new_d:
            data_dict["line_simple"]["title"].append(i[0])
            data_dict["line_simple"]["data"].append(i[1])
        print(data_dict)
        return data_dict


if __name__ == '__main__':
    obj_show = ShowTabOpt()
    obj_show.line_simple()
