import re

from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
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
        # 实现状态保持
        login(request, user)
        # 响应注册结果
        # return http.HttpResponse('注册成功，重定向到首页')
        return redirect(reverse('contents:index'))


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """

        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'count': count})


class MobileCountView(View):
    """判断手机号是否重新注册"""

    def get(self, request, mobile):
        """

        :param request:请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'count': count})


class LoginView(View):
    """获取登录页面"""
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        """

        :param request: 请求对象
        :return: 响应结果
        """
        # 获取参数
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseBadRequest('参数不全')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入正确的的用户名或者手机号')
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位字符的密码')
        # 认证登录用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
        # 实现状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户，浏览器回话结束就过期
            request.session.set_expiry(0)
        else:
            # 记住用户:None表示两周后过期
            request.session.set_expiry(None)

        response = redirect(reverse("contents:index"))
        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        # 清理session
        logout(request)
        # 退出登录，重定向到登录页
        response = redirect(reverse("contents:index"))
        # 退出登录时，清除cookie的username
        response.delete_cookie('username')
        return response


class UserCenterInfoView(LoginRequiredMixin, View):
    """展示用户中心信息"""
    def get(self, request):
        return render(request, "user_center_info.html")

