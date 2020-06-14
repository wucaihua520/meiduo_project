from apps.verifications import constants
from celery_tasks.main import celery_app
from libs.yuntongxun.sms import CCP
import logging
logger = logging.getLogger('django')


# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限


@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    """
    发送短信异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功0 或 失败-1
    """
    CCP().send_template_sms(mobile, [sms_code, constants.IMAGE_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
    # try:
    #     send_ret = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    #
    # except Exception as e:
    #     logger.error(e)
    #     # 有异常自动重试三次
    #     raise self.retry(exc=e, max_retries=3)
    # if send_ret != 0:
    #     # 有异常自动重试三次
    #     raise self.retry(exc=Exception('发送短信失败'), max_retries=3)
    #
    # return send_ret
