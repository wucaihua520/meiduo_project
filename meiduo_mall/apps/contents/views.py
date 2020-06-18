from django.shortcuts import render

# Create your views here.
# 提供首页广告页面
from django.views import View


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

# #####################fastDFS上传图片的代码######################################
# 导入fastDFS库


# from fdfs_client.client import Fdfs_client
# 创建fastDFS客户端实例,让客户端实例加载配置文件(因为配置文件可以找到tracker server)
# client = Fdfs_client('utils/fastdfs/client.conf')
# 上传文件(使用绝对路径)
# client.upload_by_filename('/home/wch/Desktop/image/3.jpg')
# 获取上传成功之后的数据
"""getting connection <fdfs_client.connection.Connection object at 0x7f8b3142a160> 
<fdfs_client.fdfs_protol.Tracker_header object at 0x7f8b3142a128> {'Storage IP': '192.168.199.186', 'Group name': 
'group1', 'Local file name': '/home/wch/Desktop/image/3.jpg', 'Uploaded size': '665.00KB', 'Status': 'Upload 
successed.', 'Remote file_id': 'group1/M00/00/00/wKjHul7p18uAMi3NAApmwGu4ayE963.jpg'} """


