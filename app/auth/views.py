import json
from functools import wraps
from sqlite3 import IntegrityError

from PixivSpider import PixivSpiderApi as pix_api
from flask import (
    flash, g, render_template, request, session, url_for, redirect
)

from app.db import get_db
from . import auth


def check_account(pixiv_account, pixiv_password):
    return_dict = pix_api.check_login_status(account=pixiv_account, password=pixiv_password, enforce=True,
                                             return_auth_info=True)
    return return_dict


def get_bookmark_set():
    db = get_db()
    illust_id_list = db.execute(
        'SELECT illust_id FROM bookmark_user_relation WHERE user_id = ?', (g.user['id'],)
    ).fetchall()
    illust_id_set = {item['illust_id'] for item in illust_id_list}
    return illust_id_set


def update_bookmark(bookmark_set):
    db = get_db()
    gen_bookmarks = pix_api.get_bookmarks(painter_id=g.user['id'], cookies_dict=json.loads(g.user['cookies']),
                                        token_str=g.user['token'])
    update_sign = True
    for bookmark_list in gen_bookmarks:
        for bookmark_dict in bookmark_list:
            illust_title = bookmark_dict['illust_title']
            illust_tags_list = bookmark_dict['illust_tags_list']
            illust_id = bookmark_dict['illust_id']
            user_id = bookmark_dict['user_id']
            user_name = bookmark_dict['user_name']
            bookmark_count = bookmark_dict['bookmark_num']
            if illust_id not in bookmark_set:
                try:
                    db.execute(
                        'INSERT INTO bookmark_user_relation (illust_id, user_id) VALUES (?, ?)', (illust_id, user_id)
                    )
                    db.execute(  # 插入illust_info, 但是信息可使用, 却不稳定
                        'INSERT OR IGNORE INTO illust_info (id, title, user_id, bookmark_count)'  # 冲突之后要忽略
                        ' VALUES (?, ?, ?, ?)', (illust_id, illust_title, user_id, bookmark_count)
                    )
                    db.execute('INSERT OR IGNORE INTO user (id, name) VALUES (?, ?)', (user_id, user_name))
                    for illust_tag in illust_tags_list:
                        db.execute('INSERT OR IGNORE INTO illust_tag (name) VALUES (?)', (illust_tag,))
                        illust_tag_id = \
                            db.execute('SELECT id FROM illust_tag WHERE name = ?', (illust_tag, )).fetchone()['id']
                        # 字符串的相等总觉得会慢死
                        try:
                            db.execute(
                                'INSERT INTO illust_tag_relation (illust_id, tag_id) VALUES (?, ?)',
                                (illust_id, illust_tag_id)
                            )
                        except IntegrityError:  # 实际上来说,如果illust_id不在bookmark_set中,是不会产生这个Error的.
                            update_sign = False
                            break
                except Exception:
                    raise
                else:
                    db.commit()
                    bookmark_set.add(illust_id)
            else:
                update_sign = False
                break
        if not update_sign:
            break


def get_bookmark(bookmark_set):
    db = get_db()
    bookmark_info_list = []
    for bookmark_id in bookmark_set:
        bookmark_info_dict = {}
        illust_tag_result = db.execute(
            'SELECT name FROM illust_tag WHERE id IN (SELECT tag_id FROM illust_tag_relation WHERE illust_id = ?)',
            (bookmark_id,)
        ).fetchall()
        illust_tag_set = set([illust_tag['name'] for illust_tag in illust_tag_result])  # 避免重复,如果前面出了错,这里很可能会重复
        # bookmark_info = db.execute(
        #     'SELECT illust_info.title, bookmark_count.count, user.id, user.name FROM '
        #     '(illust_info JOIN user ON illust_info.id = ? AND illust_info.user_id = user.id) '
        #     'JOIN bookmark_count ON bookmark_count.id = ?',
        #     (bookmark_id, bookmark_id)
        # ).fetchone()
        bookmark_info = db.execute(
            'SELECT illust_info.title, illust_info.bookmark_count, user.id, user.name FROM '
            'illust_info JOIN user ON illust_info.id = ? AND user.id = illust_info.user_id', (bookmark_id,)
        ).fetchone()
        bookmark_info_dict['illust_title'] = bookmark_info['title']
        bookmark_info_dict['bookmark_count'] = bookmark_info['bookmark_count']
        bookmark_info_dict['user_id'] = bookmark_info['id']
        bookmark_info_dict['user_name'] = bookmark_info['name']
        bookmark_info_dict['illust_id'] = bookmark_id
        bookmark_info_dict['illust_tag'] = illust_tag_set
        bookmark_info_list.append(bookmark_info_dict)
    return bookmark_info_list


def login_require(view_func):
    @wraps(view_func)
    # 我估计不加*args,是因为唯一一个位置参数在调度的时候已经被用了，所以实际调用的时候，不需要了
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view_func(**kwargs)

    return wrapped_view


@auth.route('/')
def test():
    return render_template('index.html')


@auth.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        pixiv_account = request.form['pixiv_account']
        pixiv_password = request.form['pixiv_password']
        db = get_db()
        error = None
        ps_user = db.execute(
            'SELECT * FROM ps_user WHERE account = ?', (pixiv_account,)
        ).fetchone()
        if ps_user is None:
            error = 'Incorrect pixiv account.'
        elif ps_user['password'] != pixiv_password:
            error = 'Incorrect pixiv password.'
        if error is None:
            session.clear()
            session['ps_user_id'] = ps_user['id']
            return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session.clear()  # server 是无权修改用户的cookie的，这里是不是把用户的cookie覆盖掉了
    return redirect(url_for('main.index'))


@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        pixiv_account = request.form['pixiv_account']
        pixiv_password = request.form['pixiv_password']
        error = None
        db = get_db()
        if not pixiv_account or not pixiv_password:
            error = 'Account and password is required.'
        elif db.execute(
                'SELECT * FROM ps_user WHERE account = ?', (pixiv_account,)
        ).fetchone() is not None:
            error = 'Account {} is already registered.'.format(pixiv_account)
        else:
            return_dict = check_account(pixiv_account, pixiv_password)
            print(pixiv_account, pixiv_password)
            from pprint import pprint
            pprint(return_dict)
            login_status = return_dict['login_status']
            ps_user_id = return_dict['auth_info']['ps_user_id']
            cookies_json_str = return_dict['auth_info']['cookies']
            token_str = return_dict['auth_info']['token']
            if not login_status:
                error = 'Failed to login in Pixiv.net, ' \
                        'Please make sure your account and password have access to pixiv.net.'
            else:
                if ps_user_id is None:
                    error = 'Failed to get pixiv user id.'

        if error is None:
            db.execute(
                'INSERT INTO ps_user (id, account, password, cookies, token) VALUES (?, ?, ?, ?, ?)',
                (ps_user_id, pixiv_account, pixiv_password, cookies_json_str, token_str)
            )
            db.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')


@auth.route('/user/<int:id>')  # 这里不合适，谁的主页都能进
@login_require
def homepage(id):
    bookmark_set = get_bookmark_set()
    if request.args.get('operate') == 'update':
        update_bookmark(bookmark_set)
    bookmark_info_list = get_bookmark(bookmark_set)
    return render_template('auth/homepage.html', bookmark_info_list=bookmark_info_list)


@auth.before_app_request
def load_logged_in_user():
    ps_user_id = session.get('ps_user_id')
    if ps_user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM ps_user WHERE id = ?', (ps_user_id,)
        ).fetchone()
