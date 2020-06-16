import json
import re

from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from apps.users.models import User, Address
from apps.users.utils import generate_verify_email_url, check_verify_email_token
from celery_tasks.sms.tasks import logger
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin


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
            return render(request, 'register.html', {'register_error': '注册失败'})
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
        """提供个人信息界面"""
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, "user_center_info.html", context=context)


class EmailView(LoginRequiredJSONMixin, View):
    """添加邮箱"""
    def put(self, request):
        """实现添加邮箱逻辑"""
        # 接收axios
        body = request.body
        body_str = body.decode()
        data = json.loads(body_str)
        # 检验参数
        email = data.get('email')
        if not email:
            return http.HttpResponseBadRequest('缺少email参数')
        if not re.match(r"^[a-z0-9][\w\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return http.HttpResponseBadRequest('email参数有误')
        # 更新数据
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 0,
                                      'errmsg': '添加邮箱失败'})
        # 给邮箱发送链接
        # from django.core.mail import send_mail
        # # subject, message, from_email, recipient_list
        # subject = "美多商城激活邮件"
        # message = ""
        # from_email = "欢乐玩家<wu_cai_hua@163.com>"
        # # 收件人列表
        # recipient_list = ["wu_cai_hua@163.com"]
        # html_message = "<a href='http://www.huyouni.com'>戳我有惊喜</a>"
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message)
        # 异步发送验证邮件
        from celery_tasks.email.tasks import send_verify_email
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)
        # 响应添加邮箱结果
        return http.JsonResponse({"code": 0,
                                  "errmsg": "添加邮箱成功"})


class EmailActiveView(View):
    """验证邮箱"""
    def get(self, request):
        # 接收参数
        token = request.GET.get('token')
        # 校验参数: 判断token是否为空和过期,提取user
        if not token:
            return http.HttpResponseBadRequest('缺少token')
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('无效的token')
        # 修改email_active的值位true
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')
        # 返回验证结果
        # return http.HttpResponse('激活成功')
        return redirect(reverse('users:center'))


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        # 获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id": address.province_id,
                "city": address.city.name,
                "city_id": address.city_id,
                "district": address.district.name,
                "district_id": address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list
        }

        return render(request, "user_center_site.html", context)


class CreateAddressView(LoginRequiredMixin, View):
    """新增收货地址"""
    def post(self, request):
        # 判断地址上限,最多20个
        count = request.user.addresses.count()
        if count >= 20:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR,
                                      'errmsg': '超过地址上限'})
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('参数不全')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR,
                                      'errmsg': '新增地址失败'})
        # 新增地址成功,并将地址响应给前端实现局部刷新
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email
        }
        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK,
                                  'errmsg': '新增地址成功',
                                  'address': address_dict})


class DefaultAddressView(LoginRequiredJSONMixin, View):
    # 设置默认地址
    def put(self, request, address_id):
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)
            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR,
                                      'errmsg': '设置默认地址失败'})
        # 响应设置默认地址
        return http.JsonResponse({'code': RETCODE.OK,
                                  'errmsg': '设置默认地址成功'})


class UpdateDstroyAddressView(View):
    # 修改和删除地址
    def put(self, request, address_id):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR,
                                      'errmsg': '更新地址失败'})
        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address_id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK,
                                  'errmsg': '更新地址成功',
                                  'address': address_dict})

    def delete(self, request, address_id):
        # 删除地址
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)
            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR,
                                      'errmsg': '删除地址失败'})
        return http.JsonResponse({'code': RETCODE.OK,
                                  'errmsg': '删除地址成功'})


class UpdateTitleAddressView(View):
    """修改地址标题"""
    def put(self, request, address_id):
        # 获取参数
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        try:
            # 查询地址
            address = Address.objects.get(id=address_id)
            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

            # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


