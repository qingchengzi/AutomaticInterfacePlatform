from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.views import View

from django.http import JsonResponse

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
        for i in it_obj:
            print(i.it_name)
            print("开始时间", i.it_start_time, type(i.it_start_time))
            print("结束时间", i.it_end_time)
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
    def get(self,request,*args,**kwargs):
        """
        点击删除后传入项目id进行删除
        :param request:
        :param args:
        :param kwargs: 传入项目id {'pk':项目id}
        :return:
        """
        models.It.objects.filter(pk=kwargs.get('pk')).delete()
        return redirect(reverse('app01:index'))


