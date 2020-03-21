from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os
import clipboard_ocr as ocr
import time, threading
# from multiprocessing import Process

class OcrGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = ocr.baidu_client_create()
        self.text = ''
        self.auto_ocr_started = False
        self.replace_punctuation = True
        self.initUI()

    def initUI(self):
        self.statusBar()

        exitAction = QAction('退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('退出程序')
        exitAction.triggered.connect(self.close)

        openAction = QAction('打开图片', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('打开本地图片进行OCR识别')
        openAction.triggered.connect(self.native_pic_ocr)

        clipboardAction = QAction('识别剪切板图片', self)
        clipboardAction.setShortcut('Ctrl+S')
        clipboardAction.setStatusTip('对剪切板的图片进行OCR识别')
        clipboardAction.triggered.connect(self.clipboard_ocr)

        removewrapAction = QAction('去掉换行', self)
        removewrapAction.setStatusTip('去掉文本中的所有换行')
        removewrapAction.triggered.connect(self.remove_wrap)

        self.auto_ocrAction = QAction('开始自动识别', self)
        self.auto_ocrAction.setStatusTip('后台自动识别并复制文字')
        self.auto_ocrAction.triggered.connect(self.auto_ocr)

        self.change_replace_punctuationAction = QAction('关闭英文标点替换', self)
        self.change_replace_punctuationAction.setStatusTip('关闭将英文标点自动替换为中文标点')
        self.change_replace_punctuationAction.triggered.connect(self.change_replace_punctuation)

        menubar = self.menuBar()
        menubar.addAction(openAction)
        menubar.addAction(clipboardAction)
        menubar.addAction(removewrapAction)
        menubar.addAction(self.change_replace_punctuationAction)
        menubar.addAction(self.auto_ocrAction)
        menubar.addAction(exitAction)
        # 用来创建窗口内的菜单栏
        menubar.setNativeMenuBar(False)

        self.widget = QWidget()

        self.lbl_seperate = QLabel('\n'+'-'*100)
        self.lbl_seperate.setAlignment(Qt.AlignCenter)
        self.textedit = QTextEdit()
        self.textedit.setMinimumHeight(300)
        self.textedit.setMaximumHeight(300)
        self.lbl_img = QLabel()
        self.lbl_img.setMaximumHeight(300)
        self.lbl_img.setAlignment(Qt.AlignCenter)
        # self.lbl_img.setMinimumHeight(300)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.textedit)
        self.vbox.addWidget(self.lbl_seperate)
        self.vbox.addWidget(self.lbl_img)

        self.widget.setLayout(self.vbox)

        self.setCentralWidget(self.widget)
        self.setWindowTitle('小龙的OCR识别软件')
        self.widget.setGeometry(0,0,600,600)
        self.setWindowIcon(QIcon(os.path.join(os.path.abspath('.'), os.path.join('icon','ocr.jpg'))))
        self.center()
        self.show()


    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def native_pic_ocr(self):
        file_path, file_type = QFileDialog.getOpenFileName(self,
                                                    '选择图片',
                                                    '',
                                                    'All Files (*);;Image files(*.jpg *.png *.jpeg *.bmp)')
        print(file_path)
        self.do_ocr_and_refresh(file_path)

    def clipboard_ocr(self):
        file_path = ocr.get_clipboard_image()
        if not file_path:
            self.statusBar().showMessage('剪切板中没有图片！')
        else:
            self.do_ocr_and_refresh(file_path)

    def do_ocr_and_refresh(self, file_path):
        self.lbl_img.setPixmap(self.scaled_pixmap(file_path))
        self.text = ocr.do_ocr(file_path, self.client, replace_punctuation=self.replace_punctuation)
        self.statusBar().showMessage('结果已复制到剪切板！')
        self.textedit.setText(self.text)

    def remove_wrap(self):
        self.text = self.text.replace('\n', '')
        ocr.set_clip_board(self.text)
        self.textedit.setText(self.text)

    def change_replace_punctuation(self):
        if self.replace_punctuation:
            self.change_replace_punctuationAction.setText('开启英文标点替换')
            self.change_replace_punctuationAction.setStatusTip('开启将英文标点自动替换为中文标点')
            self.replace_punctuation = False
        else:
            self.change_replace_punctuationAction.setText('关闭英文标点替换')
            self.change_replace_punctuationAction.setStatusTip('关闭将英文标点自动替换为中文标点')
            self.replace_punctuation = True


    def scaled_pixmap(self, file_path):
        img_pix = QPixmap(file_path)
        if img_pix.height() > 300:
            return img_pix.scaledToHeight(300)
        else:
            return img_pix

    def repeat_ocr(self):
        while self.auto_ocr_started:
            # print('test')
            time.sleep(0.5)
            # self.clipboard_ocr()
            img_path = ocr.get_clipboard_image()
            ocr.do_ocr(img_path, self.client, replace_punctuation=self.replace_punctuation)
        print('自动识别已停止！')

    def auto_ocr(self):
        if self.auto_ocr_started:
            self.auto_ocrAction.setText('开始自动识别')
            self.auto_ocrAction.setStatusTip('开始自动识别')
            self.auto_ocr_started = False
        else:
            self.auto_ocr_started = True
            self.auto_ocrAction.setText('停止自动识别')
            self.auto_ocrAction.setStatusTip('停止自动识别')
            # self.subprocess = Process(target=self.repeat_ocr)
            # self.subprocess.start()
            # self.subprocess.join()
            subthread = threading.Thread(target=self.repeat_ocr)
            subthread.start()
            # self.subthread.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OcrGui()
    app.exec_()