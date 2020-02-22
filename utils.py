# -*- coding:utf-8 -*-

import uuid
import os
import re


def get_random_pic_name(pic_url):
    name = uuid.uuid4().__str__().replace("-", "").upper()
    pic_types = [".bmp", ".jpg", ".png", ".tif", ".gif", ".pcx", ".tga", ".exif", ".fpx", ".svg", ".psd", ".cdr",
                 ".pcd", ".dxf", ".ufo", ".eps", ".ai", ".raw", ".WMF", ".webp"]
    for t in pic_types:
        if t in pic_url:
            return name + t
    return name + ".jpg"


# alter("file1", "admin", "password")
def alter(file, old_str, new_str):
    with open(file, "r", encoding="utf-8") as f1, open("%s.bak" % file, "w", encoding="utf-8") as f2:
        for line in f1:
            f2.write(re.sub(old_str, new_str, line))
    os.remove(file)
    os.rename("%s.bak" % file, file)
