import os
from pprint import pprint
from random import choice

from PixivSpider import PixivSpiderApi as pix_api
from PyQt5 import QtGui, QtCore, QtWidgets

from db_func import *

picture_dir = os.path.abspath(os.curdir)
picture_list = [x for x in os.listdir(picture_dir) if x.endswith(('png', 'jpg'))]
print(picture_list)




def select_one_picture(picture_dir, picture_file=None):
    if picture_file is not None:
        return os.path.join(picture_dir, picture_file)
    return os.path.join(picture_dir, choice(picture_list))


def set_a_pixmap(qt_widget, qt_picture_list=None):
    picture_file = None
    if qt_picture_list is not None:
        picture_file = qt_picture_list.currentItem().text()
        print('picture_file: ', picture_file)
        print('picture_path: ', select_one_picture(picture_dir, picture_file))
    pixmap = QtGui.QPixmap(select_one_picture(picture_dir, picture_file))
    pixmap = pixmap.scaled(qt_widget.width(), qt_widget.height(), True, QtCore.Qt.SmoothTransformation)  # 等比例缩小
    qt_widget.setAlignment(QtCore.Qt.AlignCenter)  # 居中
    qt_widget.setPixmap(pixmap)


def download_specific_picture(picture_id):
    resp_text = None
    picture_base_info_sign, associated_sign = True, True
    picture_base_info = search_picture_base_info(picture_id=picture_id)
    if picture_base_info is not None:
        base_info_dict = {
            'picture_id': picture_base_info[0],
            'p': picture_base_info[2],
            'date': picture_base_info[3],
            'file_type': picture_base_info[4]
        }
        print('数据库中有信息，但本地没有这图片，使用关键信息下载图片...')
        pix_api.get_a_picture(picture_id=picture_id, account=account, password=password,
                              info_dict=base_info_dict, dirname=picture_dir)
        print('base_info_dict: ', base_info_dict)
    else:
        picture_base_info_sign = False
        print('数据库中无信息，本地也无，使用详细页面下载图片...')
        picture_base_info, save_path, resp_text = pix_api.get_a_picture(
            picture_id=picture_id, account=account, password=password, dirname=picture_dir
        )
        print(picture_base_info)
    return picture_base_info, resp_text, picture_base_info_sign


# def get_picture_base_info(picture_id):
#     picture_base_info = search_picture_base_info(picture_id=picture_id)
#     if picture_base_info is not None:
#         base_info_dict = {
#             'picture_id': picture_base_info[0],
#             'p': picture_base_info[2],
#             'date': picture_base_info[3],
#             'file_type': picture_base_info[4]
#         }


def operate_picture_base_info(picture_base_info, resp_text, picture_base_info_sign):
    picture_id = picture_base_info[0]
    associated_sign = True
    if picture_base_info[1] is None:
        associated_sign = False
        print('图片与画师之间并没有关联...{}'.format(picture_id))
        picture_base_info[1] = pix_api.get_painter_id(picture_id=picture_id, resp=resp_text, account=account,
                                                      password=password)

    if not picture_base_info_sign:
        insert_picture_base_info_from_download(*picture_base_info)
    elif not associated_sign:
        update_picture_base_info(picture_id=picture_id, painter_id=picture_base_info[1])

    return picture_base_info[1]  # painter id


def operate_picture_info(picture_id, resp_text=None):
    # check picture info exists. 这样太消耗资源了，为了检查搜索一回，而且GUI启动搜索的时候，又得搜索一回，太消耗资源了
    if not search_picture_info(picture_id=picture_id):
        picture_info = pix_api.get_picture_info(picture_id=picture_id, resp=resp_text)
        print('picture_info: ', picture_info)
        insert_picture_info_from_picture_detail_page(*picture_info)  # 向数据库插入信息


def operate_painter_info(painter_id, qt_painter_list):
    if not check_specific_painter(painter_id):  # 数据库不存在该画师信息
        painter_info = pix_api.get_painter_info(painter_id=painter_id, account=account, password=password)
        pprint(painter_info)
        insert_painter_info(ID=painter_id, **painter_info['Profile'])  # 将painter_info插入数据库

        nickname = painter_info['Profile']['Nickname']
        item = QtWidgets.QListWidgetItem('{nickname}({painter_id})'.format(nickname=nickname, painter_id=painter_id))
        qt_painter_list.addItem(item)


def main_logic(qt_picture_list, qt_painter_list, qt_line, qt_widget, qt_table_picutre_info, qt_table_painter_info):
    id = str(qt_line.text())
    if id.find('_p') == -1:  # 找不到
        id += '_p0'
    try:
        item = qt_picture_list.findItems(id + '\..*', QtCore.Qt.MatchRegExp)[0]
        print('正则匹配之后的item: ', item.text())
    except IndexError as e:
        print(e)
        print('正则匹配失败，本地没有这张图片...')
        picture_id = id.split('_')[0]
        picture_base_info, resp_text, picture_base_info_sign = download_specific_picture(picture_id=picture_id)
        file_type = picture_base_info[4]  # get file type.
        painter_id = operate_picture_base_info(picture_base_info, resp_text, picture_base_info_sign)
        # insert picture base info to database.
        print('获取到的painter_id:', painter_id)
        operate_picture_info(picture_id=picture_id, resp_text=resp_text)
        # insert picture info to database.
        operate_painter_info(painter_id=painter_id, qt_painter_list=qt_painter_list)
        # insert painter info to database.

        item = QtWidgets.QListWidgetItem(str(id) + '.' + file_type)
        qt_picture_list.addItem(item)
    else:
        print('本地有这张图片，直接跳转...')
    # item.setSelected(True)
    # qt_picture_list.scrollToItem(item)
    qt_picture_list.setCurrentItem(item)
    set_a_pixmap(qt_widget, qt_picture_list)
    set_picture_info(qt_picture_list, qt_table_picutre_info)
    set_painter_info(qt_table_painter_info, qt_picture_list=qt_picture_list)


def set_picture_info(qt_picture_list, qt_table_picture_info):
    picture_id = qt_picture_list.currentItem().text().split('_')[0]
    picture_info = search_picture_info(picture_id=picture_id)
    if picture_info is None:
        # for x in range(qt_table_picture_info.rowCount()):
        #     qt_table_picture_info.setItem(x, 0, QtWidgets.QTableWidgetItem(''))
        #     qt_table_picture_info.resizeRowsToContents()
        qt_table_picture_info.clearContents()  # 这样也可以清除内容，但问题是大小不会变回去，不过无伤大雅
        print('数据库暂时查不到....')
    else:
        for row_num, row_data in enumerate(picture_info):
            qt_table_picture_info.setItem(row_num, 0, QtWidgets.QTableWidgetItem(str(row_data)))
        qt_table_picture_info.resizeRowsToContents()


def set_painter_info(qt_table_painter_info, qt_picture_list=None, qt_painter_list=None):
    painter_info = None
    if qt_picture_list is not None:
        picture_id = qt_picture_list.currentItem().text().split('_')[0]
        print(picture_id)
        painter_info = search_painter_info(picture_id=picture_id)
        print(painter_info)
    elif qt_painter_list is not None:
        painter_id = qt_painter_list.currentItem().text().split('(')[-1][:-1]
        painter_info = search_painter_info(painter_id=painter_id)

    if painter_info is None:
        qt_table_painter_info.clearContents()
        print('数据库暂时查不到对应画师信息....')
    else:
        painter_info = tuple(
            [(item1, item2) for item1, item2 in zip(painter_info.keys(), painter_info) if item2 is not None])
        qt_table_painter_info.setRowCount(len(painter_info))
        qt_table_painter_info.setVerticalHeaderLabels([str(x[0]) for x in painter_info])
        for row_num, row_data in enumerate([x[1] for x in painter_info]):
            qt_table_painter_info.setItem(row_num, 0, QtWidgets.QTableWidgetItem(str(row_data)))
        qt_table_painter_info.resizeRowsToContents()

    # picture_id = search_painter_info(picture_id=)
    # x = tuple([(item1, item2) for item1, item2 in zip(x.keys(), x) if item2 is not None])


def add_bookmark_button(qt_picture_list, comment=None, tag=None):
    picture_id = qt_picture_list.currentItem().text().split('_')[0]
    if pix_api.add_bookmark(picture_id=picture_id, comment=comment, tag=tag):
        print("加入书签成功......")
    else:
        print('加入书签失败......')


def get_painter_list():
    temp_list = search_all_painter()
    return [(item[1], item[0]) for item in temp_list]


def parse_painter_list():
    temp_list = get_painter_list()
    return [str(item[0]) + '(' + str(item[1]) + ')' for item in temp_list]


def get_bookmark_list():
    pass
