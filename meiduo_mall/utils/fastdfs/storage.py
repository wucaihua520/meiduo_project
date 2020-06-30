from django.core.files.storage import Storage

from meiduo_mall import settings


class FastDFSStorage(Storage):
    def __init__(self, fdfs_base_url=None):
        """
        构造方法,可以不带参数,也可以携带参数
        :param fdfs_base_url: storage的IP
        """
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL
    """自定义文件存储系统"""
    def _open(self, name, mode='rb'):
        """
        用于打开文件
        :param name: 要打开文件的名字
        :param mode: 打开文件的方式
        :return:
        """
        pass

    def _save(self, name, content):
        """
        用于保存文件
        :param name: 保存文件的名字
        :param content: 保存文件的内容
        :return: None
        """
    def url(self, name):
        """
        返回name所指文件的绝对URL
        :param name: 要读取文件的引用: group1/M00/00/00/wKjHul7p18uAMi3NAApmwGu4ayE963.jpg
        :return:    http://192.168.199.186:8888/group1/M00/00/00/wKjHul7p18uAMi3NAApmwGu4ayE963.jpg
        """
        # return 'http://192.168.199.186:8888/' + name
        return self.fdfs_base_url + name
