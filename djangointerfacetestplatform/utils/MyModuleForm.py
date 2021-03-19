#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tian'
__data__ = '2021/3/17 10:31'

from django.forms import ModelForm
from django.forms import widgets as wid
from app01 import models


class ItModelForm(ModelForm):
    """
    添加项目
    """

    class Meta:
        model = models.It
        fields = "__all__"
        labels = {
            "it_name": "项目名称",
            "it_desc": "项目描述",
            "it_start_time": "项目开始时间",
            "it_end_time": "项目结束时间"

        }
        error_messages = {
            "it_name": {"required": "该字段不能为空"},
            "it_desc": {"required": "该字段不能为空"},
            "it_start_time": {"required": "该字段不能为空"},
            "it_end_time": {"required": "该字段不能为空"},
        }
        widgets = {
            "it_name": wid.Input(attrs={"class": "form-control", "placeholder": "输入项目名称"}),
            "it_desc": wid.Textarea(attrs={"class": "form-control", "placeholder": "输入项目描述"}),
            "it_start_time": wid.DateInput(attrs={"class": "form-control", "type": "date"}),
            "it_end_time": wid.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class ApiModelForm(ModelForm):
    """
    添加用例
    """

    class Meta:
        model = models.Api
        fields = "__all__"
        exclude = ["api_run_status", "api_run_time", "api_pass_status", "api_report", "api_sub_it"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{0}'.format(field.label, )
