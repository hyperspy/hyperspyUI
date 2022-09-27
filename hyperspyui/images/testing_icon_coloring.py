#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Based off of:

ZetCode PyQt4 tutorial

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar and a central widget.

author: Jan Bodnar
website: zetcode.com
last edited: September 2011
"""

import sys
from qtpy import QtGui, QtWidgets

import tempfile
import glob
import os


class Example(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def replaceSvgColor(self, filename, oldColor, newColor):
        '''
        Generate and return a temp svg filename with oldColor replaced
        by newColor (color names are in HTML format '#XXXXXX')
        '''
        with open(filename, 'r') as svg_file:
            svg_cnt = svg_file.read()
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(svg_cnt.replace(oldColor, newColor).encode('utf-8'))
        temp.close()

        return temp.name

    def initUI(self):
        stack = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()

        color_list = []
        color_list.append(('QtGui.QPalette.Window',
                           self.palette().color(QtGui.QPalette.Window)))
        color_list.append(('QtGui.QPalette.Background',
                           self.palette().color(QtGui.QPalette.Background)))
        color_list.append(('QtGui.QPalette.WindowText',
                           self.palette().color(QtGui.QPalette.WindowText)))
        color_list.append(('QtGui.QPalette.Foreground',
                           self.palette().color(QtGui.QPalette.Foreground)))
        color_list.append(('QtGui.QPalette.Base',
                           self.palette().color(QtGui.QPalette.Base)))
        color_list.append(('QtGui.QPalette.AlternateBase',
                           self.palette().color(QtGui.QPalette.AlternateBase)))
        color_list.append(('QtGui.QPalette.ToolTipBase',
                           self.palette().color(QtGui.QPalette.ToolTipBase)))
        color_list.append(('QtGui.QPalette.ToolTipText',
                           self.palette().color(QtGui.QPalette.ToolTipText)))
        color_list.append(('QtGui.QPalette.Text',
                           self.palette().color(QtGui.QPalette.Text)))
        color_list.append(('QtGui.QPalette.Button',
                           self.palette().color(QtGui.QPalette.Button)))
        color_list.append(('QtGui.QPalette.ButtonText',
                           self.palette().color(QtGui.QPalette.ButtonText)))
        color_list.append(('QtGui.QPalette.BrightText',
                           self.palette().color(QtGui.QPalette.BrightText)))

        textEdit = QtWidgets.QTextEdit()
        for n, c in color_list:
            textEdit.append(n + ':\t' + str(c.name()))
        stack.addWidget(textEdit)

        # Change this to wherever your icons are stored
        icon_files = glob.glob("*.svg")

        widget.setLayout(stack)
        self.setCentralWidget(widget)

        toolbar1 = self.addToolBar('Bar1')
        toolbar2 = self.addToolBar('Bar2')
        toolbar3 = self.addToolBar('Bar3')

        ico_list = [''] * len(icon_files)
        action_list = [''] * len(icon_files)
        for i, f in enumerate(icon_files):
            ico_list[i] = QtGui.QIcon(self.replaceSvgColor(f,
                                                           '#000000',
                                                           'red'))
            action_list[i] = QtWidgets.QAction(ico_list[i], 'Exit', self)
            action_list[i].setStatusTip(os.path.basename(f))

            # add to toolbars
            if i/float(len(icon_files)) <= 0.33:
                toolbar1.addAction(action_list[i])
            elif i/float(len(icon_files)) <= 0.66:
                toolbar2.addAction(action_list[i])
            else:
                toolbar3.addAction(action_list[i])

        # shortcut to close ('X' icon in position 8)
        action_list[8].setShortcut('Ctrl+Q')
        action_list[8].triggered.connect(self.close)

        self.insertToolBarBreak(toolbar2)
        self.insertToolBarBreak(toolbar3)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(action_list[8])

        self.setGeometry(50, 30, 650, 350)
        self.setWindowTitle('Icon color testing')
        self.show()

        self.statusBar().showMessage("Ready")


def main():
    app = QtWidgets.QApplication(sys.argv)
    _ = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
