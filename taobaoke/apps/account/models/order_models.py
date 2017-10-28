# coding=utf-8
import datetime
from django.utils.timezone import utc

from django.db import models
from broadcast.models.user_models import TkUser


class AgentOrderStatus(models.Model):
    ## 订单状态, 记录订单是否入账了
    ## 通过 pub_alimama_data.py 维护

    order_id = models.CharField('订单id', max_length=30)
    enter_account = models.BooleanField('是否入账', default=True, null=False)


class Order(models.Model):
    # 创建时间
    create_time = models.DateTimeField()
    # 点击时间
    click_time = models.DateTimeField(null=True)
    # 商品信息
    good_info = models.CharField('商品信息', max_length=255)
    # 商品ID
    good_id = models.CharField('商品id', max_length=255)
    # 掌柜旺旺
    wangwang = models.CharField('掌柜旺旺', max_length=255)
    # 所属店铺
    shop = models.CharField('所属店铺', max_length=255)
    # 商品数
    good_num = models.IntegerField()
    # 商品单价
    good_price = models.FloatField()
    # 订单状态
    order_status = models.CharField('订单状态', max_length=255)
    # 订单类型
    order_type = models.CharField('订单类型', max_length=255)
    # 收入比率
    earning_rate = models.CharField('收入比率', max_length=255)
    # 分成比率
    share_rate = models.CharField('分成比率', max_length=255)
    # 付款金额
    pay_amount = models.FloatField()
    # 效果预估
    result_predict = models.FloatField()
    # 结算金额
    balance_amount = models.FloatField()
    # 预估收入
    money_amount = models.FloatField()
    # 结算时间
    earning_time = models.DateTimeField(null=True, blank=True)

    # 佣金比率
    commision_rate = models.CharField('佣金比率', max_length=255)
    # 佣金金额
    commision_amount = models.FloatField()

    # 显示佣金金额
    show_commision_amount = models.FloatField()
    # 显示佣金比率
    show_commision_rate = models.CharField('显示佣金比率', max_length=255)

    # 补贴比率
    subsidy_rate = models.CharField('补贴比率', max_length=255)
    # 补贴金额
    subsidy_amount = models.FloatField()
    # 补贴类型
    subsidy_type = models.CharField('补贴类型', max_length=255)
    # 成交平台
    terminalType = models.CharField('成交平台', max_length=255)
    # 第三方服务
    third_service = models.CharField('第三方服务', max_length=255)
    # 订单编号
    order_id = models.CharField('订单编号', max_length=255, unique=True)
    # 类目名称
    category_name = models.CharField('类目名称', max_length=255)
    # 来源ID
    source_id = models.CharField('来源id', max_length=255)
    # 来源媒体
    source_media = models.CharField('来源媒体', max_length=255)
    # 广告位ID
    ad_id = models.CharField('广告位id', max_length=255)
    # 广告位名称
    ad_name = models.CharField('广告位名称', max_length=255)

    # 最后更新时间
    last_update_time = models.DateTimeField(default=datetime.datetime.now)
    # 是否入账
    enter_account = models.BooleanField(default=False)

    # 计算显示出来的佣金比率
    @property
    def get_show_commision_rate(self):
        from account.models.commision_models import Commision
        try:
            commision = Commision.objects.get(user__tkuser__adzone__pid__contains=self.ad_id)
            commision_rate = commision.commision_rate
            if commision_rate == '' or commision_rate is None:
                # username = TkUser.objects.get(adzone__pid__contains=self.ad_id).user.username
                commision_rate = 0.15
        except Commision.DoesNotExist:
            commision_rate = 0.15
        show_commision_rate = str(commision_rate * 100) + ' %'
        return show_commision_rate

    # 计算显示出来的佣金
    @property
    def get_show_commision_amount(self):
        from account.models.commision_models import Commision
        try:
            commision = Commision.objects.get(user__tkuser__adzone__pid__contains=self.ad_id)
        except Commision.DoesNotExist:
            username = TkUser.objects.get(adzone__pid__contains=self.ad_id).user.username
            from rest_framework_jwt.serializers import User
            user = User.objects.get(username=username)
            commision = Commision.objects.create(user_id=str(user.id))

        show_commision_amount = self.pay_amount * commision.commision_rate
        return show_commision_amount

    def save(self, *args, **kwargs):
        # 把传过来的create_time强行转换为同样数字的utc时间
        # create_time = self.create_time.replace(tzinfo=utc)
        last_update_time = datetime.datetime.now()
        self.last_update_time = last_update_time
        return super(Order, self).save(*args, **kwargs)
