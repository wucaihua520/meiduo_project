# 生产者( 就是 发送短信的任务/函数)
def send_sms_code():
    print('send_sms_code')

# 中间人(消息队列)


class Broker(object):
    # 任务队列
    broker_list = []

# 消费者(执行任务/函数)


class Worker(object):
    # 任务执行者

    def run(self, broker, func):
        if func in broker.broker_list:
            func()
        else:
            return 'error'

# 由Celery 将三者串联起来


class Celery(object):
    def __init__(self):
        self.broker = Broker()  # 中间人
        self.worker = Worker()  # 消费者

    def add(self, func):        # 将生产者的任务 添加到 队列中
        self.broker.broker_list.append(func)

    def work(self, func):       # 让消费者 执行 任务
        self.worker.run(self.broker, func)


app = Celery()
app.add(send_sms_code)

app.work(send_sms_code)

"""
1.断点是需要使用 小虫子模式 开运行的
2. 添加断点是需要在 函数体中加断点
    不要在函数名,类名,属性上加
3. 每一行都加断点都可以
"""
