# -*- coding: utf-8 -*-
# Nola
from PyQt5 import QtWidgets, QtCore, QtMultimedia
import sys

app = QtWidgets.QApplication(sys.argv)
url = QtCore.QUrl.fromLocalFile("../music/赛马娘/ALL/hard/∞.wav")
content = QtMultimedia.QMediaContent(url)
player = QtMultimedia.QMediaPlayer()
player.setMedia(content)
player.setVolume(50)
player.play()
sys.exit(app.exec())