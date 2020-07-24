from pprint import pprint
import sqlite3
from datetime import datetime
import requests
import json
import sys
import geohash2
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import webbrowser

form_class = uic.loadUiType("html_js.ui")[0]


class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.AddNewWebTab(QUrl('https://naver.com'))

    def ClickedWebSearchBtn(self):
        self.AddNewWebTab(QUrl(self.lineEdit_url.text()), 'Loading...')

    def RenewURLBar(self, qurl, browser):
        # self.lineEdit_url.setText(qurl.toDisplayString())
        pass

    def AddNewWebTab(self, qurl, label='labels'):
        html = open(r"test_html.html", 'r', encoding='UTF8').read()
        browser = QWebEngineView()
        self.webSettings = browser.settings()
        self.webSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        browser.setHtml(html)
        # browser.setUrl(qurl)

        i = self.tabWidget.addTab(browser, label)

        self.tabWidget.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.RenewURLBar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabWidget.setTabText(i, browser.page().title()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
