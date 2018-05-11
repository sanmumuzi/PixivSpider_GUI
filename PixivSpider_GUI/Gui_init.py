from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from os import path

from PixivSpider import PixivSpiderApi as PixApi

from login import Ui_Login
from main_window import Ui_MainWindow
from Gui_func import *
from db_func_back import GuiOperateDB
from setting import *


class LoginGui(Ui_Login):
    def __init__(self):
        super(LoginGui, self).__init__()
        self.construct()

    def construct(self):
        pass


class MainGui(Ui_MainWindow):
    def __init__(self):
        super(MainGui, self).__init__()

    def retranslateUi(self, MainWindow):
        super(MainGui, self).retranslateUi(MainWindow)
        self.construct()

    def construct(self):
        self.listWidget_picture.addItems(picture_list)
        self.listWidget_picture.clicked.connect(lambda: set_a_pixmap(self.label_picture, self.listWidget_picture))
        self.listWidget_picture.clicked.connect(
            lambda: set_picture_info(self.listWidget_picture, self.tableWidget_picture_info))
        self.listWidget_picture.clicked.connect(
            lambda: set_painter_info(self.tableWidget_painter_info, qt_picture_list=self.listWidget_picture))

        self.listWidget_painter.addItems(parse_painter_list())
        self.listWidget_painter.clicked.connect(
            lambda: set_painter_info(self.tableWidget_painter_info, qt_painter_list=self.listWidget_painter))

        self.pushButton_ok.clicked.connect(
            lambda: main_logic(
                self.listWidget_picture, self.listWidget_painter, self.lineEdit_id, self.label_picture,
                self.tableWidget_picture_info, self.tableWidget_painter_info
            )
        )

        self.pushButton_add_bookmark.clicked.connect(
            lambda: add_bookmark_button(
                self.listWidget_picture, self.lineEdit_comment, self.lineEdit_tag
            )
        )


class LoginUiWindow(QMainWindow):
    def __init__(self):
        super(LoginUiWindow, self).__init__()
        self.login_ui = LoginGui()
        self.login_ui.setupUi(self)
        self.login_ui.pushButton_login.clicked.connect(lambda: self.login_test())
        self.login_ui.pushButton_quit.clicked.connect(lambda: self.destroy())

    def login_success(self):
        print('fuck 登录成功...')
        self.destroy()
        self.main_ui = MainUiWindow()
        self.main_ui.show()

    def login_test(self):
        account = self.login_ui.lineEdit_account.text().strip()
        password = self.login_ui.lineEdit_password.text().strip()
        print('login测试')

        if pix_api.check_login_status(account, password):
            print('登录成功...')
            self.login_success()
        else:
            self.login_ui.lineEdit_password.clear()
            self.login_ui.label_message.setText('登录失败...')
            print('重新输入...')


class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()
        self.main_ui = MainGui()
        self.main_ui.setupUi(self)


class GuiLogic(object):
    def __init__(self):
        self.db_init()
        self.choose_ui()

    def choose_ui(self):
        if not PixApi.check_login_status():
            self.login_ui = LoginUiWindow()
            self.login_ui.show()
        else:
            self.main_ui = MainUiWindow()
            self.main_ui.show()

    @staticmethod
    def db_init():
        if not os.path.exists(db_path):
            os.makedirs(db_dirname)  # create db directory.
            create_db_and_table()  # create .sqlite3 file and all tables.


if __name__ == '__main__':
    # x = PixApi.get_painter_info(painter_id=15064871)
    # print(x)
    if not os.path.exists(db_path):
        os.makedirs(db_dirname)  # create db directory.
        instance = GuiOperateDB()  # create .sqlite3 file and all tables.
        instance.create_table()

