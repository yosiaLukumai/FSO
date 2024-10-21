from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import serial
import serial.tools
import serial.tools.list_ports
import os
import time


# class DataSender(QThread):
#     # Signal to update progress in the main thread
#     progress = pyqtSignal(int)
#     finished = pyqtSignal()
#     error_occurred = pyqtSignal(str)
#     file_size = pyqtSignal(str)
#     speed_signal = pyqtSignal(float)

#     def __init__(self, mode, com_port=None, file_path=None, text_data=None, baudrate=115200, chunk_size=1024):
#         super().__init__()
#         self.mode = mode  # 1 for file mode, 0 for text mode
#         self.com_port = com_port
#         self.file_path = file_path
#         self.text_data = text_data
#         self.baudrate = baudrate
#         self.chunk_size = chunk_size
#         self.serial_port = None  # This will hold the serial connection

#     def create_header(self, file_type, file_size, chunk_size):
#         header = f"{file_type}|{file_size}|{chunk_size}\n"  # Using | as a delimiter
#         return header.encode('utf-8')  # Return encoded header


#     def set_com_port(self):
#         """ Set up the serial port connection. """
#         if self.com_port is None:
#             self.error_occurred.emit("No COM port provided.")
#             return False

#         try:
#             # Set the serial port (replace baudrate with your preferred rate)
#             self.serial_port = serial.Serial(self.com_port, baudrate=self.baudrate, timeout=1)
#             return True
#         except Exception as e:
#             self.error_occurred.emit(f"Error connecting to {self.com_port}: {str(e)}")
#             return False
    
#     def format_size(self, bytes_size):
#         """
#         Convert the size from bytes to KB, MB, or GB, depending on its magnitude.
#         :param bytes_size: Size in bytes
#         :return: Formatted string with the size in KB, MB, or GB
#         """
#         # Convert bytes to kilobytes
#         kb_size = bytes_size / 1024

#         if kb_size < 1000:
#             # If size is less than 1000 KB, return in KB
#             return f"{kb_size:.2f} KB"
        
#         # Convert kilobytes to megabytes
#         mb_size = kb_size / 1024

#         if mb_size < 1000:
#             # If size is less than 1000 MB, return in MB
#             return f"{mb_size:.2f} MB"
        
#         # Convert megabytes to gigabytes
#         gb_size = mb_size / 1024

#         # Return the size in GB
#         return f"{gb_size:.2f} GB"
    
#     def size_file(self):
#         return self.format_size(os.path.getsize(self.file_path)) if self.mode == 1 else self.format_size(self.text_data.encode('utf-8'))



#     def run(self):
#         """ Main function run in the thread. """
#         if not self.set_com_port():
#             return  # Exit if COM port couldn't be set up

#         try:
#             if self.mode == 1:
#                 self.send_file()
#             else:
#                 self.send_text()
#         except Exception as e:
#             print(e)
#             self.error_occurred.emit(f"Error: {str(e)}")
#         finally:
#             # Ensure the serial port is closed when done
#             if self.serial_port is not None:
#                 self.serial_port.close()
#             self.finished.emit()

#     def send_file(self):
#         if self.file_path is None:
#             self.error_occurred.emit("No file selected.")
#             return

#         # Get file size
#         file_size = os.path.getsize(self.file_path)
#         print(f" Size: {self.format_size(file_size)}")
#         self.file_size.emit(str(self.format_size(file_size)))
#         total_chunks = file_size // self.chunk_size + (1 if file_size % self.chunk_size != 0 else 0)
#         print(f"Sending file of size {file_size} bytes in {total_chunks} chunks.")
#         start_time = time.time()
#         bytes_sent = 0

#         with open(self.file_path, 'rb') as file:
#             for chunk_index in range(total_chunks):
#                 content = file.read(self.chunk_size)
#                 print(f"content: {content}")
#                 self.serial_port.write(content)
#                 bytes_sent += len(content)  # Track total bytes sent

#                 # Calculate elapsed time
#                 elapsed_time = time.time() - start_time
#                 if elapsed_time > 0:  # Avoid division by zero
#                     speed = bytes_sent / elapsed_time  # Bytes per second
#                     self.speed_signal.emit(speed)  # Emit speed
#                 self.progress.emit(int((chunk_index + 1) / total_chunks * 100))

    
  

#     def send_text(self):
#         if self.text_data is None:
#             self.error_occurred.emit("No text data provided.")
#             return

#         # Start time for speed calculation
#         start_time = time.time()
#         bytes_sent = 0  # Initialize total bytes sent

#         # Encode text
#         text_data = self.text_data.encode('utf-8')  # Encode the text
#         text_size = len(text_data)  # Get size in bytes
#         self.file_size.emit(str(self.format_size(text_size)))  # Emit the file size
#         total_chunks = text_size // self.chunk_size + (1 if text_size % self.chunk_size != 0 else 0)
#         print(f"Sending text of size {text_size} bytes in {total_chunks} chunks.")

#         for chunk_index in range(total_chunks):
#             # Slice the text data into chunks
#             chunk = text_data[chunk_index * self.chunk_size:(chunk_index + 1) * self.chunk_size]
#             self.serial_port.write(chunk)  # Send the chunk
#             bytes_sent += len(chunk)  # Track total bytes sent

#             # Calculate elapsed time
#             elapsed_time = time.time() - start_time
#             if elapsed_time > 0:  # Avoid division by zero
#                 speed_kbps = bytes_sent  / elapsed_time  # Convert to KB/s
#                 self.speed_signal.emit(speed_kbps)  # Emit speed in KB/s

#             # Emit progress
#             self.progress.emit(int((chunk_index + 1) / total_chunks * 100))


class DataSender(QThread):
    # Signal to update progress in the main thread
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    file_size = pyqtSignal(str)
    speed_signal = pyqtSignal(float)

    def __init__(self, mode, com_port=None, file_path=None, text_data=None, baudrate=115200, chunk_size=1024):
        super().__init__()
        self.mode = mode  # 1 for file mode, 0 for text mode
        self.com_port = com_port
        self.file_path = file_path
        self.text_data = text_data
        self.baudrate = baudrate
        self.chunk_size = chunk_size
        self.serial_port = None  # This will hold the serial connection

    def create_header(self, file_type, file_size, chunk_size):
        """
        Create a header string that contains file information.
        Format: "HEADER|FILE_TYPE:<file_type>|FILE_SIZE:<file_size>|CHUNK_SIZE:<chunk_size>|END_HEADER\n"
        """
        header = f"HEADER|FILE_TYPE:{file_type}|FILE_SIZE:{file_size}|CHUNK_SIZE:{chunk_size}|END_HEADER\n"
        return header.encode('utf-8')  # Return encoded header

    def set_com_port(self):
        """ Set up the serial port connection. """
        if self.com_port is None:
            self.error_occurred.emit("No COM port provided.")
            return False

        try:
            # Set the serial port (replace baudrate with your preferred rate)
            self.serial_port = serial.Serial(self.com_port, baudrate=self.baudrate, timeout=1)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error connecting to {self.com_port}: {str(e)}")
            return False

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

    def get_file_size(self):
        """ Return the size of the file or text data. """
        return os.path.getsize(self.file_path) if self.mode == 1 else len(self.text_data.encode('utf-8'))

    def run(self):
        """ Main function run in the thread. """
        if not self.set_com_port():
            return  # Exit if COM port couldn't be set up

        try:
            # Create header based on the mode (file or text)
            file_type = "mp4" if self.mode == 1 else "text"
            file_size = self.get_file_size()
            header = self.create_header(file_type, file_size, self.chunk_size)

            # Send the header first
            self.serial_port.write(header)
            # time.sleep(2)
            print(f"Header sent: {header.decode('utf-8')}")

            if self.mode == 1:
                self.send_file()
            else:
                self.send_text()
        except Exception as e:
            print(e)
            self.error_occurred.emit(f"Error: {str(e)}")
        finally:
            # Ensure the serial port is closed when done
            if self.serial_port is not None:
                self.serial_port.close()
            self.finished.emit()

    def send_file(self):
        """Send file data in chunks after sending the header."""
        if self.file_path is None:
            self.error_occurred.emit("No file selected.")
            return

        # Get file size
        file_size = os.path.getsize(self.file_path)
        print(f"Size: {self.format_size(file_size)}")
        self.file_size.emit(str(self.format_size(file_size)))
        total_chunks = file_size // self.chunk_size + (1 if file_size % self.chunk_size != 0 else 0)
        print(f"Sending file of size {file_size} bytes in {total_chunks} chunks.")
        start_time = time.time()
        bytes_sent = 0

        with open(self.file_path, 'rb') as file:
            for chunk_index in range(total_chunks):
                content = file.read(self.chunk_size)
                # print(f"Sending chunk: {content[:50]}...")  # Print the first 50 bytes of the chunk
                self.serial_port.write(content)
                bytes_sent += len(content)  # Track total bytes sent

                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:  # Avoid division by zero
                    speed = bytes_sent / elapsed_time  # Bytes per second
                    self.speed_signal.emit(speed)  # Emit speed
                self.progress.emit(int((chunk_index + 1) / total_chunks * 100))

    def send_text(self):
        """Send text data in chunks after sending the header."""
        if self.text_data is None:
            self.error_occurred.emit("No text data provided.")
            return

        # Start time for speed calculation
        start_time = time.time()
        bytes_sent = 0  # Initialize total bytes sent

        # Encode text
        text_data = self.text_data.encode('utf-8')  # Encode the text
        text_size = len(text_data)  # Get size in bytes
        self.file_size.emit(str(self.format_size(text_size)))  # Emit the file size
        total_chunks = text_size // self.chunk_size + (1 if text_size % self.chunk_size != 0 else 0)
        print(f"Sending text of size {text_size} bytes in {total_chunks} chunks.")

        for chunk_index in range(total_chunks):
            # Slice the text data into chunks
            chunk = text_data[chunk_index * self.chunk_size:(chunk_index + 1) * self.chunk_size]
            print(f"Sending chunk: {chunk[:50]}...")  # Print the first 50 bytes of the chunk
            self.serial_port.write(chunk)  # Send the chunk
            bytes_sent += len(chunk)  # Track total bytes sent

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:  # Avoid division by zero
                speed_kbps = bytes_sent / elapsed_time  # Bytes per second
                self.speed_signal.emit(speed_kbps)  # Emit speed

            # Emit progress
            self.progress.emit(int((chunk_index + 1) / total_chunks * 100))


class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Results")
        self.setGeometry(100, 100, 200, 100)

        layout = QVBoxLayout()

        self.label = QLabel("Name: ")
        layout.addWidget(self.label)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        layout.addWidget(self.closeButton)

        self.setLayout(layout)

    def center(self, parent):
        parent_geometry = parent.geometry()
        parent_center = parent_geometry.center()
        self_geometry = self.geometry()
        self_geometry.moveCenter(parent_center)
        self.setGeometry(self_geometry)
    
    def setTextResult(self, name):
        self.label.setText(f"{name}")

    def SetTitle(self, title):
        self.setWindowTitle(title)

class Ui_FSO_SENDER(object):
    def setupUi(self, FSO_SENDER):
        if not FSO_SENDER.objectName():
            FSO_SENDER.setObjectName(u"FSO_SENDER")
        FSO_SENDER.resize(620, 480)
        FSO_SENDER.setMinimumSize(QSize(620, 480))
        FSO_SENDER.setMaximumSize(QSize(630, 480))
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

        self.verticalLayoutWidget_2 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(10, 160, 321, 151))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textEdit = QTextEdit(self.verticalLayoutWidget_2)
        self.textEdit.setObjectName(u"textEdit")
        font2 = QFont()
        font2.setFamily(u"Terminal")
        font2.setPointSize(14)
        font2.setBold(True)
        font2.setWeight(75)
        self.textEdit.setFont(font2)
        self.textEdit.setStyleSheet(u"border:1px solid #003f88;\n""")

        self.verticalLayout_2.addWidget(self.textEdit)

        self.verticalLayoutWidget_3 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(90, 60, 161, 36))
        self.TtileBox = QVBoxLayout(self.verticalLayoutWidget_3)
        self.TtileBox.setObjectName(u"TtileBox")
        self.TtileBox.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget_3)
        self.label.setObjectName(u"label")
        font3 = QFont()
        font3.setFamily(u"Segoe Script")
        font3.setBold(True)
        font3.setWeight(75)
        self.label.setFont(font3)
        self.label.setLayoutDirection(Qt.LeftToRight)
        self.label.setStyleSheet(u"color: #fdc500; \n""background-color: none;\n""\n""")
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.TtileBox.addWidget(self.label)

        self.horizontalLayoutWidget_2 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(40, 120, 294, 37))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.Text_Mode = QPushButton(self.horizontalLayoutWidget_2)
        self.Text_Mode.setObjectName(u"Text_Mode")
        self.Text_Mode.setMinimumSize(QSize(0, 30))
        self.Text_Mode.setMaximumSize(QSize(16777215, 30))
        self.Text_Mode.setFont(font3)
        self.Text_Mode.setCursor(QCursor(Qt.PointingHandCursor))
        self.Text_Mode.setStyleSheet(u"")

        self.horizontalLayout_2.addWidget(self.Text_Mode)

        self.pushButton = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(0, 30))
        self.pushButton.setMaximumSize(QSize(16777215, 30))
        self.pushButton.setFont(font3)
        self.pushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton.setStyleSheet(u";")

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.Upload_Button = QPushButton(self.centralwidget)
        self.Upload_Button.setObjectName(u"Upload_Button")
        self.Upload_Button.setGeometry(QRect(110, 380, 136, 30))
        self.Upload_Button.setMinimumSize(QSize(0, 30))
        self.Upload_Button.setMaximumSize(QSize(16777215, 30))
        self.Upload_Button.setFont(font3)
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
        self.label_2.setFont(font3)
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
        self.horizontalLayoutWidget_3 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_3.setObjectName(u"horizontalLayoutWidget_3")
        self.horizontalLayoutWidget_3.setGeometry(QRect(10, 320, 321, 42))
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = QLineEdit(self.horizontalLayoutWidget_3)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 32))
        self.lineEdit.setMaximumSize(QSize(16777215, 32))
        font4 = QFont()
        font4.setFamily(u"Segoe Script")
        font4.setPointSize(11)
        font4.setBold(False)
        font4.setWeight(50)
        self.lineEdit.setFont(font4)

        self.horizontalLayout_3.addWidget(self.lineEdit)

        self.pushButton_2 = QPushButton(self.horizontalLayoutWidget_3)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(0, 32))
        self.pushButton_2.setMaximumSize(QSize(16777215, 32))
        self.pushButton_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_2.setFont(font4)

        self.horizontalLayout_3.addWidget(self.pushButton_2)

        self.verticalLayoutWidget_5 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_5.setObjectName(u"verticalLayoutWidget_5")
        self.verticalLayoutWidget_5.setGeometry(QRect(410, 10, 160, 41))
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.Status = QLabel(self.verticalLayoutWidget_5)
        self.Status.setObjectName(u"Status")
        self.Status.setFont(font3)
        self.Status.setStyleSheet(u"color:  #cae9ff; \n""background-color: none;")

        self.verticalLayout_3.addWidget(self.Status)

        self.FileInfo = QLabel(self.centralwidget)
        self.FileInfo.setObjectName(u"FileInfo")
        self.FileInfo.setGeometry(QRect(20, 210, 197, 31))
        font7 = QFont()
        font7.setFamily(u"SWItalt")
        font7.setBold(False)
        font7.setWeight(50)
        self.FileInfo.setFont(font7)
        self.FileInfo.setStyleSheet(u"color: #fb8500;\n""font-size:8 !important\n"";")
        self.horizontalLayoutWidget_4 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_4.setObjectName(u"horizontalLayoutWidget_4")
        self.horizontalLayoutWidget_4.setGeometry(QRect(420, 120, 161, 33))
        self.horizontalLayout_4 = QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.horizontalLayoutWidget_4)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(50, 16777215))
        self.label_5.setFont(font3)
        self.label_5.setStyleSheet(u"color:#fb8500;")

        self.horizontalLayout_4.addWidget(self.label_5)

        self.label_4 = QLabel(self.horizontalLayoutWidget_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font3)
        self.label_4.setStyleSheet(u"color:#fff;")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.circularProgressBar_Main = QFrame(self.centralwidget)
        self.circularProgressBar_Main.setObjectName(u"circularProgressBar_Main")
        self.circularProgressBar_Main.setGeometry(QRect(360, 170, 240, 240))
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
        font5 = QFont()
        font5.setFamily(u"Segoe UI")
        self.labelAplicationName.setFont(font5)
        self.labelAplicationName.setStyleSheet(u"color: #FFFFFF; background-color: none;")
        self.labelAplicationName.setAlignment(Qt.AlignCenter)

        self.infoLayout.addWidget(self.labelAplicationName, 0, 0, 1, 1)

        self.labelPercentageCPU = QLabel(self.layoutWidget)
        self.labelPercentageCPU.setObjectName(u"labelPercentageCPU")
        font6 = QFont()
        font6.setFamily(u"Roboto Thin")
        self.labelPercentageCPU.setFont(font6)
        self.labelPercentageCPU.setStyleSheet(u"color: rgb(115, 185, 255); padding: 0px; background-color: none;")
        self.labelPercentageCPU.setAlignment(Qt.AlignCenter)
        self.labelPercentageCPU.setIndent(-1)

        self.infoLayout.addWidget(self.labelPercentageCPU, 1, 0, 1, 1)

        self.labelCredits = QLabel(self.layoutWidget)
        self.labelCredits.setObjectName(u"labelCredits")
        self.labelCredits.setFont(font5)
        self.labelCredits.setStyleSheet(u"color: rgb(148, 148, 216); background-color: none;")
        self.labelCredits.setAlignment(Qt.AlignCenter)

        self.infoLayout.addWidget(self.labelCredits, 2, 0, 1, 1)

        self.circularBg.raise_()
        self.circularProgressCPU.raise_()
        self.circularContainer.raise_()
        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(360, 10, 41, 41))
        self.pushButton_3.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_3.setStyleSheet(u"background-color:none;")
        icon = QIcon()
        icon.addFile(u"C:/Users/Yosia/Desktop/_/FSO/FSO_SENDER/Software/Sender/Refresh.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_3.setIcon(icon)
        self.pushButton_3.setIconSize(QSize(22, 22))
        FSO_SENDER.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(FSO_SENDER)
        self.statusbar.setObjectName(u"statusbar")
        FSO_SENDER.setStatusBar(self.statusbar)

        self.retranslateUi(FSO_SENDER)
        QMetaObject.connectSlotsByName(FSO_SENDER)


        self.pushButton_3.clicked.connect(self.refreshComports)
        self.AvailableComports = []
        self.OperationMode = 1 # [1: FileMode, 2: TextMode]
        self.ConnecteCompin = False
        self.workingComportName = ""
        self.ObtainSerialPort()
        self.WorkinComport = None
        
        # self.DisableOtherFuctions()
        self.Text_Mode.clicked.connect(self.setTextMode)
        self.pushButton.clicked.connect(self.setFilesMode)
        self.pushButton_2.clicked.connect(self.openSelectFileDialog)
        self.Upload_Button.clicked.connect(self.UploadProcess)
        self.ConnectButton.clicked.connect(self.ChangePorts)
        self.workingFile = ""
        self.AlertDialog = MyDialog()

    def ChangePorts(self):
        ThereComport = False
        if self.ComportSelector.currentText() != "":
            self.Status.setText(self.ComportSelector.currentText())
            ThereComport = True
        else:
            self.Status.setText(" No comport")
        
        self.workingComportName = self.ComportSelector.currentText()
        # try:
        #     SerialPort = self.ComportSelector.currentText()
        #     if ThereComport:
        #         self.WorkinComport = serial.Serial(port=SerialPort,baudrate=115200,timeout=1)
        # except Exception as e:
        #     pass

    def openSelectFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(None,"Select File to Upload","","All Files (*);;Text Files (*.txt)",options=options,)
        if fileName:
            # set file name equal to selected...
            self.lineEdit.setText(fileName)
            self.workingFile = fileName
            self.Upload_Button.setGeometry(QRect(110, 225, 136, 30))
            self.FileInfo.setText("")
        else:
            # failed to load file we have to give an alert
            font7 = QFont()
            font7.setFamily(u"SWItalt")
            font7.setBold(False)
            font7.setWeight(50)
            font7.setPixelSize(7)
            self.FileInfo.setFont(font7)
            self.FileInfo.setText("Select First File...")
            self.Upload_Button.setGeometry(QRect(110, 242, 136, 30))

        
    def refreshComports(self):
        self.ObtainSerialPort()
    
    def setTextMode(self):
        self.OperationMode = 2
        self.TextMode()
        self.FileInfo.setText("")

    def setFilesMode(self):
        self.OperationMode = 1
        self.FileMode()

    def DisableOtherFuctions(self):
        print(len(self.AvailableComports))
        if len(self.AvailableComports) == 0:
            self.lineEdit.setDisabled(True)
            self.pushButton.setDisabled(True)
            self.pushButton_2.setDisabled(True)
            self.Upload_Button.setDisabled(True)
            self.Text_Mode.setDisabled(True)
            self.circularProgressBar_Main.hide()
        else:
            self.lineEdit.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.Upload_Button.setEnabled(True)
            self.Text_Mode.setEnabled(True)
            self.circularProgressBar_Main.show()
        
    def TextMode(self):
        self.verticalLayoutWidget_2.show()
        self.horizontalLayoutWidget_3.hide()
        self.Upload_Button.setGeometry(QRect(110, 320, 136, 30))


    def EnableFuncs(self):
        pass

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


    def UploadProcess(self):
        # Update on the port selected and used..
        # self.Status.setText(f"{self.ComportSelector.currentText()}")
        try:
            if (len(self.AvailableComports) == 0) and (self.workingFile == "") :
                if len(self.AvailableComports) == 0:
                    self.AlertDialog.setWindowTitle("Error")
                    self.AlertDialog.setTextResult(" ERR: Please  Check Comport..  ")
                    self.AlertDialog.center(mainWindow)
                    self.AlertDialog.exec_()  
                else:
                    self.AlertDialog.setWindowTitle("Error")
                    self.AlertDialog.setTextResult(" ERR: Please Choose File or Write Text first..  ")
                    self.AlertDialog.center(mainWindow)
                    self.AlertDialog.exec_()
                return

            if self.workingComportName == "" or self.workingComportName == None:
                self.AlertDialog.setWindowTitle("Error")
                self.AlertDialog.setTextResult(" Hooray: Select serial port.  ")
                self.AlertDialog.center(mainWindow)
                self.AlertDialog.exec_()
                return


            else:
                print(self.ComportSelector.currentText())
                SerialPort = self.ComportSelector.currentText() 
                # if self.WorkinComport  == None or (self.WorkinComport.name != SerialPort):
                if SerialPort == "":
                    print(SerialPort, self.WorkinComport.name(), self.WorkinComport)
                    self.AlertDialog.setWindowTitle("Error")
                    self.AlertDialog.setTextResult(" ERR: Connect first Comport")
                    self.AlertDialog.center(mainWindow)
                    self.AlertDialog.exec_()  
                    return
                else:
                    pass
                print("reached...")
                if self.OperationMode == 1:
                    # deal with file uploading process
                    if self.workingFile == "":
                        self.AlertDialog.setWindowTitle("Error")
                        self.AlertDialog.setTextResult(" ERR: Select File First")
                        self.AlertDialog.center(mainWindow)
                        self.AlertDialog.exec_()
                        return
                    else:
                        try:
                            self.worker = DataSender(mode=self.OperationMode, com_port=self.workingComportName, file_path=self.workingFile)
                            self.worker.progress.connect(self.update_progress)
                            self.worker.finished.connect(self.transfer_finished)
                            self.worker.error_occurred.connect(self.show_error)
                            self.worker.speed_signal.connect(self.update_speed)
                            self.worker.file_size.connect(self.file_size)
                            self.worker.start()
                            # size = os.path.getsize(self.workingFile)
                            # self.label_4.setText(self.format_size(size/1024))
                            # with open(self.workingFile, 'rb') as file:
                            #     while(content := file.read(102400)):
                            #         self.WorkinComport.write(content)
                    
                        except Exception as e:
                            print(e)
                            self.AlertDialog.setWindowTitle("Error")
                            self.AlertDialog.setTextResult(" ERR: Something Went Wrong while trying to Read File.. Retry ")
                            self.AlertDialog.center(mainWindow)
                            self.AlertDialog.exec_()
                                     
                else:
                    if len(self.textEdit.toPlainText()) > 20:
                        try:
                            # textData = self.textEdit.toPlainText().encode('utf-8')
                            # text_size_bytes = len(textData)
                            # text_size_kb = text_size_bytes / 1024
                            # formatted = self.format_size(text_size_kb)
                            # print(formatted)
                            # self.label_4.setText(formatted)
                            # print(self.OperationMode)
                            self.worker = DataSender(mode=self.OperationMode, com_port=self.workingComportName, text_data=self.textEdit.toPlainText())
                            self.worker.progress.connect(self.update_progress)
                            self.worker.finished.connect(self.transfer_finished)
                            self.worker.error_occurred.connect(self.show_error)
                            self.worker.speed_signal.connect(self.update_speed)
                            self.worker.file_size.connect(self.file_size)
                            self.worker.start()

                            
                            # chunk_size = 1024
                            # # Loop through the text and send it in chunks
                            # for i in range(0, len(textData), chunk_size):
                            #     chunk = textData[i:i + chunk_size]
                            #     self.WorkinComport.write(chunk)
                        except Exception as e:
                            print("Error in the ")
                            print(e)
                    else:
                        self.AlertDialog.setWindowTitle("Error")
                        self.AlertDialog.setTextResult(" Hooray: Increase the text count ")
                        self.AlertDialog.center(mainWindow)
                        self.AlertDialog.exec_()



                        
        except Exception as e:
            print("it's her.....")
            print(e)
            if(e.__cause__ == None):
                self.AlertDialog.setWindowTitle("Error")
                self.AlertDialog.setTextResult(" ERR: Connect first Comport")
                self.AlertDialog.center(mainWindow)
                self.AlertDialog.exec_()  

        # first we have to esure the port is connected 
        


    def FileMode(self):
        self.verticalLayoutWidget_2.hide()
        self.horizontalLayoutWidget_3.setGeometry(QRect(10, 150, 321, 71))
        self.horizontalLayoutWidget_3.show()
        self.Upload_Button.setGeometry(QRect(110, 225, 136, 30))
    
    def UploadingMode(self):
        pass

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

        # self.DisableOtherFuctions()
        if self.OperationMode == 1:
            self.FileMode()
        else:
            self.TextMode()
    def update_progress(self, value):
        self.labelPercentageCPU.setText(str(value))
        self.progressBarValue(color="rgba(85, 170, 255, 255)", widget=self.circularProgressCPU, value=value)

    def transfer_finished(self):
        print("Status: Transfer Complete")

    def show_error(self, error_message):
        self.AlertDialog.setWindowTitle("Error")
        self.AlertDialog.setTextResult(error_message)
        self.AlertDialog.center(mainWindow)
        self.AlertDialog.exec_()
    
    def file_size(self, size):
        print("size")
        print(size)
        self.label_4.setText(size)

    def update_speed(self, speed):
        speed_kbps = speed / 1024
        self.labelCredits.setText(f"{speed_kbps:.2f} KB/s")

    def CleanResources(self):
        try:
            self.WorkinComport.close()
        except Exception as e:
            print("E", e)

    def retranslateUi(self, FSO_SENDER):
        FSO_SENDER.setWindowTitle(QCoreApplication.translate("FSO_SENDER", u"FSO_SENDER", None))
        self.ConnectButton.setText(QCoreApplication.translate("FSO_SENDER", u"Connect", None))
        self.textEdit.setHtml(QCoreApplication.translate("FSO_SENDER", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n""<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n""p, li { white-space: pre-wrap; }\n""</style></head><body style=\" font-family:'Terminal'; font-size:14pt; font-weight:600; font-style:normal;\">\n""<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Terminal','Segoe Script';\"><br /></p></body></html>", None))
        self.label.setAccessibleDescription(QCoreApplication.translate("FSO_SENDER", u"0", None))
        self.label.setText(QCoreApplication.translate("FSO_SENDER", u"Input Section", None))
        self.Text_Mode.setText(QCoreApplication.translate("FSO_SENDER", u"Text Mode", None))
        self.pushButton.setText(QCoreApplication.translate("FSO_SENDER", u"File Mode", None))
        self.Upload_Button.setText(QCoreApplication.translate("FSO_SENDER", u"Upload", None))
        self.label_2.setAccessibleDescription(QCoreApplication.translate("FSO_SENDER", u"0", None))
        self.label_2.setText(QCoreApplication.translate("FSO_SENDER", u"Monitoring Section", None))
        self.lineEdit.setText(QCoreApplication.translate("FSO_SENDER", u"  Select A file. png or txt", None))
        self.pushButton_2.setText(QCoreApplication.translate("FSO_SENDER", u"Select", None))
        self.Status.setText(QCoreApplication.translate("FSO_SENDER", u"Not conected", None))
        self.labelAplicationName.setText(QCoreApplication.translate("FSO_SENDER", u"<html><head/><body><p>% completion</p></body></html>", None))
        self.labelPercentageCPU.setText(QCoreApplication.translate("FSO_SENDER", u"<p align=\"center\"><span style=\" font-size:50pt;\">0</span><span style=\" font-size:40pt; vertical-align:super;\">%</span></p>", None))
        self.labelCredits.setText(QCoreApplication.translate("FSO_SENDER", u"<html><head/><body><p><span style=\" font-size:11pt;\">Speed:</span><span style=\" font-size:11pt; color:#ffffff;\"> 0Kb/s</span></p></body></html>", None))
        self.pushButton_3.setText("")
        self.label_5.setText(QCoreApplication.translate("FSO_SENDER", u"Size: ", None))
        self.label_4.setText(QCoreApplication.translate("FSO_SENDER", u"0 Kbs", None))



    

if __name__ == "__main__":
    import atexit
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_FSO_SENDER()
    ui.setupUi(mainWindow)
    atexit.register(ui.CleanResources)
    mainWindow.show()
    sys.exit(app.exec_())
