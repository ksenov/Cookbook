from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from main_okno import Ui_MainWindow
from recepty import Ui_MainWindow2
from add import Ui_MainWindow3
from skach import Ui_MainWindow4
from check_db import *
from des import *
from handler.db_handler import *

import sys
import sqlite3
import os
import youtube_dl

con = sqlite3.connect('mydata.db')

class Window1(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Window1, self).__init__()
        self.setupUi(self)
        self.btn_recepty.clicked.connect(self.go2)
        self.btn_add.clicked.connect(self.go3)
        self.btn_skach.clicked.connect(self.go4)
        self.setStyleSheet("QMainWindow{{border-image: url({});}}".format('./cok2.jpg'))

    def go2(self):
        self.wnd2 = Window2()
        self.wnd2.show()
        self.close()

    def go3(self):
        self.wnd3 = Window3()
        self.wnd3.show()
        self.close()

    def go4(self):
        self.wnd4 = Window4()
        self.wnd4.show()
        self.close()

# Окно просмотра рецептов
class Window2(QMainWindow, Ui_MainWindow2):
    def __init__(self):
        super(Window2,self).__init__()
        self.setupUi(self)
        self.btn_rec_back.clicked.connect(self.go1)
        self.pre_load()
        self.btn_enter.clicked.connect(self.load)
        self.btn_del.clicked.connect(self.deletebtn)
        self.setStyleSheet("QMainWindow{{border-image: url({});}}".format('./cok2.jpg'))


    def go1(self):
        self.wnd1 = Window1()
        self.wnd1.show()
        self.close()

    def pre_load(self):
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM data"
        )
        rows = cur.fetchall()
        self.list_rec.clear()
        self.rows = rows
        for row in range(len(rows)):
            self.list_rec.addItem(QListWidgetItem(f'{self.rows[row][1]}'))
        cur.connection.commit()

    def load(self):
        cur = con.cursor()
        cur.execute("SELECT * FROM data")
        rows = cur.fetchall()
        self.rows = rows
        text_put = self.rows[int(self.list_rec.currentRow())][2]
        self.text_rec.setText(text_put)

    def deletebtn(self):
        id = self.rows[int(self.list_rec.currentRow())][0]
        sql = f'DELETE FROM data WHERE id=?'
        cur = con.cursor()
        cur.execute(sql, (id,))
        cur.connection.commit()
        self.pre_load()

# Окно Добавления нового рецепта
class Window3(QMainWindow, Ui_MainWindow3):
    def __init__(self):
        super(Window3,self).__init__()
        self.setupUi(self)
        self.btn_add_back.clicked.connect(self.go1)
        self.btn_save.clicked.connect(self.save)

    def go1(self):
        self.wnd1 = Window1()
        self.wnd1.show()
        self.close()

    def save(self):
        cur = con.cursor()
        a = self.name_vvod.text()
        b = self.rec_vvod.toPlainText()
        cur.execute(
            f'INSERT INTO data VALUES (NULL, "{a}", "{b}")'
        )
        cur.connection.commit()



class downloader(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = None

    def run(self):
        self.mysignal.emit('Процесс скачивания запущен!!!')

        with youtube_dl.YoutubeDL({}) as ydl:
            ydl.download([self.url])

        self.mysignal.emit('Скачивание завершено!')
        self.mysignal.emit('finish')

    def init_args(self, url):
        self.url = url

# Окно скачивания с youtube
class Window4(QMainWindow, Ui_MainWindow4):
    def __init__(self):
        super(Window4, self).__init__()
        self.ui = Ui_MainWindow4
        self.setupUi(self)

        self.download_folder = None
        self.pushButton.clicked.connect(self.get_folder)
        self.pushButton_2.clicked.connect(self.start)
        self.pushButton_3.clicked.connect(self.go1)
        self.mythread = downloader()
        self.mythread.mysignal.connect(self.handler)

    def go1(self):
        self.wnd1 = Window1()
        self.wnd1.show()
        self.close()

    def start(self):
        if len(self.lineEdit.text()) > 5:
            if self.download_folder != None:
                link = self.lineEdit.text()
                self.mythread.init_args(link)
                self.mythread.start()
                self.locker(True)
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Вы не выбрали папку!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Ссылка на видео не указана!")

    def get_folder(self):
        self.download_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выбрать папку для сохранения')
        os.chdir(self.download_folder)

    def handler(self, value):
        if value == 'finish':
            self.locker(False)

        else:
            self.plainTextEdit.appendPlainText(value)

    def locker(self, lock_value):
        base = [self.pushButton, self.pushButton_2]

        for item in base:
            item.setDisabled(lock_value)




class Interface(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.ui.pushButton.clicked.connect(self.reg)
        self.ui.pushButton_2.clicked.connect(self.auth)
        self.base_line_edit = [self.ui.lineEdit, self.ui.lineEdit_2]

        self.check_db = CheckThread()
        self.check_db.mysignal.connect(self.signal_handler)
        self.check_db.mysignal2.connect(self.signal_handler2)


    # Проверка правильности ввода
    def check_input(funct):
        def wrapper(self):
            for line_edit in self.base_line_edit:
                if len(line_edit.text()) == 0:
                    return
            funct(self)
        return wrapper

    # Обработчик сигналов
    def signal_handler(self, value):
        QtWidgets.QMessageBox.about(self, 'Оповещение', value)
        if value == 'Успешная авторизация!':
            self.go1()


    def signal_handler2(self, value):
        print('111')
        self.wnd1.label_user.setText(value)


    @check_input
    def auth(self):
        name = self.ui.lineEdit.text()
        passw = self.ui.lineEdit_2.text()
        self.check_db.thr_login(name, passw)

    @check_input
    def reg(self):
        name = self.ui.lineEdit.text()
        passw = self.ui.lineEdit_2.text()
        self.check_db.thr_register(name, passw)

    def go1(self):
        self.wnd1 = Window1()
        self.wnd1.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = Interface()
    myapp.show()
    sys.exit(app.exec_())