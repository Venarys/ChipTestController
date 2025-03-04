import sys
import time

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from UI.MainWindow import Ui_MainWindow
import cv2
import DahengCamera
import SerialPort
from PIL import Image
import ans_code

index2 = 0
flag = 0
img_list = ["raw.png", "img1.png", "img2.png"]
cac = [True, False, True]
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupWindow()

        self.ismoving = False
        self.is_auto = False
        self.Camera = DahengCamera.DahengCamera()
        self.Port = SerialPort.SerialPort()
        self.TimerForShowImageInGraphicsView = QTimer()
        self.ImageWidthInGraphicsView = 600
        self.scene = QGraphicsScene()

        self.SerialRecvTimer = QTimer()

        self.SlotInit() #槽函数初始化
        self.UpdateUI() #UI初始化

    """初始化槽信号函数"""
    def SlotInit(self):
        self.ui.pushButton_UpdateCameraList.clicked.connect(self.PB_UpdateCameraList_clicked)
        self.ui.pushButton_OpenCamera.clicked.connect(self.PB_OpenCamera_clicked)
        self.ui.pushButton_CloseCamera.clicked.connect(self.PB_CloseCamera_clicked)
        self.ui.pushButton_StartAcq.clicked.connect(self.PB_StartAcq_clicked)
        self.ui.pushButton_StopAcq.clicked.connect(self.PB_StopAcq_clicked)
        self.ui.pushButton_ZoomIn.clicked.connect(self.PB_ZoomIn_clicked)
        self.ui.pushButton_ZoomOut.clicked.connect(self.PB_ZoomOut_clicked)
        self.TimerForShowImageInGraphicsView.timeout.connect(self.SlotForShowImageInGraphicsView)
        self.ui.pushButton_SendSoftwareCommand.clicked.connect(self.SendSoftwareCommand)

        self.ui.pushButton_UpdatePortList.clicked.connect(self.PB_UpdatePortList_clicked)
        self.ui.pushButton_OpenPort.clicked.connect(self.PB_OpenPort_clicked)
        self.ui.pushButton_ClosePort.clicked.connect(self.PB_ClosePort_clicked)
        self.ui.pushButton_Send.clicked.connect(self.PB_sendClicked)
        self.SerialRecvTimer.timeout.connect(self.updataSerialData)
        self.UpdatePortUI()
        self.ui.pushButton_OpenPort_2.clicked.connect(self.PB_OpenPort_clicked_2)
        self.ui.pushButton_ClosePort_2.clicked.connect(self.PB_ClosePort_clicked_2)

        self.ui.pushButton_auto.clicked.connect(self.auto_mode)

        self.ui.toolButton_maximize.clicked.connect(self.maxOrNormal)
        self.ui.toolButton_minimize.clicked.connect(self.showMinimized)
        self.ui.toolButton_close.clicked.connect(self.queryExit)
        self.initPortPara()
        self.SlotConnect()

    def maxOrNormal(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def queryExit(self):
        QCoreApplication.instance().exit()

    def SlotConnect(self):
#        self.ui.comboBox_ExposureAuto.currentIndexChanged.connect(self.SetExposureAuto)
 #       self.ui.doubleSpinBox_ExposureTime.valueChanged.connect(self.SetExposureTime)
        self.ui.comboBox_TriggerMode.currentIndexChanged.connect(self.SetTriggerAuto)
        self.ui.comboBox_TriggerSource.currentIndexChanged.connect(self.SetTriggerSource)
        self.ui.comboBox_GainAuto.currentIndexChanged.connect(self.SetGainAuto)
        self.ui.doubleSpinBox_GainValue.valueChanged.connect(self.SetGainValue)

        self.ui.comboBox_baud.currentIndexChanged.connect(self.SetBaud)
        self.ui.comboBox_DataBit.currentIndexChanged.connect(self.SetDataBit)
        self.ui.comboBox_StopBit.currentIndexChanged.connect(self.SetStopBit)
        self.ui.comboBox_AuthBit.currentIndexChanged.connect(self.SetAuthBit)
    def SlotDisConnect(self):
#        self.ui.comboBox_ExposureAuto.currentIndexChanged.disconnect(self.SetExposureAuto)
 #       self.ui.doubleSpinBox_ExposureTime.valueChanged.disconnect(self.SetExposureTime)
        self.ui.comboBox_TriggerMode.currentIndexChanged.disconnect(self.SetTriggerAuto)
        self.ui.comboBox_TriggerSource.currentIndexChanged.disconnect(self.SetTriggerSource)
        self.ui.comboBox_GainAuto.currentIndexChanged.disconnect(self.SetGainAuto)
        self.ui.doubleSpinBox_GainValue.valueChanged.disconnect(self.SetGainValue)

    """ 更新UI界面"""
    def UpdateUI(self):
        self.ui.pushButton_OpenCamera.setDisabled(self.Camera.IsCameraOpened)
        self.ui.pushButton_CloseCamera.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.pushButton_StartAcq.setDisabled(not self.Camera.IsCameraOpened or self.Camera.IsCameraStartAcq)
        self.ui.pushButton_StopAcq.setDisabled(not self.Camera.IsCameraStartAcq)
#        self.ui.comboBox_ExposureMode.setDisabled(not self.Camera.IsCameraOpened)
#        self.ui.comboBox_ExposureAuto.setDisabled(not self.Camera.IsCameraOpened)
#        self.ui.doubleSpinBox_ExposureTime.setDisabled(not self.Camera.IsCameraOpened or
#                                                       not self.ui.comboBox_ExposureAuto.currentIndex() == 0)
        self.ui.pushButton_ZoomIn.setDisabled(not self.Camera.IsCameraStartAcq)
        self.ui.pushButton_ZoomOut.setDisabled(not self.Camera.IsCameraStartAcq)
        self.ui.comboBox_TriggerMode.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.comboBox_TriggerSource.setDisabled(not self.Camera.IsCameraOpened or
                                                   self.ui.comboBox_TriggerMode.currentIndex() == 0)
        self.ui.pushButton_SendSoftwareCommand.setDisabled(not self.Camera.IsCameraOpened or
                                                           self.ui.comboBox_TriggerMode.currentIndex() == 0 or
                                                           not self.ui.comboBox_TriggerSource.currentIndex() == 0)
        self.ui.comboBox_GainAuto.setDisabled(not self.Camera.IsCameraOpened)
        self.ui.doubleSpinBox_GainValue.setDisabled(not self.Camera.IsCameraOpened or
                                                    not self.ui.comboBox_GainAuto.currentIndex() == 0)

    def UpdatePortUI(self):
        self.ui.pushButton_OpenPort.setDisabled(self.Port.IsPortOpen_receive)
        self.ui.pushButton_ClosePort.setDisabled(not self.Port.IsPortOpen_receive)

    def UpdatePortUI_2(self):
        self.ui.pushButton_OpenPort_2.setDisabled(self.Port.IsPortOpen_send)
        self.ui.pushButton_ClosePort_2.setDisabled(not self.Port.IsPortOpen_send)
        self.ui.pushButton_Send.setDisabled(not self.Port.IsPortOpen_send)

    """ 更新相机参数的可选项目"""
    def UpdateCameraPara_Range(self):
        self.SlotDisConnect()

        # self.ui.comboBox_ExposureMode.clear()
        # for Range in self.Camera.GetExposureModeRange():
        #     #print(Range)
        #     self.ui.comboBox_ExposureMode.addItem(Range)
        #
        # self.ui.comboBox_ExposureAuto.clear()
        # for Range in self.Camera.GetExposureAutoRange():
        #     self.ui.comboBox_ExposureAuto.addItem(Range)

        self.ui.comboBox_TriggerMode.clear()
        for Range in self.Camera.GetTriggerAutoRange():
            self.ui.comboBox_TriggerMode.addItem(Range)

        self.ui.comboBox_TriggerSource.clear()
        for Range in self.Camera.GetTriggerSourceRange():
            self.ui.comboBox_TriggerSource.addItem(Range)

        self.ui.comboBox_GainAuto.clear()
        for Range in self.Camera.GetGainAutoRange():
            self.ui.comboBox_GainAuto.addItem(Range)

        self.SlotConnect()

    #init port para
    def initPortPara(self):
        self.ui.comboBox_baud.addItems([
            "300",
            "600",
            "1200",
            "2400",
            "4800",
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
            "12800"
        ])
        self.ui.comboBox_baud_2.addItems([
            "300",
            "600",
            "1200",
            "2400",
            "4800",
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
            "12800"
        ])
        self.ui.comboBox_baud.setCurrentIndex(5)
        self.ui.comboBox_baud_2.setCurrentIndex(5)

        self.ui.comboBox_DataBit.addItems([
            "5","6","7","8"
        ])
        self.ui.comboBox_DataBit_2.addItems([
            "5","6","7","8"
        ])
        self.ui.comboBox_DataBit.setCurrentIndex(3)
        self.ui.comboBox_DataBit_2.setCurrentIndex(3)

        self.ui.comboBox_StopBit.addItems([
            "1","1.5","2"
        ])
        self.ui.comboBox_StopBit_2.addItems([
            "1","1.5","2"
        ])
        self.ui.comboBox_AuthBit.addItems([
            "None","Even","Mark","Odd"
        ])
        self.ui.comboBox_AuthBit_2.addItems([
            "None","Even","Mark","Odd"
        ])

        self.ui.checkBox_hex_rec.setChecked(True)

    """ 读取相机当前参数值"""
    def GetCameraPara(self):
        self.SlotDisConnect()

        # ExposureAuto = self.Camera.GetExposureAuto()
        # self.ui.comboBox_ExposureAuto.setCurrentText(ExposureAuto[1])
        #
        # ExposureTime = self.Camera.GetExposureTime()
        # self.ui.doubleSpinBox_ExposureTime.setValue(ExposureTime)

        TriggerMode = self.Camera.GetTriggerAuto()
        self.ui.comboBox_TriggerMode.setCurrentText(TriggerMode[1])

        TriggerSource = self.Camera.GetTriggerSource()
        self.ui.comboBox_TriggerSource.setCurrentText(TriggerSource[1])

        GainAuto = self.Camera.GetGainAuto()
        self.ui.comboBox_GainAuto.setCurrentText(GainAuto[1])

        GainValue = self.Camera.GetGainValue()
        self.ui.doubleSpinBox_GainValue.setValue(GainValue)

        self.SlotConnect()

    """ 点击UpdateCameraList"""
    def PB_UpdateCameraList_clicked(self):
        status, CameraNameList = self.Camera.UpdateCameraList()
        if status:
            for CameraName in CameraNameList:
                self.ui.comboBox_CameraList.addItem(CameraName)

    #更新portlist
    def PB_UpdatePortList_clicked(self):
        status,PortNameList = self.Port.UpdatePortList()
        if status:
            for PortName in PortNameList:
                self.ui.comboBox_PortList.addItem(PortName)
                self.ui.comboBox_PortList_2.addItem(PortName)

    """ 点击OpenCamera"""
    def PB_OpenCamera_clicked(self):
        if self.ui.comboBox_CameraList.count() == 0:
            return
        self.Camera.OpenCamera(int(self.ui.comboBox_CameraList.currentIndex()) + 1)
        self.UpdateCameraPara_Range()
        self.GetCameraPara()

        self.UpdateUI()

    #click open port
    def PB_OpenPort_clicked(self):
        if self.ui.comboBox_PortList.count() == 0:
            return

        name = self.ui.comboBox_PortList.currentText()
        self.SetBaud()
        self.SetPortName()
        self.SetAuthBit()
        self.SetStopBit()
        self.SetDataBit()

        ok = self.Port.OpenPort_receive()
        if ok:
            #self.ui.plainTextEdit_Result.appendPlainText("串口"+name+"打开啦!")
            self.SerialRecvTimer.start(2)
            self.UpdatePortUI()

    def PB_OpenPort_clicked_2(self):
        if self.ui.comboBox_PortList.count() == 0:
            return

        name = self.ui.comboBox_PortList.currentText()
        self.SetBaud_2()
        self.SetPortName_2()
        self.SetAuthBit_2()
        self.SetStopBit_2()
        self.SetDataBit_2()

        ok = self.Port.OpenPort_send()
        if ok:
            self.UpdatePortUI_2()

    #click close port
    def PB_ClosePort_clicked(self):
        ok, name = self.Port.ClosePort_receive()
        if ok:
            self.SerialRecvTimer.stop()
            self.UpdatePortUI()

    def PB_ClosePort_clicked_2(self):
        ok, name = self.Port.ClosePort_send()
        if ok:
            self.UpdatePortUI_2()

    #click send button
    def PB_sendClicked(self):
        message = self.ui.textEdit_Send.toPlainText()
        is_hex = self.ui.checkBox_hex_send.isChecked()
        self.Port.SendMessage(message, is_hex)

    def setGraph(self):
        global img_index, img_list
        # time.sleep(0.1)
        x = ["mid", "res"]
        global flag, index2
        img = Image.open("img/"+x[flag]+str(index2)+".png")
        #img = Image.open("img1.png")
        img_array = np.array(img)
        DahengCamera.change(img_array)
        self.SlotForShowImageInGraphicsView()
        flag += 1
        if flag >= 2:
            self.setGTimer.stop()
            flag = 0
            index2 += 1
            # self.ui.plainTextEdit_Result.clear()

    def updataSerialData(self):
        is_hex = self.ui.checkBox_hex_rec.isChecked()
        data = self.Port.DataReceive(is_hex)
        if is_hex:
            self.ui.textBrowser_Recv.insertPlainText(data)

            if self.is_auto:
                if data == '5A 2E 20 2E 2E 2E 2E 2E 2E 2E 2E 0D 0A ':
                    # print("接受到拍照信号")
                    self.Camera.SendSoftWareCommand()
                    self.SlotForShowImageInGraphicsView()

                    # 进行图像处理，得到img1,img2,img3
                    #try:
                        # result = ans_code.VoidMain("raw.png", "img1.png", "img2.png")
                    global index2
                    if index2 > 2:
                        index2 = 0

                    self.ui.plainTextEdit_Result.clear()
                    with open("img/exp"+str(index2)+".txt", 'r', encoding="utf-8") as file:
                        line = file.readline()
                        text = line.split(",")
                        for i in text:
                            i = i.strip()
                            i = i.strip("'")
                            self.ui.plainTextEdit_Result.insertPlainText(i+'\n')

                        # if cac[index2]:
                        #     QtWidgets.QMessageBox.information(None, "检测结果", "芯片存在缺陷")
                        # else:
                        #     QtWidgets.QMessageBox.information(None, "检测结果", "芯片完好")

                    self.setGTimer = QTimer()
                    self.setGTimer.timeout.connect(self.setGraph)
                    self.setGTimer.start(1500)

                    if cac[index2]:
                        self.catchTimer = QTimer()
                        self.catchTimer.timeout.connect(self.Catch)
                        self.catchTimer.start(13140)
                    #except:
                    #    self.ui.plainTextEdit_Result.insertPlainText("芯片存在未知缺陷")
        else:
            if data != None:
                try:
                    self.ui.textBrowser_Recv.insertPlainText(data.decode('utf-8'))
                except:
                    pass

        self.ui.label_SentValue.setText(str(self.Port.sent_count))
        self.ui.label_ReceivedValue.setText(str(self.Port.recv_count))

    def Catch(self):
        global can_catch
        if can_catch:
            try:
                self.Port.SendMessage('1',False)
                can_catch = False
            except:
                QtWidgets.QMessageBox.critical(None, "机械臂", "机械臂故障")
        else:
            self.catchTimer.stop()
            can_catch = True

    """ 点击CloseCamera"""
    def PB_CloseCamera_clicked(self):
        self.Camera.CloseCamera(int(self.ui.comboBox_CameraList.currentIndex()) + 1)
        if self.TimerForShowImageInGraphicsView.isActive():
            self.TimerForShowImageInGraphicsView.stop()
        DahengCamera.num = 0

        self.UpdateUI()

    """ 点击StartAcq"""
    def PB_StartAcq_clicked(self):
        self.Camera.StartAcquisition()
        self.TimerForShowImageInGraphicsView.start(33)

        self.UpdateUI()

    """ 点击StopAcq"""
    def PB_StopAcq_clicked(self):
        self.Camera.StopAcquisition()
        self.TimerForShowImageInGraphicsView.stop()
        self.UpdateUI()

        DahengCamera.num = 0

    """ 点击ZoomIn"""
    def PB_ZoomIn_clicked(self):
        self.ImageWidthInGraphicsView += 100

    """ 点击ZoomOut"""
    def PB_ZoomOut_clicked(self):
        if self.ImageWidthInGraphicsView >= 200:
            self.ImageWidthInGraphicsView -= 100

    """ 图像显示回调函数"""
    def SlotForShowImageInGraphicsView(self):
        if DahengCamera.rawImageUpdate is None:
            return
        else:
            ImageShow = DahengCamera.rawImageUpdateList[0]
            ImageRatio = float(ImageShow.shape[0] / ImageShow.shape[1])
            image_width = self.ImageWidthInGraphicsView
            show = cv2.resize(ImageShow, (image_width, int(image_width * ImageRatio)))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            item = QGraphicsPixmapItem(QPixmap.fromImage(showImage))
            self.scene.clear()
            self.scene.addItem(item)
            self.scene.setSceneRect(0, 0, image_width + 1, image_width * ImageRatio + 1)
            self.ui.graphicsView.setScene(self.scene)
            self.ui.graphicsView.show()
            self.ui.label_AcqNum.setText(str(DahengCamera.num))
            self.ui.label_FPS.setText(str(self.Camera.GetFPS()))

    """ ExposureAuto值改变"""

    def SetExposureAuto(self):
        self.Camera.SetExposureAuto(self.ui.comboBox_ExposureAuto.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    #4 important parameter for ports
    def SetBaud(self):
        self.Port.SetBaudRate(self.ui.comboBox_baud.currentText())

    def SetBaud_2(self):
        self.Port.SetBaudRate_2(self.ui.comboBox_baud_2.currentText())

    def SetDataBit(self):
        self.Port.SetByteSize(self.ui.comboBox_DataBit.currentText())

    def SetDataBit_2(self):
        self.Port.SetByteSize_2(self.ui.comboBox_DataBit_2.currentText())

    def SetStopBit(self):
        self.Port.SetStopBits(self.ui.comboBox_StopBit.currentText())

    def SetStopBit_2(self):
        self.Port.SetStopBits_2(self.ui.comboBox_StopBit_2.currentText())

    def SetAuthBit(self):
        self.Port.SetParity(self.ui.comboBox_AuthBit.currentText())

    def SetAuthBit_2(self):
        self.Port.SetParity_2(self.ui.comboBox_AuthBit_2.currentText())

    def SetPortName(self):
        self.Port.SetPortName(self.ui.comboBox_PortList.currentText())

    def SetPortName_2(self):
        self.Port.SetPortName_2(self.ui.comboBox_PortList_2.currentText())

    """ ExposureTime改变"""

    def SetExposureTime(self):
        self.Camera.SetExposureTime(self.ui.doubleSpinBox_ExposureTime.value())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()

    """ TriggerMode改变"""

    def SetTriggerAuto(self):
        self.Camera.SetTriggerAuto(self.ui.comboBox_TriggerMode.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ TriggerSource改变"""

    def SetTriggerSource(self):
        self.Camera.SetTriggerSource(self.ui.comboBox_TriggerSource.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ 发送软触发"""

    def SendSoftwareCommand(self):
        self.Camera.SendSoftWareCommand()

    """ GainAuto改变"""

    def SetGainAuto(self):
        self.Camera.SetGainAuto(self.ui.comboBox_GainAuto.currentText())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()
        self.UpdateUI()

    """ GainValue值改变"""

    def SetGainValue(self):
        self.Camera.SetGainValue(self.ui.doubleSpinBox_GainValue.value())
        self.UpdateCameraPara_Range()
        self.GetCameraPara()

    def setupWindow(self):
        self.desktop = QDesktopWidget()
        self.screenRect = self.desktop.screenGeometry()
        self.screenheight = self.screenRect.height()
        self.screenwidth = self.screenRect.width()
        #print(self.screenwidth, self.screenheight)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.toolButton_close.setIcon(QIcon(":/images/UI/close.png"))
        self.ui.toolButton_maximize.setIcon(QIcon(":/images/UI/maximize.png"))
        self.ui.toolButton_minimize.setIcon(QIcon(":/images/UI/minimize.png"))

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            self.ismoving = True
            self.start_point = e.globalPos()
            self.window_point = self.frameGeometry().topLeft()

    def mouseReleaseEvent(self, e):
        self.ismoving = False

    def mouseMoveEvent(self, e):
        if self.ismoving:
            replos = e.globalPos() - self.start_point
            self.move(replos + self.window_point)

    def auto_mode(self):
        if not self.Camera.IsCameraOpened:
            QtWidgets.QMessageBox.critical(None, "你的相机呢", "相机未打开")
            return
        elif not self.Port.IsPortOpen_receive:
            QtWidgets.QMessageBox.critical(None, "你的串口呢", "串口未打开")
            return
        elif not self.ui.checkBox_hex_rec.isChecked():
            QtWidgets.QMessageBox.critical(None, "要十六进制", "未勾选十六进制接收")
            return
        elif self.ui.comboBox_TriggerMode.currentText() != 'On':
            QtWidgets.QMessageBox.critical(None, "触发模式", "要打开触发模式")
            return

        if self.is_auto:
            # self.TimerForShowImageInGraphicsView.timeout.connect(self.SlotForShowImageInGraphicsView)
            self.is_auto = False
            self.ui.pushButton_auto.setText("开启自动检测")
            self.ui.pushButton_SendSoftwareCommand.setEnabled(True)
            self.ui.comboBox_TriggerMode.setEnabled(True)
            self.Camera.set_auto_mode(False)
        else:
            # self.TimerForShowImageInGraphicsView.timeout.disconnect(self.SlotForShowImageInGraphicsView)
            self.is_auto = True
            self.ui.pushButton_auto.setText("关闭自动检测")
            self.ui.pushButton_SendSoftwareCommand.setDisabled(True)
            self.ui.comboBox_TriggerMode.setDisabled(True)
            self.Camera.set_auto_mode(True)

can_catch = True

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())