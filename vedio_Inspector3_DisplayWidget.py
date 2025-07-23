import sys
import time
import cv2

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QImage, QPixmap, QMouseEvent

class DisplayWidget(QWidget):
    # roi_selected = pyqtSignal(tuple)  # 信号：框选区域完成
    # start_signal = pyqtSignal()  # 信号：开始统计
    # stop_signal = pyqtSignal()   # 信号：结束统计

    def __init__(self, image_saverA ):
        super().__init__()
        self.imageContorl = image_saverA
        self._width = 640
        self._height = 480

        self.initUI()
        
        
        #让上部时间每ms更新一次
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1)  # 每1ms更新一次
        
        

        
        

    def initUI(self):
        self.setWindowTitle('Delay Measurement')

        

        self.setGeometry(0, 0, 1920, 768)  # 假设屏幕宽度1920
        main_layout = QHBoxLayout()

        # 右边布局
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)  # 设置布局内元素间距为20像素


        # 左边时间显示
        self.time_label = QLabel(self)
        self.time_label.setStyleSheet("background-color: black; color: white;")
        self.time_label.setFont(QFont('Arial', 30))  # 初始字体大小
        # 新增：设置固定尺寸为100x100
        self.time_label.setFixedSize( 1024, 150 )
        #main_layout.addWidget(self.time_label, stretch=1)
        right_layout.addWidget(self.time_label, alignment=Qt.AlignCenter)
        
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(self._width, self._height)
        right_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # 按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('开始', self)
        self.start_button.clicked.connect(self.imageContorl.start_save)

        self.stop_button = QPushButton('结束', self)
        self.stop_button.clicked.connect(self.imageContorl.stop_save)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        right_layout.addLayout(button_layout)

        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)


    #上边，更新ms
    def update_time(self):
        current_time = int(time.time() * 1000)
        self.time_label.setText(str(current_time))
        font = self.time_label.font()
        font.setPixelSize(self.time_label.height() // 2)
        self.time_label.setFont(font)

    #中间， 回放摄像头
    def set_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width


        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)        
        qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self._width, self._height, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)