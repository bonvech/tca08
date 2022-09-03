import sys
import socket
import time
import datetime
from datetime import datetime
#import pandas as pd
import os
import serial
# for bot
import telebot
import config



class TCA08_device:
    def __init__(self):
        self.develop = False ## flag True for develop stage
        self.logfilename = "tca08_log.txt"

        self.MINID = 0
        self.MAXID = 0
        self.pathfile = None  ## data directory name

        ##  COM port properties
        self.portName = None
        self.BPS = 115200
        self.PARITY   = serial.PARITY_NONE
        self.STOPBITS = serial.STOPBITS_ONE
        self.BYTESIZE = serial.EIGHTBITS
        self.TIMEX = 1

        ## for data files
        #self.yy = '0'        ##  year for filename of raw file
        #self.mm = '0'        ## month for filename of raw file
        #self.yy_D = '0'      ##  year for filename of D-file
        #self.mm_D = '0'      ## month for filename of D-file 
        #self.xlsfilename = ''      ## exl file name
        #self.file_raw = None       ## file for raw data
        #self.file_format_D = None  ## file for raw data

        self.buff = ''
        self.info = ''
        self.device_name = None

        self.file_header = ''
        self.fill_header()  ## fill header

        self.timestamp = str(datetime.now())[:7]
        if 'ix' in os.name:
            self.sep = '/'  ## -- path separator for LINIX
        else:
            self.sep = '\\' ## -- path separator for Windows
            
        ## write to log file
        message = "\n============================================\n" + str(datetime.now()) + '  start'
        self.print_message(message, '\n')



    ## ----------------------------------------------------------------
    ##  Print message to logfile
    ## ----------------------------------------------------------------
    def print_message(self, message, end=''):
        print(message)
        flog = open(self.logfilename,'a')
        flog.write(message + end)
        flog.close()


    ## ----------------------------------------------------------------
    ##  Fill header for data file
    ## ----------------------------------------------------------------
    def fill_header(self):
        self.file_header = ""


    ## ----------------------------------------------------------------
    ## read config params from file tca08_config.py as a python module
    ## ----------------------------------------------------------------
    def read_path_file(self):
        # check file
        try:
            import tca08_config as tcaconfig
        except:
            print("\nread_path_file Error!! No file  tsa08_config to read config\n\n")
            return -1

        self.portName = tcaconfig.COM
        self.MINID = int(tcaconfig.MINID)
        self.MAXID = self.MINID
        self.pathfile = tcaconfig.path
        self.compname = tcaconfig.computer

        try:
            self.develop = tcaconfig.develop
        except:
            pass

        if self.develop == True:
            print("--------------------------------------------")
            print("  Warning!   Run in emulation mode!    ")
            print("--------------------------------------------")
        self.prepare_dirs()


    ## ----------------------------------------------------------------
    ##  make dirs to save data
    ## ----------------------------------------------------------------
    def prepare_dirs(self):
        ## \todo ПОПРАВИТЬ в конфигурацилонном файле СЛЕШИ В ИМЕНИ ДИРЕКТОРИИ  !!!   для ВИНДА
        if 'ix' in os.name:
            sep = '/'  ## -- separator for LINIX
        else:
            sep = '\\' ## -- separator for Windows

        path = self.pathfile
        if not os.path.exists(path):   os.system("mkdir " + path)

        ## make dirs for different data files
        dirs = ['Data', 'OffLineData', 'OnLineResult', 'Logs', 'table', 'ExtDeviceData', 'Setup']
        for name in dirs:
            path = self.pathfile + sep + name
            if not os.path.exists(path):   os.system("mkdir " + path)


    ## ----------------------------------------------------------------
    ## save config to bak file
    ## ----------------------------------------------------------------
    def write_path_file(self):
        filename = "tca08_config.py.bak"
        if not self.pathfile:
            print("\nwrite_path_file Error!!: no data to write to file ", filename, '\n')
            return -1

        f = open(filename, 'w')
        f.write("# Attention! Write with python sintax!!!!\n")
        f.write("#\n#\n# Directory for DATA:\n#\n")
        f.write("path = '" + self.pathfile + "'\n")

        f.write("#\n#\n# TCA08:   Serial Port:\n#\n")
        f.write("COM = '" + self.portName + "'\n")

        f.write("#\n#\n# TCA08:  Last Records:\n#\n")
        f.write("MINID = " + str(self.MINID) + "\n")
        f.close()


    ## ----------------------------------------------------------------
    ## print params from config file
    ## ----------------------------------------------------------------
    def print_params(self):
        print("Directory for DATA: ", self.pathfile)
        print("portName = ", self.portName)
        #print("BPS = ",      self.BPS)
        #print("STOBITS  = ", self.STOPBITS)
        #print("PARITY   = ", self.PARITY)
        #print("BYTESIZE = ", self.BYTESIZE)
        #print("TIMEX = ",    self.TIMEX)
        print("MINID = ",    self.MINID)


    ## ----------------------------------------------------------------
    ## Open COM port
    ## ----------------------------------------------------------------
    def connect(self):
        if self.develop == True:
            print("connect(): WARNING!!! Device run in simulation mode!!!\n")
            return
        try:
            self.ser = serial.Serial(
                port =     self.portName,
                baudrate = self.BPS,       # 115200,
                parity =   self.PARITY,    # serial.PARITY_NONE,
                stopbits = self.STOPBITS,  # serial.STOPBITS_ONE,
                bytesize = self.BYTESIZE,  # serial.EIGHTBITS
                timeout  = 10
                )
            if (self.ser.isOpen()):
                self.print_message("COM port open success\n")
                return 0
            print("COM port open failed\n")
            
        except serial.serialutil.SerialException:
            print("\n\nError in connect(): !!!!!!!! \nException type: serial.serialutil.SerialException")
            print("Problem with port", self.portName)
        except Exception as inst:
            print("\n\nError in connect(): !!!!!!!! except Exception: ")
            print("Exception type:", type(inst))    # the exception instance
            #print(inst.args)    # arguments stored in .args
            print("Exception args:", inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasses
        
        text = f"TCA08 port error: cannot connect to {self.portName} port"
        bot = telebot.TeleBot(config.token, parse_mode=None)
        bot.send_message(config.channel, text)
        ## write to log file
        message = str(datetime.now()) + ' ' + text
        self.print_message(message, '\n')
        
        return -1


    ## ----------------------------------------------------------------
    ## Close COM port
    ## ----------------------------------------------------------------
    def unconnect(self):
        if self.develop == True:
            print("unconnect(): WARNING!!! Device run in simulation mode!!!\n")
            return
        self.ser.close() # Закройте порт


    ## ----------------------------------------------------------------
    ## Send request to COM port
    ## ----------------------------------------------------------------
    def request(self, command, start=0, stop=0):
        if self.develop == True:
            self.print_message("request(): WARNING!!! Device run in simulation mode!!!\n")
            return -1

        #f = open(self.logfilename, 'a') 
        self.buff = ""

        if command == '$TCA:STREAM 0':
            command += ' ' + str(start) + ' ' + str(stop)
        command += '\r\n'
        #print(command)
        #f.write(str(command[:-1]))

        ## write command to COM port
        try:
            self.ser.write(command.encode())
        except:
            text = '\nrequest(): Error in writing to COM port!\n Check: COM port is open?'
            print(text)
            #f.write(text + '\n')
            #f.close()
            return -1

        ## read answer from buffer
        if not 'END' in command:
            time.sleep(1)
            while self.ser.in_waiting:
                #line = str(self.ser.readline())
                line = self.ser.readline().decode()
                if (line):
                    self.buff += line #.decode()
                    #print("{{"+line+"}}")
                    #f.write("{{"+str(line)+"}}\n")
                    line = 0
            #self.buff = self.buff.decode()
            if len(self.buff) == 0:
                text = 'Warning!! No answer to request for command' + command[:-2]
                print(text)
                #f.write(text + '\n')
            print('request(): buff =>', self.buff, "<=", sep='')
            #f.write('request(): buff =>' + self.buff + "<=")
        #f.write("\n")
        #f.close()
        return 0


    ## ----------------------------------------------------------------
    ##  Replace three columns with time to one datetime column and insert ","
    ## ----------------------------------------------------------------
    def join_datetime_in_string(self, s):
        #print(s)
        s = s.split()
        while "PM" in s or "AM" in s:
            marker = "PM" if "PM" in s else "AM"
            k = s.index(marker)
            datestamp = " ".join(s[k-2:k+1])
            #print("datastamp:", datestamp, end=' ')
            datestamp = datetime.strptime(datestamp, "%m/%d/%Y %I:%M:%S %p")
            #print("datastamp:", datestamp)
            s.insert(k+1, str(datestamp.strftime("%Y-%m-%d %H:%M:%S")))
            s = s[:k-2] + s[k+1:] ## удалить столбцы со временем, датой и AM/PM
        #print(s)
        return ','.join(s)


    ## ----------------------------------------------------------------
    ##  Find "Wait" and "sample" and join it to "Wait sample"
    ## ----------------------------------------------------------------
    def join_status_in_string(self, s):
        s = s.split(',')
        while "Wait" in s:
            k = s.index("Wait")
            s[k] = s[k] + ' ' + s[k+1]
            s.pop(k+1)  ## удалить столбцы со временем, датой и AM/PM
        return ','.join(s)


    ## ----------------------------------------------------------------
    ##  Get info from device
    ## ----------------------------------------------------------------
    def get_info(self):
        #flog = open(self.logfilename, 'a') 
        if self.develop == False:
            self.request('$TCA:INFO', 0, 0)
        else:
            self.buff = (
                          b'Instrument name: Total Carbon Analyzer\r\n'
                        + b'Model number: TCA08\r\n'
                        + b'Serial Number: TCA-08-S02-00209\r\n'
                        + b'Firmware version: 314\r\n'
                        + b'Software version: 1.3.2.0\r\n'
                        + b'Current date and time: 5/19/2022 1:28:13 PM\r\n'
                        ).decode()
        #print(type(self.buff))
        self.info = self.buff
        text = "-------------------\nINFO:\n" + self.info
        print(text, sep='')
        #flog.write(text + '\n')
        #flog.close()
        if 'ix' in os.name:
            self.buff = self.buff.split("\n")   ## for Linux
        else:
            self.buff = self.buff.split("\r\n") ## for Windows
        for line in self.buff[::]:
            if "Serial Number" in line:
                self.device_name = line.split()[-1]
                text = "Device name =>" + self.device_name + "<="
                self.print_message(text)


    ## ----------------------------------------------------------------
    ##  Get EXTDEVICEDATA
    ## ----------------------------------------------------------------
    def get_ext_device_data(self):
        typename = 'ExtDeviceData'
        
        ## ask for data
        if self.develop == False:
            self.request('$TCA:LAST EXTDEVICEDATA')
        else:
            self.buff = (b'4198813 4472972 18 14 52 989.2 4.4 0\r\n').decode()
        text = "-------------------\nEXTDEVICEDATA:\n" + self.buff
        #self.print_message(text)

        ## open datafile
        head_txt = "DataID,TimeStamp,DeviceID,DeviceData"
        head_csv = "TimeStamp,DataID,DataID2,DeviceID,DeviceData"
        head = {'.csv': "DataID,TimeStamp,DeviceID,DeviceData", 
                '.txt': "TimeStamp,DataID,DataID2,DeviceID,DeviceData"}
        datestamp = str(datetime.now())

        ## erite to datafile
        for filetype in {'.csv', '.txt'}:
            filename = self.pathfile + self.sep + typename + self.sep
            filename += self.timestamp + "_" + typename + filetype
            if not os.path.exists(filename):
                fdat = open(filename, 'a')
                fdat.write(head[filetype] + "\n")
            else:
                fdat = open(filename, 'a')
                
            ## compose dataline
            if "txt" in filetype:
                data = [datestamp,]
                data += self.buff.split()[:3]
            else:
                data = [self.buff.split()[1], datestamp, ]
                data.append(self.buff.split()[2])
            data.append(' '.join(self.buff.split()[3:]))
            #print(data)
            dataline = ",".join(data) + '\n'
            
            ## write to datafile    
            fdat.write(dataline)
            fdat.close()


    ## ----------------------------------------------------------------
    ##  Get DATA with '$TCA:LAST DATA' command
    ## ----------------------------------------------------------------
    def get_data(self):
        ##  read data from COM port
        #flog = open(self.logfilename, 'a') 
        if self.develop == False:
            self.request('$TCA:LAST DATA')
        else:
            self.buff = (b'4472971 5/19/2022 1:40:53 PM 20 60 1 2 1 0 0 0 1 Wait Sample 1432 S 1433 N n n n 16.6836 630 630 257 0 0 203 0 0 0 0 C C O O 43 27 0 0 0 0 0 0 0 0 0 0 0 0 29 29 31 0 0 40 40 51.394 99.1449 419.198 0.08593589 7.37411 0.05046773 2.43565 12.26107 12 2201 60\r\n').decode()
            #self.buff = '1602383,2018-11-16 23:59:59.073,11,20,1,2,1,4,0,0,1,Standby,866,Standby,867,N,n,n,n,16.6347,0,635,255,0,0,203,0,0,0,0,C,C,O,O,100,31,0,0,0,0,0,0,0,0,0,0,0,0,34,33,34,60,0,40,40,51.4907,99.3099,842.182,0.1488839,11.8919,0.07915366,9.36399,11.90369'
        text = "-------------------\nDATA:\n" + self.buff
        print(text, sep='')
        #flog.write(text + '\n')
        #flog.close()

        ## reformat data to csv string
        self.buff = self.join_datetime_in_string(self.buff)
        self.buff = self.join_status_in_string(self.buff)

        ## write to datafile
        ## Data file header
        head = "ID TimeStamp SetupID Timebase G0_Status G1_Status G2_Status G3_Status G4_Status G5_Status G6_Status Ch1_Status Ch1_SampleID Ch2_Status Ch2_SampleID MainBoardStatus Ch1BoardStatus Ch2BoardStatus SensorBoardStatus FlowS setFlowS FlowS_RAW SamplePumpSpeed FlowA setFlowA FlowA_RAW AnalyticPumpSpeed Solenoid1 Solenoid2 Solenoid5 BallValve1 BallValve2 BallValve3 BallValve4 Ch1_Temp Ch2_Temp Ch1_Voltage1 setCh1Voltage1 Ch1_Current1 Ch1_Voltage2 setCh1Voltage2 Ch1_Current2 Ch2_Voltage1 setCh2Voltage1 Ch2_Current1 Ch2_Voltage2 setCh2Voltage2 Ch2_Current2 Ch1_SafetyTemp Ch2_SafetyTemp SafetyTempInt Fan1 Fan2 Fan3 Fan4 LicorTemp LicorPressure LicorCO2 LicorCO2abs LicorH2O LicorH2Oabs LicorH2Odewpoint LicorVoltage"

        #print("buff:", len(self.buff.split(',')), "head:", len(head.split()))
        typename = 'Data'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'
        newfile = True if not os.path.exists(filename) else False
        fdat = open(filename, 'a')
        if newfile:
            fdat.write(",".join(head.split()) + "\n")
        #f.write(",".join(self.buff.split()) + '\n')
        fdat.write(self.buff + '\n')
        fdat.close()


    ## ----------------------------------------------------------------
    ##  Get ONLINERESULT with '$TCA:LAST ONLINERESULT' command
    ## ----------------------------------------------------------------
    def get_online_result(self):
        #flog = open(self.logfilename, 'a') 
        if self.develop == False:
            self.request('$TCA:LAST ONLINERESULT')
        else:
            ## from COM port
            self.buff = (b'1411 1432 5/19/2022 9:00:00 AM 5/19/2022 10:00:00 AM 5/19/2022 12:00:00 PM 5/19/2022 1:00:00 PM 270.84 4669.2 4722 780 100 1 3942 780 414.88 988.91 1 20 433.513965697825 -0.052493927308238 0.0000621135375773269 -0.0000019112057832946 0.0000000107468045043784 -0.0000000000160651521958029 417.003817069674 -0.00519565725647155 0.0000407358928456258 -0.00000088209278033617 0.0000000036674856614354 -0.00000000000427524100286778\r\n').decode()
            ## from docs
            #self.buff = '1,3,2018-09-05 09:20:00,2018-09-05 09:40:00,2018-09-05 11:20:00,2018-09-05 11:40:00,1618.25,18529.02,58708,0,0,1,0,0,678.83,315.61,1,4,734.11151923016,0.007605128934671236,-0.0008426029126914941,1.2467680585602101e-5,-5.7904734574089255e-8,8.278151418589865e-11,721.7721108681338,0.07058174812424729,-0.0033522482678232687,4.1361800378848836e-5,-1.7473727839550791e-7,2.3652177675724055e-10'

        text = "-------------------\nONLINERESULT:\n" + self.buff
        print(text, sep='')
        #flog.write(text + '\n')
        #flog.close()

        ## reformat data to csv string
        self.buff = self.join_datetime_in_string(self.buff)

        ## write to datafile
        ## Data file header
        head = "ID SampleID StartTimeUTC EndTimeUTC StartTimeLocal EndTimeLocal TCcounts TCmass TCconc AE33_BC6 AE33_ValidData AE33_b OC EC CO2 Volume Chamber SetupID a1 b1 c1 d1 e1 f1 a2 b2 c2 d2 e2 f2"

        #print("buff:", len(self.buff.split(',')), "head:", len(head.split()))
        typename = 'OnLineResult'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'
        newfile = True if not os.path.exists(filename) else False
        fdat = open(filename, 'a')
        if newfile:
            fdat.write(",".join(head.split()) + "\n")
        #f.write(",".join(self.buff.split()) + '\n')
        fdat.write(self.buff + '\n')
        fdat.close()



    ## ----------------------------------------------------------------
    ##  Get OFFLINERESULT with '$TCA:LAST OFFLINERESULT' command
    ## ----------------------------------------------------------------
    def get_offline_result(self):
        #flog = open(self.logfilename, 'a') 
        if self.develop == False:
            self.request('$TCA:LAST OFFLINERESULT')
        else:
            ## simulate data from COM port
            self.buff = (b'\r\n').decode()
            ## from docs
            self.buff = '39,695,5_arso_20170215mm,2018-01-12 12:36:19,2018-01-12 13:36:19,17520.1621,214100,189335,1.1308,0,1,25,653.0881745453704,2.070347518278751,-0.015783676941518294,5.743388472621944e-5,-9.85991925184398e-8,6.435298788574163e-11,-1921.268617466437,20.638064759183404,- Error in docs'

        text = "-------------------\nOFFLINERESULT:\n" + self.buff
        print(text, sep='')
        #flog.write(text + '\n')
        #flog.close()

        ## write to datafileз
        ## Data file header
        head = "ID SampleID SampleName StartTimeUTC StartTimeLocal TCcounts TCmass TCconc PunchArea DryingTime Chamber SetupID a1 b1 c1 d1 e1 f1 a2 b2 c2 d2 e2 f2"

        print("buff len:", len(self.buff.split(',')), "head len:", len(head.split()))
        typename = 'OffLineData'
        filename = self.pathfile + self.sep + typename + self.sep
        #filename += 'OffLineData.csv'
        filename += self.timestamp + "_" + typename + '.csv'
        #print("filename: ", filename)
        if not os.path.exists(filename):
            fdat = open(filename, 'a')
            fdat.write(",".join(head.split()) + "\n")
        else:
            fdat = open(filename, 'a')
        #f.write(",".join(self.buff.split()) + '\n')
        fdat.write(self.buff + '\n')
        fdat.close()
        #print("end of get_offline_result()")



    ## ----------------------------------------------------------------
    ##  Get SETUP with '$TCA:LAST SETUP' command
    ## ----------------------------------------------------------------
    def get_setup(self):
        #flog = open(self.logfilename, 'a') 
        if self.develop == False:
            self.request('$TCA:LAST SETUP')
        else:
            ## from COM port
            self.buff = (b'\r\n').decode()
            ## from docs
            self.buff = '1,2017-09-26 14:19:05,TCA-08-S00-00000,16.7,0.5,4.91,7.31204978640517e-5,-0.0357400687309517,10.0655216405797,9.76321196119687e-7,-4.46034050051914e-6,0.0185413211101763,11.45,11.45,1,0,1,0,60,300,3,12,57,3,495,3,12,57,3,180,265,265,220,265,265,220,100,50,100,1,25,101.325,0.1.0.0,301,1,UTC,1,0,0,0.45, string from docs'
        text = "-------------------\nSETUP:\n" + self.buff
        print(text, sep='')
        #flog.write(text + '\n')
        #flog.close()

        ## write to datafile
        ## Data file header
        head = "ID TimeStamp SerialNumber SetFlowS SetFlowA Area FlowFormulaA FlowFormulaB FlowFormulaC FlowFormulaD FlowFormulaE FlowFormulaF CCch1 CCch2 SlopeTempCh1 InterceptTempCh1 SlopeTempCh2 InterceptTempCh2 SampleTime C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 P11 P12 P13 P21 P22 P23 A0 A2 A3 FlowRepStd Temp Pressure SoftwareVersion FirmwareVersion AE33_b TimeZone DST TimeProtocol BHparamID FilterIntegrity_threshold"

        print("buff:", len(self.buff.split(',')), "head:", len(head.split()))
        typename =  'Setup'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'
        #filename += 'Setup.csv'
        if not os.path.exists(filename):
            fdat = open(filename, 'a')
            fdat.write(",".join(head.split()) + "\n")
        else:
            fdat = open(filename, 'a')
        #.write(",".join(self.buff.split()) + '\n')
        fdat.write(self.buff + '\n')
        fdat.close()





    ## ----------------------------------------------------------------
    ##  END
    ## ----------------------------------------------------------------





##    def request(self, command, start, stop):
##        if command == 'FETCH DATA':
##            command += ' ' + str(start) + ' ' + str(stop)
##        command += '\r\n'
##        print(command)
##
##        ## --- send command ---
##        time.sleep(1)
##        ##self.sock.send(bytes(command))
##        bytes = self.sock.send(command.encode())
##        print(bytes)
##        ## \todo проверить, что все отправилось
##        if bytes != len(command):
##            print("request: Error in sending data!! ") 
##        print('sent ', bytes, ' to socket')
##
##        if "CLOSE" in command:
##            return 1
##
##        ## --- read data ---
##        time.sleep(1)
##        attempts = 0
##        buf = self.sock.recv(2000000)
##        print('qq,  buf(bytes)=',len(buf))
##        #print(buf)
##
##        buff2 = buf.decode("UTF-8")
##        buff2 = buff2.split("\r\nTCA>")
##        #print('qq,  buff2=',len(buff2),buff2)
##
##        #self.buff = buf.decode("UTF-8")
##        if "HELLO" in command:
##            self.buff = buff2[1]
##        else:
##            self.buff = buff2[0]
##
##        #print('qq,  self.buff=',len(self.buff))
##        #print(self.buff)
##        #self.buff = self.buff.split("TCA>")
##        #print(self.buff)
##
##        while(len(buf) == 0 and attempts < 10):
##            print('not data,  buf=',len(buf))
##            time.sleep(1)
##            buf = self.sock.recv(2000000)
##            print('qq,  buf(bytes)=',len(buf))
##            #print(buf)
##            buff2 = buf.decode("UTF-8")
##            buff2 = buff2.split("\r\nTCA>")
##            #self.buff = buf.decode("UTF-8")
##            if "HELLO" in command:
##                self.buff = buff2[1]
##            else:
##                self.buff = buff2[0]
##            #self.buff = self.buff.split("TCA>")
##            #print(self.buff)
##            attempts += 1
##        if attempts >= 10:
##            print("request: Error in receive")
##            self.sock.unconnect()
##            return 2
##        
##        if "MAXID" in command:
##            #self.buff = self.buff.split("TCA>")
##            #print(self.buff)
##            self.MAXID = int(self.buff)
##            print(self.MAXID)
##        if "MINID" in command:
##            #self.buff = self.buff.split("TCA>")
##            #print(self.buff)
##            self.MINID = int(self.buff)
##            print(self.MINID)
##        if '?' in command:
##            self.info = self.buff
##        if "FETCH" in command:
##            self.parse_raw_data()
##        if "TCA" in command:
##            if "TCA:D":
##                self.parse_format_D_data()            
##            if "TCA:W":
##                self.parse_format_W_data()            
##        return 0


    def parse_raw_data(self):
        if len(self.buff) < 10:
            return
        #self.buff = self.buff.split("TCA>")
        print(self.buff)
        for line in self.buff:
            if len(line) < 50:
                continue
            print(line)
            mm, dd, yy = line.split("|")[2][:10].split('/')
            if mm != self.mm or yy != self.yy:
                filename = '_'.join((yy, mm)) + '_TCA-S08-01006.raw'
                filename = self.pathfile +'\\raw\\' + filename
                print(filename)
                if self.file_raw:
                    self.file_raw.close()
                self.file_raw = open(filename, "a")
            self.file_raw.write(line)
            self.file_raw.write('\n')

        self.file_raw.flush()
        self.mm = mm
        self.yy = yy


    def parse_format_W_data(self):
        ## main
        print('qqqqqqqqqqq')
        if len(self.buff) < 10:
            return
        #self.buff = self.buff.split("TCA>")
        if 'ix' in os.name:
            self.buff = self.buff.split("\n")  ## for Linux
        else:
            self.buff = self.buff.split("\r\n") ## for Windows

        lastmm, lastyy = '0', '0'
        filename = ''
        lastline = ''
        need_check = True
        dateformat = "%Y/%m/%d %H:%M:%S"
        #print('lines:')
        #print(self.buff)

        ## for excel data
        header = self.file_header[self.file_header.find("Date"):].split("; ")
        columns = ['Date(yyyy/MM/dd)', 'Time(hh:mm:ss)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7', 'BB(%)']
        colnums = [header.index(x) for x in columns]      
        rows_list = []

        for line in self.buff[::-1]:
            #print('line:   ',line)
            yy, mm, _ = line.split()[0].split('/')
            #print(yy, mm)

            # for first line or new file
            if mm != lastmm or yy != lastyy:
                ##### ddat file 
                filename = '_'.join((yy, mm)) + '_TCA-S08-01006.wdat'
                filename = self.pathfile +'\wdat\\' + filename
                print(filename,mm,yy,lastmm,lastyy)
                try:
                    ## ddat file exists
                    f = open(filename, 'r')
                    lastline = f.readlines()[-1].split()
                    #print(lastline)
                    f.close()
                    print('3')
                    lasttime = lastline[0] + ' ' + lastline[1]
                    print('1  ',lasttime)
                    lasttime = datetime.strptime(lasttime, dateformat)
                    print('4',lastmm,lastyy,mm,yy)
                    need_check = True
                except:
                    ## no file
                    print('NOT FILE', filename)
                    f = open(filename, 'a')        
                    f.write(self.file_header)
                    f.close()
                    lastline = []
                    need_check = False 
                lastmm = mm
                lastyy = yy

            ## add line data to dataframe 
            line_to_dataframe = [line.split()[i] for i in colnums]
            #print("line_to_dataframe:>",line_to_dataframe)
            line_to_dataframe = line_to_dataframe[:2]\
                                + [int(x) for x in line_to_dataframe[2:-1]]\
                                + [float(line_to_dataframe[-1])]
            rows_list.append(line_to_dataframe)
            #print(rows_list)


            ## check line to be added to datafile
            if need_check: # and len(lastline):
                #print(line)
                nowtime  = line.split()[0] + ' ' + line.split()[1]
                #print(nowtime)
                nowtime  = datetime.strptime(nowtime,  dateformat)
                print(nowtime - lasttime)
                ## if line was printed earlier
                if nowtime <= lasttime:
                    continue

            need_check = False

            ## write to file
            f = open(filename, 'a')
            f.write(line+'\n')
            f.close()
            

##        ## ##### write dataframe to excel file
##        ## make dataFrame from list
##        excel_columns = ['Date', 'Time (Moscow)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6',
##            'BC7', 'BB(%)', 'BCbb', 'BCff', 'Date.1', 'Time (Moscow).1']
##        dataframe_from_buffer = pd.DataFrame(rows_list, columns=excel_columns[:-4])
##        ## add columns
##        dataframe_from_buffer['BCbb'] = dataframe_from_buffer['BB(%)'].astype(float) * dataframe_from_buffer['BC5'].astype(float) / 100
##        dataframe_from_buffer['BCff'] = (100 - dataframe_from_buffer['BB(%)'].astype(float)) / 100 *  dataframe_from_buffer['BC5'].astype(float)
##        dataframe_from_buffer['Date.1'] = dataframe_from_buffer['Date']
##        dataframe_from_buffer['Time (Moscow).1'] = dataframe_from_buffer['Time (Moscow)']
##        print(dataframe_from_buffer.head())
