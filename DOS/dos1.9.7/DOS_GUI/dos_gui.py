# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dos_gui.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from dos import *

def dos_warpper(func):
    @wraps(func)
    def wrapper(self,*args,**kargs):
        atom=eval(self.atom_input.text())
        xlim=eval(self.xlim_input.text())
        color=self.color_input.text() if (self.color_input.text()) else "#000000"
        method=self.method_input.text() if (self.method_input.text()) else "fill"
        P=PlotDOS("DOSCAR","CONTCAR")
        P.plot(atom=atom,xlim=xlim,color=color,method=method)
        func(self)
    return wrapper

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(871, 540)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(200, 150, 74, 169))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.layoutWidget1 = QtWidgets.QWidget(Form)
        self.layoutWidget1.setGeometry(QtCore.QRect(380, 150, 127, 171))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.atom_input = QtWidgets.QLineEdit(self.layoutWidget1)
        self.atom_input.setObjectName("atom_input")
        self.verticalLayout_2.addWidget(self.atom_input)
        self.xlim_input = QtWidgets.QLineEdit(self.layoutWidget1)
        self.xlim_input.setObjectName("xlim_input")
        self.verticalLayout_2.addWidget(self.xlim_input)
        self.color_input = QtWidgets.QLineEdit(self.layoutWidget1)
        self.color_input.setObjectName("color_input")
        self.verticalLayout_2.addWidget(self.color_input)
        self.method_input = QtWidgets.QLineEdit(self.layoutWidget1)
        self.method_input.setObjectName("method_input")
        self.verticalLayout_2.addWidget(self.method_input)
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setGeometry(QtCore.QRect(680, 190, 85, 76))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.show_button = QtWidgets.QPushButton(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.show_button.setFont(font)
        self.show_button.setObjectName("show_button")
        self.save_button = QtWidgets.QPushButton(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")

        self.retranslateUi(Form)
        self.show_button.clicked.connect(self.dos_show)
        self.save_button.clicked.connect(self.dos_save)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "DOS"))
        self.label.setText(_translate("Form", "atom"))
        self.label_3.setText(_translate("Form", "xlim"))
        self.label_4.setText(_translate("Form", "color"))
        self.label_5.setText(_translate("Form", "method"))
        self.show_button.setText(_translate("Form", "show"))
        self.save_button.setText(_translate("Form", "save"))

    @dos_warpper
    def dos_show(self):
        plt.show()

    @dos_warpper
    def dos_save(self):
        plt.savefig("figure.svg",dpi=300,bbox_inches='tight',format='svg')

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
