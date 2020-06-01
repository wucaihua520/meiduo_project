from django.shortcuts import render

# Create your views here.
# 提供首页广告页面
from django.views import View


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
