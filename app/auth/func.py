import sqlite3

from PixivSpider import PixivSpiderApi as pix_api


def check_account(pixiv_account, pixiv_password):
    return_dict = pix_api.check_login_status(account=pixiv_account, password=pixiv_password, enforce=True,
                                             return_auth_info=True)
    return return_dict


def get_bookmark_set(user_id=1):
    db = sqlite3.connect('D:\gitcode\PixivSpider_GUI\instance\PixivGUI.sqlite3')
    db.row_factory = sqlite3.Row
    illust_id_list = db.execute(
        'SELECT illust_id FROM bookmark_tag_relation WHERE user_id = ?', (user_id,)
    ).fetchall()
    illust_id_set = {item['illust_id'] for item in illust_id_list}
    return illust_id_set


def get_my_bookmark(user_id=1):
    db = sqlite3.connect('D:\gitcode\PixivSpider_GUI\instance\PixivGUI.sqlite3')
    db.row_factory = sqlite3.Row

    result = db.execute(  # 极其差的一段sql语句，放弃
        'SELECT bookmark_tag.name, illust_info.id, illust_info.title, bookmark_count.count FROM '
        '((bookmark_tag_relation left JOIN illust_info ON bookmark_tag_relation.illust_id = illust_info.id)'
        ' left JOIN bookmark_count ON bookmark_tag_relation.illust_id = bookmark_count.id)'
        ' JOIN bookmark_tag ON bookmark_tag.id = bookmark_tag_relation.tag_id;'
    )
    for i in result:
        print(i['id'], i['title'], i['count'], i['name'])


# def insert_bookmark_data(bookmark_list, illust_id_set):
#     db = sqlite3.connect('D:\gitcode\PixivSpider_GUI\instance\PixivGUI.sqlite3')
#     db.row_factory = sqlite3.Row
#     for bookmark_info in bookmark_list:
#         if bookmark_info[2] not in illust_id_set:
#         db.execute(
#             'INSERT INTO '
#         )

get_my_bookmark()
