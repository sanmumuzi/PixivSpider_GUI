import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Gui_init import GuiLogic

if __name__ == '__main__':
    app = QApplication(sys.argv)
    x = GuiLogic()
    sys.exit(app.exec_())
