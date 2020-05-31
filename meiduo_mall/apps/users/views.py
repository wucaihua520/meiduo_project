from django.shortcuts import render
from django.views import View


class RegisterView(View):
    def get(self, request):
        """
        
        :param request: 请求对象
        :return: 注册页面
        """
        return render(request, 'register.html')
