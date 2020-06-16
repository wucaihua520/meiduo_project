import logging

from django.core.mail import send_mail

from celery_tasks.main import celery_app
from meiduo_mall import settings

logger = logging.getLogger('django')


@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """
    发送验证邮件
    :param self:
    :param to_email: 收件人邮箱
    :param verify_url: 验证链接
    :return: None
    """
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好!</p>' \
                   '<p>感谢您使用美多商城.</p>' \
                   '<p>您的邮箱为:%s 请点击此链接激活您的邮箱:</p>' \
                   '<p><a href="%s">%s</a></p>' %(to_email, verify_url, verify_url)
    try:
        send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        logger.error(e)
        # 有异常自动重启三次
        raise self.retry(exc=e, max_retries=3)