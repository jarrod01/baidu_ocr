from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os
import clipboard_ocr as ocr

class OcrGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = ocr.baidu_client_create()
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

        menubar = self.menuBar()
        menubar.addAction(openAction)
        menubar.addAction(clipboardAction)
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
        self.setWindowIcon(QIcon(os.path.join(os.path.abspath('.'), 'ocr.jpg')))
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
        result = ocr.do_ocr(file_path, self.client)
        self.statusBar().showMessage('结果已复制到剪切板！')
        self.textedit.setText(result)

    def scaled_pixmap(self, file_path):
        img_pix = QPixmap(file_path)
        if img_pix.height() > 300:
            return img_pix.scaledToHeight(300)
        else:
            return img_pix

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OcrGui()
    app.exec_()