import re

from django import http
from django.db import DatabaseError

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from apps.users.models import User


class RegisterView(View):
    def get(self, request):
        """
        
        :param request: 请求对象
        :return: 注册页面
        """
        return render(request, 'register.html')

    def post(self, request):
        """
        实现用户注册
        :param request: 请求对象
        :return: 注册结果
        """
        # 1.获取参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # 2.校验参数
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseBadRequest('参数不全')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20位字符的用户名')
        if not re.match(r'[a-zA-Z0-9_-]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位字符的密码')
        if password2 != password:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('手机号格式输入错误')
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选协议')
        # 保存注册数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request,'register.html', {'register_error': '注册失败'})
        # 响应注册结果
        # return http.HttpResponse('注册成功，重定向到首页')
        return redirect(reverse('contents:index'))