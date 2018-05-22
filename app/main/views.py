import base64
import json
import logging

from PixivSpider import PixivSpiderApi as pix_api
from flask import render_template, jsonify, request, abort, redirect, url_for

from app.db import *
from . import main
from .func import illust_dict

logging.basicConfig(level=logging.DEBUG)


@main.route('/')
def index():
    illust_list = []
    item_num = 20
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


def get_illust_stream(illust_path):
    illust_type = illust_path.split('.')[1]
    with open(illust_path, 'rb') as f:
        illust_stream = base64.b64encode(f.read()).decode('ascii')  # open illust stream
    return illust_type, illust_stream


@main.route('/illust')
def show_illust():
    illust_id = request.args.get('illust_id')  # get url arguments
    illust_p = request.args.get('illust_p')
    if illust_p is None:
        illust_p = str(0)

    try:
        int(illust_id)
        int(illust_p)
    except Exception:
        abort(404)  # illust_id, illust_p 应该是数字
    else:
        db = get_db()
        illust_base_info_dict = select_illust_base_info(db, illust_id)

        try:
            illust_path = illust_dict[illust_id][illust_p]  # get illust abspath path from illust dict
        except KeyError:  # 本地有没有这个图片
            illust_path = None

        if illust_path is None:  # 本地没有这个图片
            if g.user is None:  # 当前用户必须登录
                return redirect(url_for('auth.login'))
            illust_base_info_sign = illust_base_info_dict is not None
            print('0~')
            return_dict = pix_api.get_a_picture(illust_id, cookies_dict=json.loads(g.user['cookies']),
                                                return_auth_info=True)
            illust_base_info_dict, save_path_list, resp = return_dict['illust_info']
            cookies_dict_json = return_dict['auth_info']['cookies']
            token_str = return_dict['auth_info']['token']
            if g.user['cookies'] != cookies_dict_json:
                logging.info('cookies在访问之后被更新了----{}'.format(g.user['id']))

            illust_path = save_path_list[0]
            illust_p = str(illust_base_info_dict['p'])
            illust_dict[illust_id] = {illust_p: illust_path}  # 向字典中添加新的数据

            if not illust_base_info_sign:  # 数据库中没有这个信息
                user_id = pix_api.get_painter_id(picture_id=illust_id, resp=resp,
                                                 cookies_dict=json.loads(g.user['cookies']))['user_id']
                # Note: 有resp的话,picture_id会被忽略
                if g.user['cookies'] != cookies_dict_json:
                    logging.info('cookies在访问之后被更新了----{}'.format(g.user['id']))

                illust_base_info_dict['user_id'] = user_id
                print(illust_base_info_dict)
                db.execute(
                    'INSERT INTO illust (id, user_id, p, date, type) VALUES (?, ?, ?, ?, ?)',
                    (illust_base_info_dict['id'], illust_base_info_dict['user_id'], illust_base_info_dict['p'],
                     illust_base_info_dict['date'], illust_base_info_dict['type'])
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


@main.before_app_first_request
def init_illust_dict():
    print(current_app)
