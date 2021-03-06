"""djangointerfacetestplatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from app01 import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # index页面
    url(r'^$', views.Index.as_view(), name="index"),
    # 项目表相关
    url(r'^index/$', views.Index.as_view(), name="index"),
    url(r'^add_it/$', views.AddItem.as_view(), name="add_it"),
    url(r'^delete_it(?P<pk>\d+)/$', views.DeleteIt.as_view(), name="delete_it"),
    url(r'^edit_it(?P<pk>\d+)/$', views.EditIt.as_view(), name="edit_it"),
    # excel文件批量上传测试用例
    url(r'^upload/(?P<pk>\d+)/$', views.UploadFile.as_view(), name="upload"),
    # 接口用例相关
    # 查看展示测试用例
    url(r"^list_api/(?P<pk>\d+)/$", views.ListApi.as_view(), name="list_api"),
    # 添加测试用例
    url(r"^add_api/(?P<pk>\d+)/$", views.AddApi.as_view(), name="add_api"),
    # 执行用例
    url(r"^run_case/(?P<pk>\d+)/$", views.run_case, name="run_case"),
    # 删除用例
    url(r"^delete_api/(?P<pk>\d+)/$", views.DeleteApi.as_view(), name="delete_api"),
    # 编辑用例
    url(r"^edit_api/(?P<pk>\d+)/$", views.EditApi.as_view(), name="edit_api"),

    # log日志
    url(r"^logs_list/$", views.logs_list, name="logs_list"),
    # 预览
    url(r"^preview/(?P<pk>\d+)/$", views.preview, name="preview"),
    # 下载测试报告
    url(r"^download_case_report/(?P<pk>\d+)/$", views.download_case_report, name="download_case_report"),
    # 可视化
    url(r"show_table/$",views.show_tab,name="show_tab",),
    # 发送邮件
    url(r'^send_email/', views.send_email, name="send_email"),


]
