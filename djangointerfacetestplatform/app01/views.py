from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.views import View
from django.http import JsonResponse
from django.db import transaction  # 事物

import xlrd

from app01 import models
from utils.MyModuleForm import ItModelForm


# Create your views here.


class Index(View):
    """
    项目默认首页逻辑处理
    """

    def get(self, request, *args, **kwargs):
        """
        处理get请求的逻辑
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        it_obj = models.It.objects.all()
        return render(request, "index.html", {"it_obj": it_obj})

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

    def get(self, request, *args, **kwargs):
        """
        处理添加项目get请求的业务逻辑
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        it_form_obj = ItModelForm()
        return render(request, "add_it.html", {"it_form_obj": it_form_obj})

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
            return render(request, "add_it.html", {"it_form_obj": form_data})


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


class EditIt(View):
    """
    编辑项目,需要传入项目id
    """

    def get(self, request, *args, **kwargs):
        """
        处理get请求，需要将编辑项目的内容获取且填充到对应的文本框中
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        it_obj = models.It.objects.filter(pk=kwargs.get("pk")).first()
        it_form_obj = ItModelForm(instance=it_obj)  # 编辑的时候先需要从数据库中取出数据，然后去渲染
        return render(request, "edit_it.html", {"it_form_obj": it_form_obj})

    def post(self, request, *args, **kwargs):
        """
        编辑项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        it_obj = models.It.objects.filter(pk=kwargs.get("pk")).first()
        form_data = ItModelForm(request.POST, instance=it_obj)
        if form_data.is_valid():
            form_data.save()
            return redirect(reverse("app01:index"))
        else:
            return render(request, "edit_it.html", {"it_form": form_data})


class UploadFile(View):
    """
    通过Excel文件，批量上传测试用例
    """

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return render(request, "upload.html", {"it_obj_pk": pk})

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
        return render(request, "upload.html", {"it_obj_pk": pk})


class ListApi(View):
    """
    需要传入项目pk，因为用例属于项目
    """

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
        return render(request, "list_api.html", {"api_obj": api_obj, "it_obj": it_obj})
