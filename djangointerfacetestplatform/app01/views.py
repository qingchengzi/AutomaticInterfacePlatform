from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse
# 事物
from django.db import transaction
# 下载文件
from django.http import FileResponse
from django.utils.encoding import escape_uri_path

import xlrd
import json

from app01 import models
from utils.MyModuleForm import ItModelForm
from utils.MyModuleForm import ApiModelForm
from utils import RequestHandler
# 可视化
from utils.ShowTabHandler import ShowTabOpt
# 发送邮件
from django.shortcuts import render,HttpResponse
from django.core.mail import EmailMessage


# Create your views here.


class Index(View):
    """
    项目默认首页逻辑处理
    """
    template_name = "index.html"

    def get_context(self):
        return models.It.get_all()

    def get(self, request, *args, **kwargs):
        """
        处理get请求的逻辑
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return render(request, self.template_name, {"it_obj": self.get_context()})

    def post(self, request, *args, **kwargs):
        """
        处理post请求的逻辑
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return JsonResponse({"code": 0, "message": "项目主页的post请求非法"})


class AddItem(View):
    """
    添加项目
    """
    template_name = "add_it.html"

    def get(self, request, *args, **kwargs):
        """
        处理添加项目get请求的业务逻辑
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        it_form_obj = ItModelForm()
        return render(request, self.template_name, {"it_form_obj": it_form_obj})

    def post(self, request, *args, **kwargs):
        """
        处理添加项目post请求的业务逻辑
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form_data = ItModelForm(request.POST)
        if form_data.is_valid():
            form_data.save()
            return redirect(reverse('app01:index'))
        else:
            return render(request, self.template_name, {"it_form_obj": form_data})


class DeleteIt(View):
    """
    删除项目,需要传入删除项目的id
    """

    def get(self, request, *args, **kwargs):
        """
        点击删除后传入项目id进行删除
        :param request:
        :param args:
        :param kwargs: 传入项目id {'pk':项目id}
        :return:
        """
        models.It.objects.filter(pk=kwargs.get('pk')).delete()
        return redirect(reverse('app01:index'))


class DeleteApi(View):
    """
    删除用例
    """

    def get(self, request, *args, **kwargs):
        """
        删除用例时，pk是用例的pk
        由于返回时，需要项目的pk值，这里还不能直接删除
        :param request:
        :param args:
        :param kwargs: 用例的pk
        :return:
        """
        # 用例是不能直接删除，因为删除用例后需要返回用例列表，这个时候需要用例的pk
        api_obj = models.Api.objects.filter(pk=kwargs.get("pk")).first()
        # 获取所属项目的PK
        it_obj_pk = api_obj.api_sub_it_id
        api_obj.delete()
        return redirect(reverse("app01:list_api", kwargs={"pk": it_obj_pk}))


class EditIt(View):
    """
    编辑项目,需要传入项目id
    """
    template_name = "edit_it.html"

    def get(self, request, *args, **kwargs):
        """
        处理get请求，需要将编辑项目的内容获取且填充到对应的文本框中
        :param request:
        :param args:
        :param kwargs:pk是项目的pk
        :return:
        """
        it_obj = models.It.objects.filter(pk=kwargs.get("pk")).first()
        # 编辑的时候先需要从数据库中取出数据，然后去渲染
        it_form_obj = ItModelForm(instance=it_obj)
        return render(request, self.template_name, {"it_form_obj": it_form_obj})

    def post(self, request, *args, **kwargs):
        """
        编辑项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        it_form_obj = models.It.objects.filter(pk=kwargs.get("pk")).first()
        form_data = ItModelForm(request.POST, instance=it_form_obj)
        if form_data.is_valid():
            form_data.save()
            return redirect(reverse("app01:index"))
        else:
            return render(request, self.template_name, {"it_form_obj": form_data})


class EditApi(View):
    """
    编辑测试用例,需要传入用例的pk
    """
    template_name = "edit_api.html"

    def get(self, request, *args, **kwargs):
        """
        处理get请求,需要将编辑用例的内容获取且填充到对应的文本框中
        :param request:
        :param args:
        :param kwargs:需要编辑用例的pk
        :return:
        """
        api_obj = models.Api.objects.filter(pk=kwargs.get("pk")).first()
        # 编辑的时候先需要从数据库中取出数据，然后去渲染
        api_form_obj = ApiModelForm(instance=api_obj)
        return render(request, self.template_name, {"api_form_obj": api_form_obj, "it_obj": api_obj.api_sub_it})

    def post(self, request, *args, **kwargs):
        """
        编辑用例
        :param request:
        :param args:
        :param kwargs:需要编辑用例的pk
        :return:
        """
        api_obj = models.Api.objects.filter(pk=kwargs.get("pk")).first()
        form_data = ApiModelForm(request.POST, instance=api_obj)
        if form_data.is_valid():
            # 测试用例进行编辑后，需要将是否通过，是否执行，测试报告重置为初始状态
            form_data.instance.__dict__["api_pass_status"] = 0
            form_data.instance.__dict__["api_run_status"] = 0
            form_data.instance.__dict__["api_report"] = ""
            form_data.save()
            # 返回需要传该用例所属项目的pk值回去
            return redirect(reverse("app01:list_api", kwargs={"pk": api_obj.api_sub_it_id}))
        else:
            return render(request, self.template_name, {"api_form_obj": form_data, "it_obj": api_obj.api_sub_it})


class UploadFile(View):
    """
    通过Excel文件，批量上传测试用例
    """
    template_name = "upload.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return render(request, self.template_name, {"it_obj_pk": pk})

    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if request.is_ajax():
            try:
                with transaction.atomic():  # 事物
                    file_obj = request.FILES.get("f1")  # 获取上传文件名
                    it_obj_pk = request.POST.get("it_obj_pk")  # 获取ajax传过来的项目pk
                    book_obj = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
                    sheet = book_obj.sheet_by_index(0)
                    title = sheet.row_values(0)
                    data_list = [dict(zip(title, sheet.row_values(item))) for item in range(1, sheet.nrows)]
                    for item in data_list:
                        if item.get("method") == "post":
                            item_method = 1
                        else:
                            item_method = 0
                        models.Api.objects.create(
                            api_sub_it_id=it_obj_pk,
                            api_name=item.get("title"),
                            api_desc=item.get("desc"),
                            api_url=item.get("url"),
                            api_method=item_method,
                            api_params=item.get("params"),
                            api_data=item.get("data")
                        )
                return JsonResponse({"status": 200, "path": "/app01/list_api/{0}".format(it_obj_pk)})

            except Exception as error:
                return JsonResponse({
                    "status": 500,
                    "path": "/app01/list_api/{0}".format(pk),
                    "it_obj_pk": pk,
                    "errors": "只能上传xls和xlsx文件类型,并且表格的字段要符合要求，错误详情:{0}".format(error)
                })
        return render(request, self.template_name, {"it_obj_pk": pk})


class ListApi(View):
    """
    需要传入项目pk，因为用例属于项目
    """
    template_name = "list_api.html"

    def get(self, request, *args, **kwargs):
        """
        根据项目PK，显示对应项目下面的测试用例
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pk = kwargs.get("pk")
        api_obj = models.Api.objects.filter(api_sub_it__id=pk)
        it_obj = models.It.objects.filter(pk=pk).first()
        return render(request, self.template_name, {"api_obj": api_obj, "it_obj": it_obj})

    def post(self, request, *args, **kwargs):
        ApiModelForm(request.POST)
        return redirect(reverse("app01:index"))


class AddApi(View):
    """
    添加测试用例
    """
    template_name = "add_api.html"

    def get(self, request, *args, **kwargs):
        """
        处理添加用例的get请求的逻辑
        :param request:
        :param args:
        :param kwargs:所属项目的pk
        :return:
        """
        it_obj = models.It.objects.filter(pk=kwargs.get("pk")).first()
        api_form_obj = ApiModelForm()
        return render(request, self.template_name, {"api_form_obj": api_form_obj, "it_boj": it_obj})

    def post(self, request, *args, **kwargs):
        """
        处理添加用例post请求
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pk = kwargs.get("pk")
        it_obj = models.It.objects.filter(pk=pk).first()
        form_data = ApiModelForm(request.POST)
        if form_data.is_valid():
            print(form_data.instance.__dict__)
            form_data.instance.__dict__['api_sub_it_id'] = pk
            form_data.save()
            return redirect(reverse("app01:list_api", args=(pk,)))
        else:
            return render(request, self.template_name, {"api_form_obj": form_data, "it_boj": it_obj})


def run_case(request, pk=0):
    """
    分别处理单条和多条测试用例执行
    :param request:
    :param pk:
    :return:
    """
    # 批量执行用例
    if request.is_ajax():
        chk_value = request.POST.get("chk_value")
        # 反序列化为list
        chk_value = json.loads(chk_value)
        # 数据库取pk在chk_value记录中对象
        api_list = models.Api.objects.filter(pk__in=chk_value)
        RequestHandler.run_case(api_list)
        # 执行成功后跳转到logs_list
        return JsonResponse({"path": "/app01/logs_list"})
    else:  # 执行单条测试用例
        case_obj = models.Api.objects.filter(pk=pk).first()
        RequestHandler.run_case([case_obj])
        return redirect(reverse("app01:logs_list"))


def logs_list(request):
    """
    log日志主页
    :param request:
    :return:
    """
    if request.method == "POST":
        return HttpResponse("ok")
    else:
        logs_obj = models.Logs.objects.all()
        return render(request, "log_list.html", {"logs_obj": logs_obj})


def preview(request, pk):
    """
    测试报告预览，pk是logs记录中的pk
    :param request:
    :param pk: log表中的pk
    :return:
    """
    if request.method == "POST":
        resport_pk = request.POST.get("report_pk")
        log_obj = models.Logs.objects.filter(pk=resport_pk).first()
        # 下载
        response = FileResponse(log_obj.log_report)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}.{1}"'.format(
            escape_uri_path(log_obj.log_sub_it.it_name),
            "html")
        return response
    log_obj = models.Logs.objects.filter(pk=pk).first()
    return render(request, "preview.html", {"log_obj": log_obj})


def download_case_report(request, pk):
    """
    下载单个用例的执行报告，pk是用例的pk
    :param request:
    :param pk:
    :return:
    """
    api_obj = models.Api.objects.filter(pk=pk).first()
    # 下载
    response = FileResponse(api_obj.api_report)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}.{1}"'.format(escape_uri_path(api_obj.api_name), "html")
    return response


def show_tab(request):
    """
    可视化
    :param request:
    :return:
    """
    if request.is_ajax():
        tab_obj = ShowTabOpt()
        data_dict = {}
        data_dict.update(tab_obj.pie())
        data_dict.update(tab_obj.line_simple())
        return JsonResponse(data_dict)
    else:
        return render(request,"show_tab.html")


def send_email(request):
    """
    发送带附件的邮件
    :param request:
    :return:
    """
    msg = EmailMessage(
        subject='这是带附件的邮件标题',
        body='这是带附件的邮件内容',
        from_email='tian@163.com',  # 也可以从settings中获取
        to=['1206180814@qq.com']
    )
    msg.attach_file('t2.xls')
    msg.send(fail_silently=False)
    return HttpResponse('OK')