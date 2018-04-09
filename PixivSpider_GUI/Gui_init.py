from PyQt5.QtWidgets import QMainWindow
from login import Ui_Login
from main_window import Ui_MainWindow
from PixivSpider import PixivSpiderApi as pix_api


class LoginGui(Ui_Login):
    def __init__(self):
        super(LoginGui, self).__init__()
        self.construct()

    def construct(self):
        pass


class MainGui(Ui_MainWindow):
    def __init__(self):
        super(MainGui, self).__init__()
        self.construct()

    def construct(self):
        pass


class LoginUiWindow(QMainWindow):
    def __init__(self):
        super(LoginUiWindow, self).__init__()
        self.login_ui = LoginGui()
        self.login_ui.setupUi(self)


class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()
        self.main_ui = MainGui()
        self.main_ui.setupUi(self)


class GuiLogic(object):
    def __init__(self):
        if not pix_api.check_login_status():
            self.login_ui = LoginUiWindow()
            self.login_ui.show()
        else:
            self.main_ui = MainUiWindow()
            self.main_ui.show()
