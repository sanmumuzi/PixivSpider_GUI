import base64
import json
import logging
from typing import List, Dict, Any, Union

from PixivSpider import PixivSpiderApi as pix_api
from flask import render_template, jsonify, request, abort, redirect, url_for

from app.db import *
from . import main

logging.basicConfig(level=logging.DEBUG)


@main.route('/')
def index():
    illust_dict: Dict[int, Dict[int, str]] = current_app.illust_dict
    illust_list: List[Dict[str, Union[int, str]]] = []
    item_num: int = 20
    for illust_id in illust_dict:
        if item_num == 0:
            break
        for illust_p in illust_dict[illust_id]:
            illust_type, illust_stream = get_illust_stream(illust_dict[illust_id][illust_p])
            illust_list.append({
                'illust_id': illust_id,
                'illust_p': illust_p,
                'illust_type': illust_type,
                'illust_stream': illust_stream
            })
        item_num -= 1
    return render_template('index.html', illust_list=illust_list)


def get_illust_stream(illust_path: str):
    illust_type = illust_path.split('.')[1]
    with open(illust_path, 'rb') as f:
        illust_stream = base64.b64encode(f.read()).decode('ascii')  # open illust stream
    return illust_type, illust_stream


def get_illust_from_pixiv(illust_id: int):
    return_dict: Dict[str, Any] = pix_api.get_a_picture(illust_id, cookies_dict=json.loads(g.user['cookies']))
    # illust_base_info_dict, save_path_list, resp_text = return_dict['illust_info']
    illust_base_info_dict = return_dict['illust_base_info']
    save_path_list = return_dict['save_path_list']
    resp_text = return_dict['resp_text']
    illust_path: str = save_path_list[0]
    illust_p = int(illust_base_info_dict['p'])
    current_app.illust_dict[illust_id] = {illust_p: illust_path}  # 更新全局变量的信息
    return illust_base_info_dict, illust_path, illust_p, resp_text


def get_illust_info_from_Pixiv(illust_id: int, resp=None):
    illust_info_dict = pix_api.get_picture_info(illust_id, resp=resp, cookies_dict=json.loads(g.user['cookies']))
    return illust_info_dict


@main.route('/illust')
def show_illust():
    try:
        illust_id = int(request.args.get('illust_id'))  # get url arguments
        illust_p = int(request.args.get('illust_p'))
    except ValueError:
        abort(404)  # illust_id, illust_p 应该是数字
    else:
        illust_p = 0 if illust_p is None else illust_p
        # illust_info = pix_api.get_picture_info(picture_id=illust_id, cookies_dict=json.loads(g.user['cookies']))
        # logging.debug(illust_info)
        try:
            illust_path = current_app.illust_dict[illust_id][illust_p]  # get illust abspath path from illust dict
        except KeyError:  # 本地有没有这个图片
            illust_path = None

        db = get_db()
        illust_base_info_dict = select_illust_base_info(db, illust_id)
        # Should be id, p, date, type
        illust_info_dict = db.execute(
            'SELECT * FROM illust_info WHERE id = ?', (illust_id,)
        ).fetchone()  # Should be id ,title, user_id, introduction

        illust_detail_resp_text = None  # html text of illust detail page.
        illust_belong_bookmark = None

        if illust_path is None:  # 本地没有这个图片
            if g.user is None:  # 当前用户必须登录
                return redirect(url_for('auth.login'))
            illust_base_info_dict, illust_path, illust_p, illust_detail_resp_text = get_illust_from_pixiv(
                illust_id)  # download illust
            db.execute(
                'INSERT OR REPLACE INTO illust (id, p, date, type) VALUES (?, ?, ?, ?)',
                (illust_base_info_dict['id'], illust_base_info_dict['p'],
                 illust_base_info_dict['date'], illust_base_info_dict['type'])
            )

            illust_info_dict_complete_sign = True
            for item in illust_info_dict.values():
                if item is None:
                    illust_info_dict_complete_sign = False
                    logging.debug('数据库中illust_info的信息不完整')
                    break

            if illust_info_dict is None or not illust_info_dict_complete_sign:  # 数据库中无这一行或数据不完整
                illust_info_dict = get_illust_info_from_Pixiv(illust_id, resp=illust_detail_resp_text)
                # 获取illust_info_dict, 覆盖

                if illust_info_dict['bookmark_num'] is not None:  # 该illust属于用户书签
                    illust_belong_bookmark = True
                    already_bookmark = db.execute(
                        'SELECT illust_id FROM bookmark_user_relation WHERE user_id = ?', (g.user['id'],)
                    ).fetchall()
                    # 获取数据库中已经记录的书签集合
                    already_bookmark_set = {bookmark_item['illust_id'] for bookmark_item in already_bookmark}
                    if illust_info_dict['bookmark_num'] not in already_bookmark_set:
                        db.execute(  # 如果当前illust是书签,但是数据库中不存在,建立书签与当前用户的对应关系
                            'INSERT INTO bookmark_user_relation (illust_id, user_id)',
                            (illust_info_dict['illust_id'], g.user['id'])
                        )
                    else:  # 数据库中存在该书签关系.
                        pass

                    db.execute(
                        'INSERT OR REPLACE INTO illust_info (id, title, user_id, introduction, bookmark_count)',
                        (illust_info_dict['illust_id'], illust_info_dict['title'], illust_info_dict['user_id'],
                         illust_info_dict['introduction'], illust_info_dict['bookmark_num'])
                    )
                else:  # 当前illust没有被加入书签
                    illust_belong_bookmark = False
                    logging.debug('{}没有被加入书签'.format(illust_info_dict['illust_id']))

                db.execute(
                    'INSERT INTO illust_info (id, title, user_id, introduction)',
                    (illust_info_dict['illust_id'], illust_info_dict['title'], illust_info_dict['user_id'],
                     illust_info_dict['introduction'])
                )
            else:  # 数据库illust_info中有该illust且数据行信息完整

            if not illust_base_info_sign:  # 数据库中没有这个信息
                user_id = pix_api.get_painter_id(picture_id=illust_id, resp=resp,
                                                 cookies_dict=json.loads(g.user['cookies']))['user_id']
                # Note: 有resp的话,picture_id会被忽略
                db.execute(
                    'INSERT INTO illust_info (id, user_id)'
                )
                db.commit()
            elif illust_base_info_dict is None:  # 本地有，数据库无
                print('10')
                pass
            elif illust_base_info_dict is not None:  # 本地有，数据库有
                print('11')
                pass

            illust_type, illust_stream = get_illust_stream(illust_path)
            return render_template('illust.html', illust_type=illust_type, illust_stream=illust_stream,
                                   illust_base_info_dict=illust_base_info_dict)
    return jsonify({'status': 'error', 'message': 'Not exist.'})

# @main.before_app_first_request
# def init_illust_dict():
#     print(current_app)
