# -*- coding: utf-8 -*-
"""
Created on Mon May 04 17:30:36 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin
from hyperspy.hspy import *

from python_qt_binding import QtGui, QtCore, QtWebKit, QtNetwork
from QtCore import *
from QtGui import *
from QtWebKit import *
from QtNetwork import *

try:
    assert(QSslSocket.supportsSsl())
except NameError, AssertionError:
    raise ImportError("Current platform doesn't support SSL. EELSDB plugin"
                      " disabled.")

from hyperspyui.widgets.extendedqwidgets import ExToolWindow
import os
import re
import urllib2
import tempfile

re_dl_url = re.compile(
    r'http://eelsdb\.eu/wp-content/uploads/\d{4}/\d{2}/.+\.msa')


class EELSDBPlugin(Plugin):
    name = "EELSDB Plugin"

    def __init__(self, main_window):
        super(EELSDBPlugin, self).__init__(main_window)
        self.window = None
        self.view = None

    def create_actions(self):
        self.add_action(self.name + '.default', "Browse", self.default,
                        tip="")

    def create_menu(self):
        self.add_menuitem('EELSDB', self.ui.actions[self.name + '.default'])

    def _make_request(self, url):
        request = QNetworkRequest()
        request.setUrl(QUrl(url))
        return request

    def _urlencode_post_data(self, post_data):
        post_params = QUrl()
        for (key, value) in post_data.items():
            post_params.addQueryItem(key, unicode(value))

        return post_params.encodedQuery()

    def _clear_window(self):
        item = self.window.layout().takeAt(0)
        while item:
            w = item.widget()
            if w:
                w.close()
            item = self.window.layout().takeAt(0)

    def load_blocking(self, view, *args):
        loop = QEventLoop()
        view.loadFinished.connect(loop.quit)

        def unravel():
            view.loadFinished.disconnect(loop.quit)
            view.loadFinished.disconnect(unravel)

        view.loadFinished.connect(unravel)
        view.load(*args)
        loop.exec_()

    def login(self, req):
        view = QWebView(self.ui)
        self.view = view
        # Grab cookie
        loginurl = QUrl("https://eelsdb.eu/wp-login.php")
        self.load_blocking(view, loginurl)

        self.settings['uname'] = self.edt_uname.text()
        if self.chk_remember.isChecked():
            self.settings['pwd'] = self.edt_pwd.text()
        else:
            self.settings['pwd'] = None

        # Log in
        post_data = {'log': self.edt_uname.text(),
                     'pwd': self.edt_pwd.text(),
                     'wp-submit': 'Log In',
                     'redirect_to': 'https://eelsdb.eu/spectra',
                     'testcookie': 1
                     }
        request = self._make_request(loginurl)
        encoded_data = self._urlencode_post_data(post_data)
        request.setRawHeader('Content-Type',
                             QByteArray('application/x-www-form-urlencoded'))
        self.load_blocking(view, request, QNetworkAccessManager.PostOperation,
                           encoded_data)
        # Remove header/footer
        frame = view.page().mainFrame()
        frame.findFirstElement(".footer").removeFromDocument()
        for el in frame.findAllElements(".navbar"):
            el.removeFromDocument()
        view.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        view.linkClicked.connect(self._on_link)

        self._clear_window()
        vbox = self.window.layout()
        vbox.addWidget(view)
        self.window.resize(view.sizeHint())

    def _on_link(self, url):
        su = url.toString(QUrl.RemoveQuery)
        if "/spectra/" in su:
            view = QWebView(self.ui)
            wp = QWebPage()
            am = self.view.page().networkAccessManager()
            wp.setNetworkAccessManager(am)
            view.setPage(wp)
            request = self._make_request(url)
            response = am.get(request)

            def resp_finished():
                html = response.readAll()
                matches = re_dl_url.findall(html)
                self.download(str(matches[0]))
                response.deleteLater()
            response.finished.connect(resp_finished)
        else:
            self.view.load(url)

    def download(self, url):
        header = {'Accept': r'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,*/*;q=0.8',
                  'Accept-Encoding': r'gzip, deflate',
                  'User-Agent': r''}

        suffix = '.msa'

        req = urllib2.Request(url, headers=header)
        page = urllib2.urlopen(req)

        try:
            f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            fn = f.name
            f.write(page.read())
            fn = f.name
            f.close()
            self.ui.load([fn])
        finally:
            f.close()
            os.remove(fn)

    def default(self):
        if self.window is None:
            self.window = ExToolWindow(self.ui)
            self.window.setWindowTitle("EELSDB")
            form = QFormLayout()
            uname = self.settings['uname'] if 'uname' in self.settings else ""
            pwd = self.settings['pwd'] if 'pwd' in self.settings else ""

            self.edt_uname = QLineEdit(uname)
            form.addRow("Username:", self.edt_uname)
            self.edt_pwd = QLineEdit(pwd)
            self.edt_pwd.setEchoMode(QLineEdit.Password)
            form.addRow("Password:", self.edt_pwd)
            self.chk_remember = QCheckBox("Remember password")
            self.chk_remember.setChecked(bool(pwd))
            form.addRow(None, self.chk_remember)
            vbox = QVBoxLayout()
            vbox.addLayout(form)
            login_btn = QPushButton("Login")
            login_btn.clicked.connect(self.login)
            vbox.addWidget(login_btn)
            self.window.setLayout(vbox)
        self.window.show()
