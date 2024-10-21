from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
import serial
import serial.tools
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal
import time
import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtSerialPort import QSerialPort


class DataReceiverWorker(QObject):
    error_occurred = pyqtSignal(str)
    data_received = pyqtSignal(str) 
    finished = pyqtSignal() 
    progress = pyqtSignal(int)
    fileTypeSignal = pyqtSignal(str)
    fileSizeSignal = pyqtSignal(str)
    errorSignal = pyqtSignal(int)

    def __init__(self, port_name):
        super().__init__()
        self.serial_port = QSerialPort()
        self.serial_port.setPortName(port_name)
        self.serial_port.setFlowControl(QSerialPort.SoftwareControl)  # Using software control (XON/XOFF)
        self.serial_port.setParity(QSerialPort.NoParity)
        self.serial_port.setReadBufferSize(1024)  # Buffer size for reading data
        self.serial_port.setDataBits(QSerialPort.Data8)
        self.serial_port.setStopBits(QSerialPort.OneStop)
        self.serial_port.setBaudRate(115200)

        self.is_running = True

        self.expected_file_size = 0 
        self.expected_file_type = "" 
        self.received_data = b"" 
        self.header_buffer = ""
        self.in_header = False  
        self.timeout_duration = 5
        self.errorSize = 0
        self.last_received_time = time.time()


    def format_size(self, bytes_size):
        """
        Convert the size from bytes to KB, MB, or GB, depending on its magnitude.
        :param bytes_size: Size in bytes
        :return: Formatted string with the size in KB, MB, or GB
        """
        # Convert bytes to kilobytes
        kb_size = bytes_size / 1024

        if kb_size < 1000:
            # If size is less than 1000 KB, return in KB
            return f"{kb_size:.2f} KB"
        
        # Convert kilobytes to megabytes
        mb_size = kb_size / 1024

        if mb_size < 1000:
            # If size is less than 1000 MB, return in MB
            return f"{mb_size:.2f} MB"
        
        # Convert megabytes to gigabytes
        gb_size = mb_size / 1024

        # Return the size in GB
        return f"{gb_size:.2f} GB"


    def start_receiving(self):
        """Start the data reception process."""
        # Try to open the serial port in read-only mode
        if not self.serial_port.open(QSerialPort.ReadOnly):
            self.error_occurred.emit(f"Failed to open port: {self.serial_port.errorString()}")
            return

        # Loop to continuously listen for incoming data
        while self.is_running:
            if self.serial_port.waitForReadyRead(100):  # Wait for data to be ready (timeout = 100 ms)
                data = self.serial_port.readAll()  # Read all available data
                try:
                    decoded_data = data.data().decode('utf-8', errors='replace')
                    self.data_received.emit(decoded_data)

                except Exception as e:
                    pass
                

            #     if data:  # If data is received, process it
            #         self.last_received_time = time.time()
            #         # If we're still in the header stage
            #         if self.in_header:
            #             # Accumulate the header data
            #             header_data = data.data().decode('utf-8', errors='replace')
            #             self.header_buffer += header_data
            #             # print(f"Received header chunk: {header_data}")

            #             # Check if the header has ended
            #             if "END_HEADER" in self.header_buffer:
            #                 # Parse the complete header until the end marker
            #                 header_end_idx = self.header_buffer.index("END_HEADER") + len("END_HEADER")
            #                 complete_header = self.header_buffer[:header_end_idx]

            #                 # Parse the header fields
            #                 header_fields = complete_header.split('|')
            #                 for field in header_fields:
            #                     if "FILE_SIZE" in field:
            #                         self.expected_file_size = int(field.split(':')[1])
            #                         print(f"Expected File Size: {self.expected_file_size} bytes")
            #                         self.fileSizeSignal.emit(self.format_size(self.expected_file_size))
            #                     if "FILE_TYPE" in field:
            #                         self.expected_file_type = field.split(':')[1]
            #                         self.fileTypeSignal.emit(self.expected_file_type)
            #                         # print(self.expected_file_type)

            #                 # Set `self.in_header` to False to move to data receiving stage
            #                 self.in_header = False

            #                 # Append any remaining data after the header into the main data buffer
            #                 remaining_data = self.header_buffer[header_end_idx:].encode('utf-8')
            #                 self.received_data += remaining_data
            #                 print(f"Remaining data added: {len(remaining_data)} bytes")
            #                 self.header_buffer = ""
            #                 self.progress.emit(0)
            #             continue  

            #         # If header has been processed, receive the file data
            #         self.received_data += data  # Append the received data to the buffer
            #         decoded_data = data.data().decode('utf-8', errors='replace')
            #         self.data_received.emit(decoded_data)
            #         print(f"Data received so far: {len(self.received_data)} bytes")
            #         progress_percent = int(len(self.received_data) / self.expected_file_size * 100)
            #         self.progress.emit(progress_percent)

            #         # Check if the received data has reached the expected file size
            #         if len(self.received_data) >= self.expected_file_size:
            #             print("Complete file received.")
            #             # Emit the complete data as a string after decoding
            #             try:
            #                 decoded_data = self.received_data.decode('utf-8', errors='replace')
            #                 self.data_received.emit(decoded_data)
            #             except UnicodeDecodeError as e:
            #                 # Handle any decoding errors and emit the error message
            #                 self.error_occurred.emit(f"Decoding error: {e}")
            #             break  # Exit the loop once the complete file is received

            # if (time.time() - self.last_received_time > self.timeout_duration) and not self.in_header:
            #     if len(self.received_data) < self.expected_file_size:
            #         self.errorSize = self.expected_file_size - len(self.received_data)
            #         self.error_occurred.emit("Error: Data transfer incomplete. Possible data loss.")

            #     else:
            #         print("Data transfer completed without errors.")
                
            #     print("emmitiing there was some error")
            #     self.errorSignal.emit(self.errorSize)

        # Close the serial port and signal that the thread has finished
        self.serial_port.close()
        self.finished.emit()

    def stop_receiving(self):
        """Stop the data reception and close the serial port."""
        self.is_running = False
        self.in_header = True
        if self.serial_port.isOpen():
            self.serial_port.close()
        print("Serial port closed successfully.")



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
        FSO_SENDER.setStyleSheet(u"\n""QPushButton {\n""     background-color: #6262a2;\n""    color: white;\n""    border: none;\n""    padding: 1px 20px;\n""    font-size: 19px;\n""    border-radius: 5px;\n""}\n""\n""QPushButton:hover {\n""    background-color:  #6c757d ;\n""}\n""\n""QPushButton:pressed {\n""    background-color: #1c6399;\n""}\n""\n""QLabel {\n""    color: #333333;\n""    font-size: 19px;\n""}\n""\n""QLineEdit {\n""    border: 1px solid #dcdcdc;\n""    padding: 5px;\n""    border-radius: 5px;\n""}\n""\n""QLineEdit:focus {\n""    border: 1px solid #3498db;\n""}\n""\n""Line{\n""\n""}\n""\n""QMainWindow {\n""background-color:rgb(77, 77, 127);\n""}\n""\n""")
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
        self.label.setStyleSheet(u"color: #fdc500; \n""background-color: none;\n""\n""")
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
        self.label_2.setStyleSheet(u"color: #fdc500; \n""background-color: none;\n""\n""")
        self.label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.TtileBox_2.addWidget(self.label_2)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 90, 621, 0))
        self.line.setMinimumSize(QSize(0, 0))
        self.line.setMaximumSize(QSize(16777215, 0))
        self.line.setStyleSheet(u"color: green;\n""")
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
        self.Status.setStyleSheet(u"color:  #cae9ff; \n""background-color: none;")

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
        self.circularProgressCPU.setStyleSheet(u"QFrame{\n""	border-radius: 110px;	\n""	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.400 rgba(85, 170, 255, 255), stop:0.395 rgba(255, 255, 255, 0));\n""}")
        self.circularProgressCPU.setFrameShape(QFrame.StyledPanel)
        self.circularProgressCPU.setFrameShadow(QFrame.Raised)
        self.circularBg = QFrame(self.circularProgressBar_Main)
        self.circularBg.setObjectName(u"circularBg")
        self.circularBg.setGeometry(QRect(10, 10, 220, 220))
        self.circularBg.setStyleSheet(u"QFrame{\n""	border-radius: 110px;	\n""	background-color: rgba(85, 85, 127, 100);\n""}")
        self.circularBg.setFrameShape(QFrame.StyledPanel)
        self.circularBg.setFrameShadow(QFrame.Raised)
        self.circularContainer = QFrame(self.circularProgressBar_Main)
        self.circularContainer.setObjectName(u"circularContainer")
        self.circularContainer.setGeometry(QRect(25, 25, 190, 190))
        self.circularContainer.setBaseSize(QSize(0, 0))
        self.circularContainer.setStyleSheet(u"QFrame{\n""	border-radius: 95px;	\n""	background-color: rgb(58, 58, 102);\n""}")
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
        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(360, 10, 41, 41))
        self.pushButton_3.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_3.setStyleSheet(u"background-color:none;")
        icon = QIcon()
        icon.addFile(u"C:/Users/Yosia/Desktop/_/FSO/FSO_SENDER/Software/Receiver/Refresh.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_3.setIcon(icon)
        self.pushButton_3.setIconSize(QSize(22, 22))
        FSO_SENDER.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(FSO_SENDER)
        self.statusbar.setObjectName(u"statusbar")
        FSO_SENDER.setStatusBar(self.statusbar)

        self.retranslateUi(FSO_SENDER)

        QMetaObject.connectSlotsByName(FSO_SENDER)


        self.pushButton_3.clicked.connect(self.ObtainSerialPort)
        self.ConnectButton.clicked.connect(self.ConnectPort)
        self.AvailableComports = []
        self.ComportConfigured = False
        self.workingComportName = ""
        self.ObtainSerialPort()
        self.worker = None
        self.thread = None
        QApplication.instance().aboutToQuit.connect(self.cleanup)
    
    # def cleanup(self):
    #     """Perform cleanup before application exits."""
    #     self.worker.stop_receiving()
    
    # def ConnectPort(self):
    #     if self.ComportSelector.currentText() != "":
    #          if not self.ComportConfigured:
    #             self.Status.setText(self.ComportSelector.currentText())
    #             self.workingComportName = self.ComportSelector.currentText()
    #             self.worker = DataReceiverWorker(self.workingComportName)
    #             self.ComportConfigured = True
    #             # self.thread = QThread()
    #             self.worker.start_receiving()
    #          else:
    #              self.stop_receiving()
    #     else:
    #         self.Status.setText("No comport")
       
    # def ObtainSerialPort(self):
    #     ports = serial.tools.list_ports.comports()
    #     self.ComportSelector.clear()
    #     if len(ports) <= 0:
    #         self.Status.setText("No comport")
    #     else:
    #         self.AvailableComports = ports
    #         self.Status.setText("Select Comport")
    #         for port in ports:
    #             self.ComportSelector.addItem(port.device)

    # def stop_receiving(self):
    #     """Stop the current data receiving process."""
    #     if self.worker:
    #         self.worker.serial_port.close()  # Close the current serial port
    #         self.worker.quit()  # Quit the thread
    #         self.worker.wait()  # Wait for the thread to finish
    #         self.worker = None
    #         self.thread = None

    # def show_error(self, message):
    #     """Show an error message to the user."""
    #     print(message)

    # def display_data(self, data):
    #     """Display received data in the text edit."""
    #     print(data)
    #     self.textEdit.append(data)
    def cleanup(self):
        """Perform cleanup before application exits."""
        self.stop_receiving()

    def progressBarValue(self, value, widget, color):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 110px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # FIX MAX VALUE
        if value == 100:
            stop_1 = "1.000"
            stop_2 = "1.000"

        # SET VALUES TO NEW STYLESHEET

        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2).replace("{COLOR}", color)

        # APPLY STYLESHEET WITH NEW VALUES
        widget.setStyleSheet(newStylesheet)


    def ConnectPort(self):
        if self.ComportSelector.currentText() != "":
            if not self.ComportConfigured:
                self.Status.setText(self.ComportSelector.currentText())
                self.workingComportName = self.ComportSelector.currentText()
                self.worker = DataReceiverWorker(self.workingComportName)
                
                # Create a new thread and move worker to that thread
                self.thread = QThread()
                self.worker.moveToThread(self.thread)
                
                # Connect signals and slots
                self.thread.started.connect(self.worker.start_receiving)
                self.worker.data_received.connect(self.display_data)
                self.worker.fileSizeSignal.connect(self.fileSize)
                self.worker.fileTypeSignal.connect(self.fileType)
                self.worker.errorSignal.connect(self.errorSignalSize)
                self.worker.progress.connect(self.update_progress)
                self.worker.error_occurred.connect(self.show_error)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                
                # Start the thread
                self.thread.start()

                self.ComportConfigured = True
            else:
                self.stop_receiving()
        else:
            self.Status.setText("No comport")

    def ObtainSerialPort(self):
        ports = serial.tools.list_ports.comports()
        self.ComportSelector.clear()
        if len(ports) <= 0:
            self.Status.setText("No comport")
        else:
            self.AvailableComports = ports
            self.Status.setText("Select Comport")
            for port in ports:
                self.ComportSelector.addItem(port.device)

    def stop_receiving(self):
        """Stop the current data receiving process."""
        if self.worker:
            self.worker.stop_receiving()  # Signal the worker to stop
            self.thread.quit()
            self.thread.wait()  # Wait for the thread to finish
            self.worker = None
            self.thread = None
            self.ComportConfigured = False
            self.Status.setText("Disconnected")

    def show_error(self, message):
        """Show an error message to the user."""
        print(message)
    
    def fileType(self, typef:str):
        """Show an error message to the user."""
        self.label_4.setText(f"File Type: {typef.upper()}")

    def errorSignalSize(self, size:int):
        """Show an error message to the user."""
        print(size)
        self.label_4.setText(f"Error: {size} bytes")
    
    def fileSize(self, typef):
        """Show an error message to the user."""
        self.label_5.setText(f"File Size: {typef}")

    def display_data(self, data):
        """Display received data in the text edit."""
        cleaned_data = data.replace('\x00', '')  # Remove null characters
        self.textEdit.append(cleaned_data)

    def update_progress(self, value):
        self.labelPercentageCPU.setText(str(value))
        self.progressBarValue(color="rgba(85, 170, 255, 255)", widget=self.circularProgressCPU, value=value)

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
        self.labelPercentageCPU.setText(QCoreApplication.translate("FSO_SENDER", u"<p align=\"center\"><span style=\" font-size:50pt;\">0</span><span style=\" font-size:40pt; vertical-align:super;\">%</span></p>", None))
        self.labelCredits.setText(QCoreApplication.translate("FSO_SENDER", u"<html><head/><body><p><span style=\" font-size:11pt;\"></span><span style=\" font-size:11pt; color:#ffffff;\"> </span></p></body></html>", None))
        self.FileInfo.setText("")
        self.label_4.setText(QCoreApplication.translate("FSO_SENDER", u"File Type: ", None))
        self.label_5.setText(QCoreApplication.translate("FSO_SENDER", u"File Size: ", None))





if __name__ == "__main__":
    import atexit
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_FSO_SENDER()
    ui.setupUi(mainWindow)
    # atexit.register(ui.CleanResources)
    mainWindow.show()
    sys.exit(app.exec_())