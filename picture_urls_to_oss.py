# -*- coding:utf-8 -*-

import oss2
import requests
import re
import time
from utils import get_random_pic_name, alter

# AccessKeyID = "YourAccessKetID"
# AccessKeySecret = "YourAccessKeySecret"
# EndPoint = "YourEndPoint"
# BucketName = "YourBucketName"
# 存储前缀，可以为空，为空就存到oss根目录
NameSpaceFile = "coding3min"
# 本地放图片的文件夹
img_dic_path = "imgs"  # where is downlaod imgs
# 读取图片的目录，你应该有自己的域名的
AliHost = "https://xxx.oss-accelerate.aliyuncs.com"
# 测试数据，用来测试上传功能
# img_dic = {"https://www.baidu.com/img/bd_logo1.png?where=super": {"img": "xxxxxx.png", "oss": "https://xxxxx"},
#            "https://cdn.nlark.com/yuque/0/2019/png/358864/1565713692593-80b85b3c-a2cb-4716-839d-1b67ec576364.png"
#            "#align=left&amp;display=inline&amp;height=259&amp;name=image.png&amp;originHeight=259&amp;"
#            "originWidth=447&amp;size=53603&amp;status=done&amp;width=447#align=left&amp;display=inline&amp;"
#            "height=259&amp;originHeight=259&amp;originWidth=447&amp;status=done&amp;width=447":
#                {"img": "xxxxxx.png", "oss": "https://xxxxx"}
#            }
IMG_DIC = {}


def oss_file_name(local_name):
    """
    :param local_name: like oss.png xxx.jpg abc.jpeg, whatever
    :return: NameSpaceFile/2020/02/22/adfasdfasdfadsfasdf.jpg
    """
    Date = time.strftime('%Y/%m/%d', time.localtime(time.time()))
    if img_dic_path in local_name:
        local_name = local_name.rsplit("/")[-1]
    return "%s/%s/%s" % (NameSpaceFile, Date, local_name)


# Oss upload
def oss_upload(upload_path, src_path):
    """
    :param upload_path: after upload img name
    :param src_path:
    :return:
    """
    auth = oss2.Auth(AccessKeyID, AccessKeySecret)
    bucket = oss2.Bucket(auth, EndPoint, BucketName)
    bucket.put_object_from_file(upload_path, src_path)


def get_oss_url(name):
    result_str = "%s/%s" % (AliHost, name)
    return result_str


def download_img(pic_url):
    name = get_random_pic_name(pic_url)
    r = requests.get(pic_url, stream=True)
    f = open(img_dic_path + "/" + name, "wb")
    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
    return img_dic_path + "/" + name


def set_imgurl_from_file(url="https://cdn.nlark.com/yuque", is_sql=False, content=""):
    reg = re.compile('\(' + url + '.*?\)')
    url_markdown = reg.findall(content)
    print("markdown  len: %s " % len(url_markdown))
    for i in url_markdown:
        IMG_DIC[i[1:-1]] = {
            "img": "",
            "oss": ""
        }

    reg = re.compile(
        "\"" + url + ".*?\"")
    url_html = reg.findall(content)
    print("html len: %s " % len(url_html))
    if is_sql:
        for i in url_html:
            # 这里为什么是-2，因为存储在sql文件里的分号带有转义字符，比如 adsf.jpg\"
            IMG_DIC[i[1:-2]] = {
                "img": "",
                "oss": ""
            }
    else:
        for i in url_html:
            IMG_DIC[i[1:-1]] = {
                "img": "",
                "oss": ""
            }


if __name__ == "__main__":
    file_name = "post_2020022401.sql"
    f_obj = open(file_name, 'r+', encoding="utf-8")
    contents = f_obj.read()

    # 语雀、腾讯云+社区、新浪oss、掘金
    other_urls = ["https://cdn.nlark.com/yuque", "https://ask.qcloudimg.com", "https://tva1.sinaimg.cn",
                  "https://user-gold-cdn.xitu.io"]
    for other_url in other_urls:
        set_imgurl_from_file(other_url, is_sql=True, content=contents)

    for img_url in IMG_DIC:
        img_path = download_img(img_url)
        print(img_path)
        oss_path = oss_file_name(img_path)
        print("oss_path:%s" % oss_path)
        oss_upload(upload_path=oss_path, src_path=img_path)
        oss_url = get_oss_url(oss_path)
        IMG_DIC[img_url] = {
            "img": img_path,
            "oss": oss_url
        }
        print("oss_url: %s " % oss_url)

    for img_url in IMG_DIC:
        ali_oss = IMG_DIC[img_url].get("oss")
        if ali_oss != "":
            if ".webp" in ali_oss:
                ali_oss = ali_oss + "?x-oss-process=image/format,jpg"
            alter(file=file_name, old_str=img_url, new_str=ali_oss)
