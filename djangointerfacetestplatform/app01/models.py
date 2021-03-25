from django.db import models


# Create your models here.

class It(models.Model):
    """
    接口项目表
    """
    it_name = models.CharField(max_length=32, default="", verbose_name="项目名称")
    it_desc = models.TextField(max_length=255, default="", verbose_name="项目描述")
    it_start_time = models.DateField(verbose_name="项目开始时间")
    it_end_time = models.DateField(verbose_name="项目结束时间")

    def __str__(self):
        return self.it_name

    class Meta:
        ordering = ["-id"]  # 列表中安装id倒序排列

    def fraction_of_coverage(self):
        """覆盖率"""
        if self.api_set.count():
            # 被除数不能为0，通过的用例数量除以用例总数，用例总数是不会为0的
            result = self.api_set.filter(
                api_pass_status=1).count() / self.api_set.count() * 100  # api_pass_status字段已通过的是1
            # 没有执行通过覆盖率就是0.0
            return "%.2f%%" % result
        else:
            return "0.00%"

    @classmethod
    def get_all(cls):
        return cls.objects.all()


class Api(models.Model):
    """
    接口用例表
    """
    api_sub_it = models.ForeignKey(to="It", verbose_name="所属接口的项目")
    api_name = models.CharField(max_length=32, default="", verbose_name="用例名称")
    api_desc = models.CharField(max_length=255, default="", verbose_name="用例描述")
    api_url = models.CharField(max_length=255, default="", verbose_name="请求的url")
    REQUEST_TYPE = [
        (0, "get"),
        (1, "post"),
    ]
    api_method = models.IntegerField(choices=REQUEST_TYPE, default=0, verbose_name="请求类型")
    api_params = models.CharField(max_length=255, default={}, verbose_name="请求参数")
    api_data = models.CharField(max_length=255, default={}, verbose_name="请求的data")
    api_expect = models.CharField(max_length=5200, default={}, verbose_name="请求的预期结果")
    api_report = models.TextField(verbose_name="报告", default="")
    api_run_time = models.DateTimeField(null=True, verbose_name="执行时间")
    API_PASS_STATUS_CHOICE = [
        (0, "未通过"),
        (1, "已通过")
    ]
    api_pass_status = models.IntegerField(choices=API_PASS_STATUS_CHOICE, default=0, verbose_name="执行是否通过")
    API_RUN_STATUS_CHOICE = [
        (0, "未执行"),
        (1, "已执行")
    ]
    api_run_status = models.IntegerField(choices=API_RUN_STATUS_CHOICE, default=0, verbose_name="是否执行")

    def __str__(self):
        return self.api_name


class Logs(models.Model):
    """
    用例执行记录
    1、所属项目
    2、执行时间
    3、执行的测试报告
    4、通过多少，失败多少，共执行了多少用例，通率是多少
    """
    log_sub_it = models.ForeignKey(to="It", verbose_name="所属接口项目")
    log_report = models.TextField(verbose_name="报告", default="")
    log_run_time = models.DateTimeField(null=True, verbose_name="log日志参数时间", auto_now_add=True)
    log_pass_count = models.IntegerField(verbose_name="通过数量")
    log_failed_count = models.IntegerField(verbose_name="失败数量")
    log_error_count = models.IntegerField(verbose_name="报错数量")
    log_run_count = models.IntegerField(verbose_name="执行用例总数")

    def pass_rate(self):
        """
        通过率 = 通过的用例 / 总用例
        :return:
        """
        if self.log_run_count:
            result = self.log_pass_count / self.log_run_count * 100
            if result:
                return "%.f%%" % (result)
            else:
                return 0
        else:
            return 0

    class Meta:
        ordering = ['-log_run_time']
