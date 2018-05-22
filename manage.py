import os
import webbrowser
import sqlite3

from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DATABASE=os.path.join(app.instance_path, 'PixivGUI.sqlite3')
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
