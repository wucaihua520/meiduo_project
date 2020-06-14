import random
from venv import logger

from django import http
from django.http import HttpResponseBadRequest

from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.users.utils import check_verify_email_token
from apps.verifications import constants
from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP


class ImageCodeView(View):

    def get(self, request, uuid):
        """

        :param request: 请求对象
        :param uuid: 唯一标示图像验证码所表示的用户
        :return: image/jpeg
        """
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        # 保存图片验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # 响应图片验证码
        return http.HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):

    def get(self, request, mobile):
        """

        :param request:
        :param mobile:
        :return:
        """
        # 接收参数
        image_code = request.GET.get('image_code')
        image_code_id = request.GET.get('image_code_id')
        # 校验参数
        if not all([image_code, image_code_id]):
            return HttpResponseBadRequest('参数不全')
        # 创建连接到redis对象
        redis_conn = get_redis_connection('code')
        # 提取图形验证码
        redis_text = redis_conn.get('img_%s' % image_code_id)
        if redis_text is None:
            # 图形验证码过期或者不存在
            return HttpResponseBadRequest('图形验证码失效')
        # 删除图形验证码，避免恶意测试图形验证码
        # try:
        #     redis_conn.delete('img_%s' % image_code_id)
        # except Exception as e:
        #     logger.error(e)
        # 对比图形验证码
        # image_code_server = image_code_server.decode()  # bytes转字符串
        if image_code.lower() != redis_text.decode().lower():
            # 转小写后比较用lower()
            return HttpResponseBadRequest('输入的图形验证码有误')
        # 生成6位短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)
        # 保存短信验证码
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # # celery异步发送短信验证码
        # send_sms_code.delay(mobile, sms_code)
        # 响应结果
        return http.JsonResponse({'code': '0',
                                  'errmsg': '短信发送成功'})



