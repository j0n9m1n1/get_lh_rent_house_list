from pprint import pprint
import sqlite3
from datetime import datetime
import requests
import json
import time
import sys
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys

form_class = uic.loadUiType("webEngineTest.ui")[0]


class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.add_new_tab()
        self.tabs = QWidget()

    def add_new_tab(self, qurl=QUrl('https://google.com'), label='labels'):
        browser = QWebEngineView()
        self.webSettings = browser.settings()
        self.webSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.renew_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
