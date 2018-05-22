import os
import re
from pprint import pprint


illust_info_restr = re.compile(r'(\d+)_p(\d+)\.([A-Za-z]+)')
dirname_list = ['D:\\picture', 'D:\\Entertainment', 'D:\gitcode\PixivSpider_GUI\info_folder']


def get_dirname_list(dirname_list):
    for dirname in dirname_list:
        dir_content = os.listdir(dirname)
        for item in dir_content:
            complete_path = os.path.join(dirname, item)
            if os.path.isdir(complete_path):
                dirname_list.append(complete_path)
    return dirname_list


def make_illust_dict(dirname_list):
    illust_dict = {}
    for dirname in dirname_list:
        for illust_name in os.listdir(dirname):
            try:
                illust_id, illust_p, _ = illust_info_restr.findall(illust_name)[0]
            except IndexError:
                pass
            else:
                try:
                    illust_dict[illust_id][illust_p] = os.path.join(dirname, illust_name)
                except KeyError:
                    illust_dict[illust_id] = {}
                    illust_dict[illust_id][illust_p] = os.path.join(dirname, illust_name)
    return illust_dict


dirname_list = get_dirname_list(dirname_list)
illust_dict = make_illust_dict(dirname_list)

if __name__ == '__main__':
    pprint(dirname_list)
    pprint(illust_dict)
