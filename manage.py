import os
import webbrowser
import sqlite3

from flask import Flask


import os
import re
from pprint import pprint


illust_info_re_str = re.compile(r'(\d+)_p(\d+)\.([A-Za-z]+)')
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
                illust_id, illust_p, _ = illust_info_re_str.findall(illust_name)[0]
                illust_id = int(illust_id)
                illust_p = int(illust_p)
            except IndexError:
                pass
            else:
                try:
                    illust_dict[illust_id][illust_p] = os.path.join(dirname, illust_name)
                except KeyError:
                    illust_dict[illust_id] = {}
                    illust_dict[illust_id][illust_p] = os.path.join(dirname, illust_name)
    return illust_dict


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DATABASE=os.path.join(app.instance_path, 'PixivGUI.sqlite3'),
        DIRLIST=['D:\\picture', 'D:\\Entertainment', 'D:\gitcode\PixivSpider_GUI\info_folder']
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if not os.path.exists(app.config['DATABASE']):  # 不知道有没有更好的处理方法,在程序运行前创建数据库
        db = sqlite3.connect(app.config['DATABASE'])
        with open('app/db/schema.sql', 'rb') as f:
            db.executescript(f.read().decode('utf-8'))
        db.close()

    with app.app_context():
        app.illust_dict = make_illust_dict(get_dirname_list(app.config['DIRLIST']))

    from app import db
    db.init_app(app)

    from app import main
    app.register_blueprint(main.main)

    from app import auth
    app.register_blueprint(auth.auth)

    from app import api_v1_0
    app.register_blueprint(api_v1_0.api)  # 暂时不用，我讨厌JS
    return app


if __name__ == '__main__':
    webbrowser.open('http://localhost:4399')  # 这个地方很容易出bug
    create_app().run(port=4399)
