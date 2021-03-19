#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tian'
__data__ = '2021/3/19 11:57'
# software: PyCharm

import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangointerfacetestplatform.settings")  # project_name 项目名称
django.setup()

import datetime
import json

import unittest
import requests
from io import BytesIO  # 在内存中创建文件句柄

from deepdiff import DeepDiff
from HTMLTestRunner import HTMLTestRunner
from app01 import models

"""
作用：处理接口请求，然后生成.html类型的测试报告
"""


class MyCase(unittest.TestCase):
    """
    接口响应进行断言
    """

    def test_case(self):
        print("有没有进入啊:desc", self.desc)
        self._testMethodDoc = self.desc  # 定义用例描述
        self.assertEqual(DeepDiff(self.response, self.expect).get("values_changes", None), None, msg=self.msg)


class RequestOperate:
    """
    处理请求，更新数据库相关字段
    """

    def __init__(self, case_obj, suite_list):
        self.case_obj = case_obj
        self.suite_list = suite_list

    def handler(self):
        """
        关于请求的一些列流程
        1、提取case_obj中的字段，使用requests发请求
           1.1、对请求参数进行校验
           1.2、将请求结果提取出来
        2、使用unittest进行断言
        3、更新数据库字段
        4、将执行结果添加到日志表中
        5、前端返回
        :return:
        """
        self.send_msg()  # 发送请求

    def send_msg(self):
        """
        发送请求
        :return:
        """
        response = requests.request(
            method="get" if self.case_obj.api_method == 0 else "post",
            url=self.case_obj.api_url,
            data=self._check_data(),
            params=self._check_params()
        )
        self.assert_msg(response.json())

    def assert_msg(self, response):
        """
        处理断言
        :param response:
        :return:
        """
        case = MyCase(methodName="test_case")
        case.response = response
        case.expect = self._check_expect()
        case.msg = "自定义的错误信息:{0}".format(DeepDiff(response, self._check_expect()))
        case.title = self.case_obj.api_name  # 测试报告中显示用例名字
        case.desc = self.case_obj.api_desc  # 测试报告中显示用例的描述

        self.suite_list.addTest(case)  # 添加到我们的self.suite_list
        suite = unittest.TestSuite()  # 当前用例的suite
        suite.addTest(case)
        self.create_single_report(suite)

    def create_single_report(self, suite):
        """
        生成单个用例报告
        :param suite:用例集
        :return:
        """
        f = BytesIO()
        result = HTMLTestRunner(
            stream=f,
            title=self.case_obj.api_name,
            description=self.case_obj.api_desc,
        ).run(suite)
        self.update_api_status(result, f)

    def create_m_report(self, suite):
        """
        生成批量用例报告
        :param suite:
        :return:
        """
        f = BytesIO()
        # print("多个测试用例的报告", suite)
        result = HTMLTestRunner(
            stream=f,
            # verbosity=2,
            title=self.case_obj.api_name,
            description=self.case_obj.api_desc,
        ).run(suite)
        self.update_log_status(result, f)

    def update_log_status(self, result, f):
        """
        批量执行用例时才更新Log表
        :param result:
        :param f:
        :return:
        """
        models.Logs.objects.create(
            # log_report=self.read_file(),  # 拿到的是a.html即测试报告
            log_report=f.getvalue(),  # 写到内存在，使用getvalue()获取里面的值
            log_sub_it_id=self.case_obj.api_sub_it_id,
            log_pass_count=result.__dict__["success_count"],
            log_error_count=result.__dict__["error_count"],
            log_failed_count=result.__dict__["failure_count"],
            log_run_count=result.__dict__["testsRun"]
        )

    def update_api_status(self, result, f):
        """
        更新数据库相关字段的状态
        1、api_report
        2、api_run_time
        3、api_pass_status
        4、api_run_status

        :param result:
        :param f:
        :return:
        """
        # 写报告
        obj = models.Api.objects.filter(pk=self.case_obj.pk).first()
        obj.api_report = f.getvalue()
        # 写执行时间
        obj.api_run_time = datetime.datetime.now()
        # 是否执行用例
        obj.api_run_status = 1
        # 写api_pass_status 通过状态
        for i in result.__dict__['result']:
            if i[0]:  # i[0] = 0 用例执行通过,i[0] = 1 失败
                obj.api_pass_status = 0
            else:
                obj.api_pass_status = 1
        obj.save()

    def _check_expect(self):
        """
        处理预期值
        :return:
        """
        if self.case_obj.api_expect:
            return json.loads(self.case_obj.api_expect)
        else:
            return {}

    def _check_data(self):
        """
        校验请求的data参数
            默认，数据库中的data字段是标准的json串
        :return:
        """
        if self.case_obj.api_data:
            return json.loads(self.case_obj.api_data)
        else:
            return {}

    def _check_params(self):
        """
        校验请求的params参数
        默认：数据库中的data字段是标准的json串
        :return:
        """
        if self.case_obj.api_params:
            return json.loads(self.case_obj.api_params)
        else:
            return {}


def run_case(api_list):
    """
    批量执行用例，单独执行用例安卓批量执行来处理
    :param api_list: 列表
    :return:
    """
    # 创建测试套件对象
    suite_list = unittest.TestSuite()
    for i in api_list:
        RequestOperate(case_obj=i, suite_list=suite_list).handler()
    # 多个用例生成测试报告
    RequestOperate(case_obj=i, suite_list=suite_list).create_m_report(suite_list)


if __name__ == '__main__':

    suite_list = unittest.TestSuite()
    api_list = models.Api.objects.filter(pk__in=['1', '2'])
    for i in api_list:
        RequestOperate(case_obj=i, suite_list=suite_list).handler()
    print("数据库中获取的值:", api_list)
