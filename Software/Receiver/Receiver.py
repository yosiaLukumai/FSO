from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
import serial
import serial.tools
import serial.tools.list_ports
import os



class Ui_FSO_SENDER(object):
    def setupUi(self, FSO_SENDER):
        if not FSO_SENDER.objectName():
            FSO_SENDER.setObjectName(u"FSO_SENDER")
        FSO_SENDER.resize(620, 480)
        FSO_SENDER.setMinimumSize(QSize(620, 480))
        FSO_SENDER.setMaximumSize(QSize(620, 480))
        font = QFont()
        font.setFamily(u"Segoe Script")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        FSO_SENDER.setFont(font)
        FSO_SENDER.setAutoFillBackground(False)
        FSO_SENDER.setStyleSheet(u"\n"
"QPushButton {\n"
"     background-color: #6262a2;\n"
"    color: white;\n"
"    border: none;\n"
"    padding: 1px 20px;\n"
"    font-size: 19px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:  #6c757d ;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #1c6399;\n"
"}\n"
"\n"
"QLabel {\n"
"    color: #333333;\n"
"    font-size: 19px;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    border: 1px solid #dcdcdc;\n"
"    padding: 5px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border: 1px solid #3498db;\n"
"}\n"
"\n"
"Line{\n"
"\n"
"}\n"
"\n"
"QMainWindow {\n"
"background-color:rgb(77, 77, 127);\n"
"}\n"
"\n"
"")
        self.centralwidget = QWidget(FSO_SENDER)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 338, 41))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.ComportSelector = QComboBox(self.horizontalLayoutWidget)
        self.ComportSelector.setObjectName(u"ComportSelector")
        self.ComportSelector.setMinimumSize(QSize(220, 30))
        self.ComportSelector.setMaximumSize(QSize(16777215, 30))
        self.ComportSelector.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout.addWidget(self.ComportSelector)

        self.ConnectButton = QPushButton(self.horizontalLayoutWidget)
        self.ConnectButton.setObjectName(u"ConnectButton")
        self.ConnectButton.setMinimumSize(QSize(0, 30))
        self.ConnectButton.setMaximumSize(QSize(16777215, 30))
        font1 = QFont()
        font1.setFamily(u"Consolas")
        font1.setBold(True)
        font1.setItalic(True)
        font1.setWeight(75)
        self.ConnectButton.setFont(font1)
        self.ConnectButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.ConnectButton.setStyleSheet(u";")

        self.horizontalLayout.addWidget(self.ConnectButton)

        self.verticalLayoutWidget_3 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(90, 60, 166, 36))
        self.TtileBox = QVBoxLayout(self.verticalLayoutWidget_3)
        self.TtileBox.setObjectName(u"TtileBox")
        self.TtileBox.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget_3)
        self.label.setObjectName(u"label")
        font2 = QFont()
        font2.setFamily(u"Segoe Script")
        font2.setBold(True)
        font2.setWeight(75)
        self.label.setFont(font2)
        self.label.setLayoutDirection(Qt.LeftToRight)
        self.label.setStyleSheet(u"color: #fdc500; \n"
"background-color: none;\n"
"\n"
"")
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.TtileBox.addWidget(self.label)

        self.Upload_Button = QPushButton(self.centralwidget)
        self.Upload_Button.setObjectName(u"Upload_Button")
        self.Upload_Button.setGeometry(QRect(20, 420, 311, 30))
        self.Upload_Button.setMinimumSize(QSize(0, 30))
        self.Upload_Button.setMaximumSize(QSize(16777215, 30))
        self.Upload_Button.setFont(font2)
        self.Upload_Button.setCursor(QCursor(Qt.PointingHandCursor))
        self.Upload_Button.setStyleSheet(u"")
        self.verticalLayoutWidget_4 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_4.setObjectName(u"verticalLayoutWidget_4")
        self.verticalLayoutWidget_4.setGeometry(QRect(370, 60, 231, 36))
        self.TtileBox_2 = QVBoxLayout(self.verticalLayoutWidget_4)
        self.TtileBox_2.setObjectName(u"TtileBox_2")
        self.TtileBox_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.verticalLayoutWidget_4)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font2)
        self.label_2.setLayoutDirection(Qt.LeftToRight)
        self.label_2.setStyleSheet(u"color: #fdc500; \n"
"background-color: none;\n"
"\n"
"")
        self.label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.TtileBox_2.addWidget(self.label_2)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 90, 621, 0))
        self.line.setMinimumSize(QSize(0, 0))
        self.line.setMaximumSize(QSize(16777215, 0))
        self.line.setStyleSheet(u"color: green;\n"
"")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(330, 110, 20, 401))
        self.line_2.setStyleSheet(u"")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_3 = QFrame(self.centralwidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setGeometry(QRect(10, 100, 611, 21))
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.verticalLayoutWidget_5 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_5.setObjectName(u"verticalLayoutWidget_5")
        self.verticalLayoutWidget_5.setGeometry(QRect(410, 10, 160, 41))
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.Status = QLabel(self.verticalLayoutWidget_5)
        self.Status.setObjectName(u"Status")
        self.Status.setFont(font2)
        self.Status.setStyleSheet(u"color:  #cae9ff; \n"
"background-color: none;")

        self.verticalLayout_3.addWidget(self.Status)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(370, 20, 21, 21))
        self.label_3.setCursor(QCursor(Qt.PointingHandCursor))
        self.label_3.setPixmap(QPixmap(u"Refresh.png"))
        self.label_3.setScaledContents(True)
        self.circularProgressBar_Main = QFrame(self.centralwidget)
        self.circularProgressBar_Main.setObjectName(u"circularProgressBar_Main")
        self.circularProgressBar_Main.setGeometry(QRect(350, 130, 240, 240))
        self.circularProgressBar_Main.setStyleSheet(u"background-color: none;")
        self.circularProgressBar_Main.setFrameShape(QFrame.NoFrame)
        self.circularProgressBar_Main.setFrameShadow(QFrame.Raised)
        self.circularProgressCPU = QFrame(self.circularProgressBar_Main)
        self.circularProgressCPU.setObjectName(u"circularProgressCPU")
        self.circularProgressCPU.setGeometry(QRect(10, 10, 220, 220))
        self.circularProgressCPU.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.400 rgba(85, 170, 255, 255), stop:0.395 rgba(255, 255, 255, 0));\n"
"}")
        self.circularProgressCPU.setFrameShape(QFrame.StyledPanel)
        self.circularProgressCPU.setFrameShadow(QFrame.Raised)
        self.circularBg = QFrame(self.circularProgressBar_Main)
        self.circularBg.setObjectName(u"circularBg")
        self.circularBg.setGeometry(QRect(10, 10, 220, 220))
        self.circularBg.setStyleSheet(u"QFrame{\n"
"	border-radius: 110px;	\n"
"	background-color: rgba(85, 85, 127, 100);\n"
"}")
        self.circularBg.setFrameShape(QFrame.StyledPanel)
        self.circularBg.setFrameShadow(QFrame.Raised)
        self.circularContainer = QFrame(self.circularProgressBar_Main)
        self.circularContainer.setObjectName(u"circularContainer")
        self.circularContainer.setGeometry(QRect(25, 25, 190, 190))
        self.circularContainer.setBaseSize(QSize(0, 0))
        self.circularContainer.setStyleSheet(u"QFrame{\n"
"	border-radius: 95px;	\n"
"	background-color: rgb(58, 58, 102);\n"
"}")
        self.circularContainer.setFrameShape(QFrame.StyledPanel)
        self.circularContainer.setFrameShadow(QFrame.Raised)
        self.layoutWidget = QWidget(self.circularContainer)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 40, 171, 145))
        self.infoLayout = QGridLayout(self.layoutWidget)
        self.infoLayout.setObjectName(u"infoLayout")
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.labelAplicationName = QLabel(self.layoutWidget)
        self.labelAplicationName.setObjectName(u"labelAplicationName")
        font3 = QFont()
        font3.setFamily(u"Segoe UI")
        self.labelAplicationName.setFont(font3)
        self.labelAplicationName.setStyleSheet(u"color: #FFFFFF; background-color: none;")
        self.labelAplicationName.setAlignment(Qt.AlignCenter)

        self.infoLayout.addWidget(self.labelAplicationName, 0, 0, 1, 1)

        self.labelPercentageCPU = QLabel(self.layoutWidget)
        self.labelPercentageCPU.setObjectName(u"labelPercentageCPU")
        font4 = QFont()
        font4.setFamily(u"Roboto Thin")
        self.labelPercentageCPU.setFont(font4)
        self.labelPercentageCPU.setStyleSheet(u"color: rgb(115, 185, 255); padding: 0px; background-color: none;")
        self.labelPercentageCPU.setAlignment(Qt.AlignCenter)
        self.labelPercentageCPU.setIndent(-1)

        self.infoLayout.addWidget(self.labelPercentageCPU, 1, 0, 1, 1)

        self.labelCredits = QLabel(self.layoutWidget)
        self.labelCredits.setObjectName(u"labelCredits")
        self.labelCredits.setFont(font3)
        self.labelCredits.setStyleSheet(u"color: rgb(148, 148, 216); background-color: none;")
        self.labelCredits.setAlignment(Qt.AlignCenter)

        self.infoLayout.addWidget(self.labelCredits, 2, 0, 1, 1)

        self.circularBg.raise_()
        self.circularProgressCPU.raise_()
        self.circularContainer.raise_()
        self.FileInfo = QLabel(self.centralwidget)
        self.FileInfo.setObjectName(u"FileInfo")
        self.FileInfo.setGeometry(QRect(20, 360, 131, 31))
        font5 = QFont()
        font5.setFamily(u"SWItalt")
        font5.setBold(False)
        font5.setWeight(50)
        self.FileInfo.setFont(font5)
        self.FileInfo.setStyleSheet(u"color: #fb8500;\n""font-size:8 !important\n"";")
        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(20, 120, 311, 291))
        self.textEdit.setStyleSheet(u"border-radius:12;")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(380, 380, 221, 33))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font2)
        self.label_4.setStyleSheet(u"color: #fdc500; ")
        self.label_4.setTextFormat(Qt.MarkdownText)

        self.verticalLayout.addWidget(self.label_4)

        self.verticalLayoutWidget_2 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(380, 420, 221, 33))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.verticalLayoutWidget_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font2)
        self.label_5.setStyleSheet(u"color: #fdc500; ")

        self.verticalLayout_2.addWidget(self.label_5)

        FSO_SENDER.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(FSO_SENDER)
        self.statusbar.setObjectName(u"statusbar")
        FSO_SENDER.setStatusBar(self.statusbar)

        self.retranslateUi(FSO_SENDER)

        QMetaObject.connectSlotsByName(FSO_SENDER)
    # setupUi

    def retranslateUi(self, FSO_SENDER):
        FSO_SENDER.setWindowTitle(QCoreApplication.translate("FSO_SENDER", u"FSO_SENDER", None))
        self.ConnectButton.setText(QCoreApplication.translate("FSO_SENDER", u"Connect", None))
#if QT_CONFIG(accessibility)
        self.label.setAccessibleDescription(QCoreApplication.translate("FSO_SENDER", u"0", None))
#endif // QT_CONFIG(accessibility)
        self.label.setText(QCoreApplication.translate("FSO_SENDER", u"Preview Section", None))
        self.Upload_Button.setText(QCoreApplication.translate("FSO_SENDER", u"Save File", None))
#if QT_CONFIG(accessibility)
        self.label_2.setAccessibleDescription(QCoreApplication.translate("FSO_SENDER", u"0", None))
#endif // QT_CONFIG(accessibility)
        self.label_2.setText(QCoreApplication.translate("FSO_SENDER", u"Monitoring Section", None))
        self.Status.setText(QCoreApplication.translate("FSO_SENDER", u"Not conected", None))
        self.label_3.setText("")
        self.labelAplicationName.setText(QCoreApplication.translate("FSO_SENDER", u"<html><head/><body><p>% completion</p></body></html>", None))
        self.labelPercentageCPU.setText(QCoreApplication.translate("FSO_SENDER", u"<p align=\"center\"><span style=\" font-size:50pt;\">60</span><span style=\" font-size:40pt; vertical-align:super;\">%</span></p>", None))
        self.labelCredits.setText(QCoreApplication.translate("FSO_SENDER", u"<html><head/><body><p><span style=\" font-size:11pt;\">Speed:</span><span style=\" font-size:11pt; color:#ffffff;\"> 2Kb/s</span></p></body></html>", None))
        self.FileInfo.setText("")
        self.label_4.setText(QCoreApplication.translate("FSO_SENDER", u"File Type: ", None))
        self.label_5.setText(QCoreApplication.translate("FSO_SENDER", u"File Size: ", None))
    # retranslateUi



if __name__ == "__main__":
    import atexit
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_FSO_SENDER()
    ui.setupUi(mainWindow)
    # atexit.register(ui.CleanResources)
    mainWindow.show()
    sys.exit(app.exec_())