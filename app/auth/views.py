from functools import wraps
import json

from flask import (
    flash, g, render_template, request, session, url_for, redirect
)
from werkzeug.security import check_password_hash

from app.db import get_db
from . import auth
from .func import check_account


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


@auth.route('/id/<int:id>')  # 这里不合适，谁的主页都能进
@login_require
def homepage(id):

    return render_template('auth/homepage.html')


@auth.before_app_request
def load_logged_in_user():
    ps_user_id = session.get('ps_user_id')
    if ps_user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM ps_user WHERE id = ?', (ps_user_id,)
        ).fetchone()
