#!/usr/bin/python
# -*- coding:utf-8 -*-

import itertools as itrt
import codecs
from PySide import QtCore, QtGui, QtWebKit
import pyter

class OpenDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(OpenDialog, self).__init__(parent)
        self.layout = QtGui.QVBoxLayout()
        ##
        lay1 = QtGui.QHBoxLayout()
        self.text1 = QtGui.QLineEdit()
        btn1 = QtGui.QPushButton("...")
        lay1.addWidget(self.text1)
        lay1.addWidget(btn1)
        self.layout.addLayout(lay1)
        btn1.clicked.connect(lambda : self.get_file(self.text1))
        ## 
        lay2 = QtGui.QHBoxLayout()
        self.text2 = QtGui.QLineEdit()
        btn2 = QtGui.QPushButton("...")
        lay2.addWidget(self.text2)
        lay2.addWidget(btn2)
        self.layout.addLayout(lay2)
        btn2.clicked.connect(lambda : self.get_file(self.text2))        
        ## button
        lay3 = QtGui.QHBoxLayout()
        ok_btn = QtGui.QPushButton('OK')
        cancel_btn = QtGui.QPushButton('Cancel')
        lay3.addWidget(ok_btn)
        lay3.addWidget(cancel_btn)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        self.layout.addLayout(lay3)
        ## 
        self.setLayout(self.layout)
        

    def get_file(self, edit):
        fileName, filtr = QtGui.QFileDialog.getOpenFileName(self)
        if fileName:
            edit.setText(fileName)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        ## size
        self.setMinimumSize(800, 600)
        self.viewer = QtWebKit.QWebView()
        #self.viewer = QtGui.QTextEdit()
        #self.viewer.setReadOnly(True)
        self.setCentralWidget(self.viewer)
        ## 
        self.createActions()
        self.createMenus()
        ##
        self.setUnifiedTitleAndToolBarOnMac(True)

    def open(self):
        d = OpenDialog()
        if d.exec_():
            self.set_view(d.text1.text(), d.text2.text())
        ## self.set_view('../../inbox/temp1.txt', '../../inbox/temp2.txt')

    def set_view(self, ref_path, hyp_path):
        htmltemplate = '''<html>
        <head><style type="text/css">%s</style></head>
        <body>%s</body>
        </html>'''
        body = ''
        stylesheet = ''
        for sid, ref, hyp in itrt.izip(itrt.count(), codecs.open(ref_path, 'r', 'utf-8'),
                                   codecs.open(hyp_path, 'r', 'utf-8')):
            if ref.strip() and hyp.strip():
                html, style = self.get_html(ref, hyp, sid)
                body += html
                stylesheet += style
        htmltext = htmltemplate % (stylesheet, body)
        self.viewer.setHtml(htmltext)
        # doc = QtGui.QTextDocument()
        # doc.addResource(QtGui.QTextDocument.StyleSheetResource, 'format.css', stylesheet)
        # doc.setHtml(htmltext)
        # self.viewer.setDocument(doc)

    def get_html(self, ref, hyp, sid):
        aligns = None
        colors = ('#0000ff', '#00ff00', '#00ffff', '#ff0000', '#ff00ff', '#ffffff')
        style = """
        * {font-size: 20px;}
        div {
          margin-bottom: 5px;
        }
        span {
          border-raduis: 5px;
        }
        p { margin: 0; }
        """
        styletemplate = "#s%d span.%s {background-color: %s;} "
        if ' ' not in ref and ' ' not in hyp:
            ## align = pyter.align(ref, hyp, wordmatch=False)
            align = pyter.diff_align(ref, hyp, wordmatch=False)
        else:
            ## align = pyter.align(ref, hyp)
            align = pyter.diff_align(ref, hyp)
        if not align:
            return '<div id="s%d"><p>%s</p><p>%s</p></div>' % (sid, ref, hyp)
        reftext = ref[:align[0][0]]
        hyptext = hyp[:align[0][1]]
        for ind, l, r in itrt.izip(itrt.count(), align[:-1], align[1:]):
            cls = 'c%d' % ind
            reftext += '<span class="%s">%s</span>' % (cls, ref[l[0]:l[0] + l[2]])
            reftext += ref[l[0] + l[2]:r[0]]
            ##
            hyptext += '<span class="%s">%s</span>' % (cls, hyp[l[1]:l[1] + l[2]])
            hyptext += hyp[l[1] + l[2]:r[1]]
            ## 
            style += styletemplate % (sid, cls, colors[ind % len(colors)])
        return '<div id="s%d"><p>%s</p><p>%s</p></div>' % (sid, reftext, hyptext), style


    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)

    def loadFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Application",
                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))
            return

        inf = QtCore.QTextStream(file)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.textEdit.setPlainText(inf.readAll())
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("File loaded", 2000)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
