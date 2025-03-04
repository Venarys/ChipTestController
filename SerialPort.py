import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QMessageBox


def test():
    # 获取所有串口设备实例。
    # 如果没找到串口设备，则输出：“无串口设备。”
    # 如果找到串口设备，则依次输出每个设备对应的串口号和描述信息。
    ports_list = serial.tools.list_ports.comports()
    if len(ports_list) <= 0:
        print("无串口设备。")
    else:
        print("可用的串口设备如下：")
        for comport in ports_list:
            print(comport[0], comport[1])
        print(ports_list[0][0])
        print(ports_list[0][1])
        print(ports_list)
        #print(list(serial.tools.list_ports.comports()))
#test()

class SerialPort(object):
    def __init__(self):
        super().__init__()
        # 初始化serial对象 用于串口通信
        self.ser_send = None
        self.ser_receive = None
        self.port_num = None

        self.port_name_send = None
        self.baudrate_send = None
        self.bytesize_send = None
        self.parity_send = None
        self.stopbits_send = None

        self.port_name_receive = None
        self.baudrate_receive = None
        self.bytesize_receive = None
        self.parity_receive = None
        self.stopbits_receive = None

        self.port_info_list = None
        self.port_info_dict = {}
        self.IsPortOpen_send = False
        self.IsPortOpen_receive = False

        self.sent_count = 0
        self.recv_count = 0

    def UpdatePortList(self):
        self.port_info_list = serial.tools.list_ports.comports()
        self.port_num = len(self.port_info_list)
        if self.port_num == 0:
            return False,'0'
        else:
            portNameList = []
            for name in self.port_info_list:
                self.port_info_dict[name[1]] = name[0]
                portNameList.append(name[1])
            return True,portNameList

    def OpenPort_send(self):
        if self.port_num == 0:
            return False
        elif self.IsPortOpen_send:
            return False
        else:
            try:
                self.ser_send = serial.Serial(
                    port=self.port_name_send,
                    baudrate=self.baudrate_send,
                    bytesize=self.bytesize_send,
                    parity=self.parity_send,
                    stopbits=self.stopbits_send
                )
                self.IsPortOpen_send = True
                return True
            except:
                QMessageBox.critical(None,"哦不",self.port_name_send+"不存在！")
                return False

    def OpenPort_receive(self):
        if self.port_num == 0:
            return False
        elif self.IsPortOpen_receive:
            return False
        else:
            try:
                self.ser_receive = serial.Serial(
                    port=self.port_name_receive,
                    baudrate=self.baudrate_receive,
                    bytesize=self.bytesize_receive,
                    parity=self.parity_receive,
                    stopbits=self.stopbits_receive
                )
                self.IsPortOpen_receive = True
                return True
            except:
                QMessageBox.critical(None,"哦不",self.port_name_receive+"不存在！")
                return False

    def ClosePort_receive(self):
        if not self.IsPortOpen_receive:
            return (False,'xuyin')

        self.ser_receive.close()
        self.IsPortOpen_receive = False
        return (True,self.port_name_receive)

    def ClosePort_send(self):
        if not self.IsPortOpen_send:
            return (False,'xuyin')

        self.ser_send.close()
        self.IsPortOpen_send = False
        return (True,self.port_name_send)

    def SendMessage(self, message, is_hex):
        if self.IsPortOpen_send:
            if message != '':
                if is_hex:
                    message = message.strip()
                    send_list = []
                    while message != '':
                        try:
                            num = int(message[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(None,"不对","我要十六进制!")
                            return
                        else:
                            message = message[2:].strip()
                            send_list.append(num)
                    single_send_message = bytes(send_list)
                else:
                    single_send_message = (message + '\r\n').encode('utf-8')

                sent_num = self.ser_send.write(single_send_message)
                self.sent_count += sent_num
        else:
             QMessageBox.warning(None, "蠢", "没开串口！")

    def DataReceive(self,is_hex=False):
        try:
            num = self.ser_receive.inWaiting()
        except:
            pass
        else:
            if num > 0:
                data = self.ser_receive.read(num)
                received_num = len(data)
                self.recv_count += received_num
                if is_hex:
                    received_string = ''
                    for i in range(received_num):
                        # {:X}16进制标准输出形式 02是2位对齐 左补0形式
                        received_string = received_string + '{:02X}'.format(data[i]) + ' '
                    return received_string
                else:
                    return data
            else:
                return None

    #4 para and name
    def SetBaudRate(self, baudrate):
        self.baudrate_receive = int(baudrate)

    def SetByteSize(self, bytesize):
        self.bytesize_receive = int(bytesize)

    def SetParity(self, parity):
        pdict = {'None': 'N',
                 'Even': 'E',
                 'Odd': 'O',
                 'Mark': 'M',
                }
        self.parity_receive = pdict[parity]

    def SetStopBits(self, stopbits):
        sdict = {'1':1,'1.5':1.5,'2':2}
        self.stopbits_receive = sdict[stopbits]

    def SetPortName(self, port_name):
        self.port_name_receive = self.port_info_dict[port_name]

    def SetBaudRate_2(self, baudrate):
        self.baudrate_send = int(baudrate)

    def SetByteSize_2(self, bytesize):
        self.bytesize_send = int(bytesize)

    def SetParity_2(self, parity):
        pdict = {'None': 'N',
                 'Even': 'E',
                 'Odd': 'O',
                 'Mark': 'M',
                }
        self.parity_send = pdict[parity]

    def SetStopBits_2(self, stopbits):
        sdict = {'1':1,'1.5':1.5,'2':2}
        self.stopbits_send = sdict[stopbits]

    def SetPortName_2(self, port_name):
        self.port_name_send = self.port_info_dict[port_name]