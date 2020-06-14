from django import http
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginRequiredJSONMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated."""

    def handle_no_permission(self):
        return http.JsonResponse({'code': 0, 'errmsg': '用户未登录'})