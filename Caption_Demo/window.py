# coding: utf-8

import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QFileInfo
from PyQt5.QtWidgets import *
import sys
from player import *
import csv


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class Form(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 100, 900, 800)###
        self.player = CPlayer(self)
        self.playlist = []
        self.selectedList = [0]
        self.playOption = QMediaPlaylist.Sequential

        self.setWindowTitle('Audio Korean Caption')
        self.initUI()

    def initUI(self):

        vbox = QVBoxLayout()

        # 1.Play List
        box = QVBoxLayout()
        gb = QGroupBox('Play List')
        vbox.addWidget(gb)

        self.table = QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem('Title'))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem('Progress'))
        # read only
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # single row selection
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # signal
        self.table.itemSelectionChanged.connect(self.tableChanged)
        self.table.itemDoubleClicked.connect(self.tableDbClicked)
        box.addWidget(self.table)

        hbox = QHBoxLayout()
        btnAdd = QPushButton('Add List')
        btnDel = QPushButton('Del List')
        btnAdd.clicked.connect(self.addList)
        btnDel.clicked.connect(self.delList)
        hbox.addWidget(btnAdd)
        hbox.addWidget(btnDel)

        box.addLayout(hbox)
        gb.setLayout(box)

        # 2.Play Control
        box = QHBoxLayout()
        gb = QGroupBox('Play Control')
        vbox.addWidget(gb)

        text = ['◀◀', '▶', '⏸', '▶▶', '■']
        grp = QButtonGroup(self)
        for i in range(len(text)):
            btn = QPushButton(text[i], self)
            grp.addButton(btn, i)
            box.addWidget(btn)
        grp.buttonClicked[int].connect(self.btnClicked)

        # Volume
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged[int].connect(self.volumeChanged)
        box.addWidget(self.slider)
        gb.setLayout(box)

        # 3.Play Option
        box = QHBoxLayout()
        gb = QGroupBox('Play Option')
        vbox.addWidget(gb)

        str = ['current item once', 'current item in loop', 'sequential', 'loop', 'random']
        grp = QButtonGroup(self)
        for i in range(len(str)):
            btn = QRadioButton(str[i], self)
            if i == QMediaPlaylist.Sequential:
                btn.setChecked(True)
            grp.addButton(btn, i)
            box.addWidget(btn)

        grp.buttonClicked[int].connect(self.radClicked)

        gb.setLayout(box)

        # 4. Captioning Result (Eng, Kor)
        box = QVBoxLayout()
        gb = QGroupBox('자동 캡션')
        vbox.addWidget(gb)

        hbox = QHBoxLayout()
        btnCap = QPushButton('오디오 캡션 생성')
        self.capText = QTextBrowser(self)
        self.capText.resize(100,60)
        btnCap.clicked.connect(self.captionGenerator)
        hbox.addWidget(btnCap)
        hbox.addWidget(self.capText)

        box.addLayout(hbox)
        gb.setLayout(box)
        # 4 끝

        # 5. Comparing with the Evaluation Text
        box = QVBoxLayout()
        gb = QGroupBox('실제 소리 정보')
        vbox.addWidget(gb)

        hbox = QHBoxLayout()
        btnEval = QPushButton('정답 캡션')
        self.evalText = QTextBrowser(self)
        btnEval.clicked.connect(self.evalTextGenerator)
        hbox.addWidget(btnEval)
        hbox.addWidget(self.evalText)

        box.addLayout(hbox)
        gb.setLayout(box)
        # 5 끝

        # 6. 정확도? 한국어 문장 두 개를 서로 비교한 결과를 표출
        box = QVBoxLayout()
        gb = QGroupBox('정확도')
        vbox.addWidget(gb)

        hbox = QHBoxLayout()
        btnMet = QPushButton('캡션 정확도')
        self.metText = QTextBrowser(self)
        btnMet.clicked.connect(self.metTextGenerator)
        hbox.addWidget(btnMet)
        hbox.addWidget(self.metText)

        box.addLayout(hbox)
        gb.setLayout(box)
        #6 끝

        self.setLayout(vbox)
        self.show()

    def tableChanged(self):
        self.selectedList.clear()
        for item in self.table.selectedIndexes():
            self.selectedList.append(item.row())

        self.selectedList = list(set(self.selectedList))

        if self.table.rowCount() != 0 and len(self.selectedList) == 0:
            self.selectedList.append(0)
        # print(self.selectedList)

    def addList(self):
        files = QFileDialog.getOpenFileNames(self
                                             , 'Select one or more files to open'
                                             , ''
                                             , 'Sound (*.mp3 *.wav *.ogg *.flac *.wma)')


        cnt = len(files[0])
        row = self.table.rowCount()
        self.table.setRowCount(row + cnt)
        for i in range(row, row + cnt):
            self.table.setItem(i, 0, QTableWidgetItem(files[0][i - row]))
            pbar = QProgressBar(self.table)
            pbar.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(i, 1, pbar)

        self.createPlaylist()

    def delList(self):
        row = self.table.rowCount()

        index = []
        for item in self.table.selectedIndexes():
            index.append(item.row())

        index = list(set(index))
        index.reverse()
        for i in index:
            self.table.removeRow(i)

        self.createPlaylist()

    def btnClicked(self, id):

        if id == 0:  # ◀◀
            self.player.prev()
        elif id == 1:  # ▶
            if self.table.rowCount() > 0:
                self.player.play(self.playlist, self.selectedList[0], self.playOption)
        elif id == 2:  # ⏸
            self.player.pause()
        elif id == 3:  # ▶▶
            self.player.next()
        else:  # ■
            self.player.stop()

    def tableDbClicked(self, e):
        self.player.play(self.playlist, self.selectedList[0], self.playOption)

    def volumeChanged(self):
        self.player.upateVolume(self.slider.value())

    def radClicked(self, id):
        self.playOption = id
        self.player.updatePlayMode(id)

    def paintEvent(self, e):
        self.table.setColumnWidth(0, self.table.width() * 0.7)
        self.table.setColumnWidth(1, self.table.width() * 0.2)

    def createPlaylist(self):
        self.playlist.clear()
        for i in range(self.table.rowCount()):
            self.playlist.append(self.table.item(i, 0).text())

        # print(self.playlist)

    def updateMediaChanged(self, index):
        if index >= 0:
            self.table.selectRow(index)

    def updateDurationChanged(self, index, msec):
        # print('index:',index, 'duration:', msec)
        self.pbar = self.table.cellWidget(index, 1)
        if self.pbar:
            self.pbar.setRange(0, msec)

    def updatePositionChanged(self, index, msec):
        # print('index:',index, 'position:', msec)
        self.pbar = self.table.cellWidget(index, 1)
        if self.pbar:
            self.pbar.setValue(msec)

    @pyqtSlot()
    def slot_1st(self):
        self.ui.label.setText("첫번째 버튼")

    @pyqtSlot()
    def slot_2nd(self):
        self.ui.label.setText("두번째 버튼")

    @pyqtSlot()
    def slot_3rd(self):
        self.ui.label.setText("세번째 버튼")

    def captionGenerator(self):

        self.capText.clear()
        #text = open('file.txt').read()
        fullname = 'clotho_file_'
        fullname += self.player.filename
        print(fullname)

        with open("result2.csv", "r") as file:
            fileReader = csv.reader(file)
            for row in fileReader:
                if (row[0]+'.wav' == fullname):
                    #print(row[0])
                    self.capText.append(row[1])
                    self.capText.append(row[2])
            print("search fin")

    def evalTextGenerator(self):
        self.evalText.clear()
        #self.evalText.append("Real Info here")
        fullname = 'clotho_file_'
        fullname += self.player.filename
        print(fullname)

        with open("result2.csv", "r") as file:
            fileReader = csv.reader(file)
            for row in fileReader:
                if (row[0]+'.wav' == fullname):
                    self.evalText.append("caption1: " + row[3])
                    self.evalText.append(row[4] + "\n")
                    self.evalText.append("caption2: " + row[5])
                    self.evalText.append(row[6] + "\n")
                    self.evalText.append("caption3: " + row[7])
                    self.evalText.append(row[8] + "\n")
                    self.evalText.append("caption4: " + row[9])
                    self.evalText.append(row[10] + "\n")
                    self.evalText.append("caption5: " + row[11])
                    self.evalText.append(row[12])
            print("search fin")

    def metTextGenerator(self):
        self.metText.clear()
        fullname = 'clotho_file_'
        fullname += self.player.filename
        print(fullname)

        with open("result2.csv", "r") as file:
            fileReader = csv.reader(file)
            for row in fileReader:
                if (row[0]+'.wav' == fullname):
                    self.metText.append("bleu_1: " + row[13])
                    self.metText.append("bleu_2: " + row[14])
                    self.metText.append("bleu_3: " + row[15])
                    self.metText.append("bleu_4: " + row[16])
                    self.metText.append("meteor: " + row[17])
                    self.metText.append("rouge_l: " + row[18])
                    self.metText.append("cider: " + row[19])
                    self.metText.append("spice: " + row[20])
                    self.metText.append("spider: " + row[21])
            print("search fin")

if __name__ == '__main__': #main?
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())