import datetime
from datetime import datetime, date
from datetime import timedelta
import os
import pandas as pd
import serial
import socket
import sys
import time
import xlsxwriter

# for bot
import telebot
import telebot_config

#try:
from tca08_error_parser import *
#except:
#    print("\n!!!__init()__ Error!! No file \"tca08_error_parser.py\" to import!!!\n\n")
#    exit()



## ----------------------------------------------------------------
##  
## ----------------------------------------------------------------
def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return hostname, local_ip


## ----------------------------------------------------------------
##  
## ----------------------------------------------------------------
class TCA08_device:
    def __init__(self):
        self.develop = False ## flag True for develop stage
        self.logfilename = "tca08_log.txt"

        #self.MINID = 0
        #self.MAXID = 0
        self.pathfile = None  ## data directory name

        ##  COM port properties
        self.portName = None
        self.BPS = 115200
        self.PARITY   = serial.PARITY_NONE
        self.STOPBITS = serial.STOPBITS_ONE
        self.BYTESIZE = serial.EIGHTBITS
        self.TIMEX = 1

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
        if len(message) == 0:
            return
            
        print(message)

        #self.logfilename = self.logdirname + "_".join(["_".join(str(datetime.now()).split('-')[:2]), self.device_name.split()[0],  'log.txt'])
        with open(self.logfilename, 'a') as flog:
            #flog.write(str(datetime.now()) + ':  ')
            #flog.write(message + end)
            flog.write(f"{datetime.now()}: {message}{end}")


    ## ----------------------------------------------------------------
    ##  write message to bot
    ## ----------------------------------------------------------------
    def write_to_bot(self, text):
        try:
            hostname, local_ip = get_local_ip()
            text = f"{hostname} ({local_ip}): {text}"
            
            bot = telebot.TeleBot(telebot_config.token, parse_mode=None)
            #bot.send_message(telebot_config.channel, text)
            nmax = 4096 ## максимальная длина сообщения в телеграме
            for n in range((len(text) + nmax - 1)// nmax):
                bot.send_message(telebot_config.channel, text[nmax*n: nmax * (n+1)])

        except Exception as err:
            ##  напечатать строку ошибки
            text = f": ERROR in writing to bot: {err}"
            self.print_message(text)  ## write to log file


        


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
        #self.MINID = int(tcaconfig.MINID)
        #self.MAXID = self.MINID
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
        #f.write("MINID = " + str(self.MINID) + "\n")
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
        #print("MINID = ",    self.MINID)


    ## ----------------------------------------------------------------
    ## Open COM port
    ## ----------------------------------------------------------------
    def connect(self):
        if self.develop == True:
            print("connect(): WARNING!!! Device run in simulation mode!!!\n")
            return
            
        ##  Open COM port
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
   
        ##  if COM port open failed            
        except serial.serialutil.SerialException:
            print("\n\nError in connect(): !!!!!!!! \nException type: serial.serialutil.SerialException")
            print("Problem with port", self.portName)
            return -1

        except Exception as inst:
            print("\n\nError in connect(): !!!!!!!! except Exception: ")
            print("Exception type:", type(inst))    # the exception instance
            #print(inst.args)    # arguments stored in .args
            print("Exception args:", inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasses
        
            ## write errors to bot & log file
            text = f"TCA08 port error: cannot connect to {self.portName} port from {self.compname}"
            self.write_to_bot(text)
            
            message = f"{datetime.now()}  {text}"
            self.print_message(message, '\n')
            
            return -1

        return 0  ## OK
 

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

        self.buff = ""

        if command == '$TCA:STREAM 0':
            command += ' ' + str(start) + ' ' + str(stop)
        command += '\r\n'

        ## write command to COM port
        try:
            self.ser.write(command.encode())
        except:
            text = '\nrequest(): Error in writing to COM port!\n Check: COM port is open?'
            #print(text)
            self.print_message(text)
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
                    line = 0
            #self.buff = self.buff.decode()
            if len(self.buff) == 0:
                text = f"Warning!! No answer to request for command {command[:-2]}"
                self.print_message(text, '\n')
                return -1
            text = 'request(): buff =>' + self.buff + "<="
            #print(text)
            #self.print_message(text)
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
            s.pop(k+1)  ## удалить столбцы со вторым словом статуса
        return ','.join(s)


    ## ----------------------------------------------------------------
    ##  Get info from device
    ## ----------------------------------------------------------------
    def get_info(self):
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
        ## if no response
        if not len(self.buff):
            return
        
        self.info = self.buff
        text = "-------------------\nINFO:\n" + self.info
        print(text, sep='')

        if 'ix' in os.name:
            self.buff = self.buff.split("\n")   ## for Linux
        else:
            self.buff = self.buff.split("\r\n") ## for Windows

        for line in self.buff[::]:
            if "Serial Number" in line:
                self.device_name = line.split()[-1]

        text = "Device name =>" + self.device_name + "<="
        self.print_message(text, '\n')
        print("===============================")


    ## ----------------------------------------------------------------
    ##  Get EXTDEVICEDATA
    ## ----------------------------------------------------------------
    def get_ext_device_data(self, dummy=False):
        typename = 'ExtDeviceData'
        
        ## ask for data
        if not dummy:
            if self.develop == False:
                self.request('$TCA:LAST EXTDEVICEDATA')
            else:
                self.buff = (b'4198813 4472972 18 14 52 989.2 4.4 0\r\n').decode()
        else:
            self.buff = 'dummy dummy data'

        ## if no response
        if not len(self.buff):
            return

        text = "-------------------\nEXTDEVICEDATA:\n" + self.buff
        print(text, sep='')
        #self.print_message(text)

        ## open datafile
        head_txt = "DataID,TimeStamp,DeviceID,DeviceData"
        head_csv = "TimeStamp,DataID,DataID2,DeviceID,DeviceData"
        head = {'.csv': "DataID,TimeStamp,DeviceID,DeviceData", 
                '.txt': "TimeStamp,DataID,DataID2,DeviceID,DeviceData"}
        datestamp = str(datetime.now())

        ## write to datafile
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
                if not dummy:
                    data += self.buff.split()[:3]
                else:
                    data += [''] * 3
            else:
                data = [self.buff.split()[1], datestamp, ]
                if not dummy:
                    data.append(self.buff.split()[2])
                else:
                    data += ['']
            if not dummy:
                data.append(' '.join(self.buff.split()[3:]))
            else:
                data += ['']
            #print(data)
            dataline = ",".join(data) + '\n'
            
            ## write to datafile    
            fdat.write(dataline)
            fdat.flush()
            fdat.close()
        print("===============================")
    

    ## ----------------------------------------------------------------
    ##  Get DATA with '$TCA:LAST DATA' command
    ## ----------------------------------------------------------------
    def get_data(self):
        ##  read data from COM port
        if self.develop == False:
            self.request('$TCA:LAST DATA')
        else:
            self.buff = (b'4472971 5/19/2022 1:40:53 PM 20 60 1 2 1 0 0 0 1 Wait Sample 1432 S 1433 N n n n 16.6836 630 630 257 0 0 203 0 0 0 0 C C O O 43 27 0 0 0 0 0 0 0 0 0 0 0 0 29 29 31 0 0 40 40 51.394 99.1449 419.198 0.08593589 7.37411 0.05046773 2.43565 12.26107 12 2201 60\r\n').decode()
            #self.buff = '1602383,2018-11-16 23:59:59.073,11,20,1,2,1,4,0,0,1,Standby,866,Standby,867,N,n,n,n,16.6347,0,635,255,0,0,203,0,0,0,0,C,C,O,O,100,31,0,0,0,0,0,0,0,0,0,0,0,0,34,33,34,60,0,40,40,51.4907,99.3099,842.182,0.1488839,11.8919,0.07915366,9.36399,11.90369'
            #self.buff = "30562740,2023-03-17 21:15:53,24,0,0,0,0,0,0,0,0,Standby,8647,Standby,8646,N,n,n,n,0,0,220,0,0,0,204,0,0,0,0,C,C,O,O,31,33,0,0,0,0,0,0,0,0,0,0,0,0,28,28,30,0,0,40,40,51.4006,100.806,891.89,0.1440741,3.6613,0.02941906,-6.8021,12.28289,5,2922,59"

        ## if no response
        if not len(self.buff):
            return

        text = "-------------------\nDATA:\n" + self.buff
        print(text, sep='')
        
        if len(self.buff):
            ## reformat data to csv string
            self.buff = self.join_datetime_in_string(self.buff)
            #print(self.buff)
            self.buff = self.join_status_in_string(self.buff)
            #print(self.buff)
        else:
            text = f"Error! {self.device_name} writes empty line to data file"
            self.write_to_bot(text)
            self.print_message(text, '\n')

        ### === write to datafile
        ## Data file header
        head = "ID TimeStamp SetupID Timebase G0_Status G1_Status G2_Status G3_Status G4_Status G5_Status G6_Status Ch1_Status Ch1_SampleID Ch2_Status Ch2_SampleID MainBoardStatus Ch1BoardStatus Ch2BoardStatus SensorBoardStatus FlowS setFlowS FlowS_RAW SamplePumpSpeed FlowA setFlowA FlowA_RAW AnalyticPumpSpeed Solenoid1 Solenoid2 Solenoid5 BallValve1 BallValve2 BallValve3 BallValve4 Ch1_Temp Ch2_Temp Ch1_Voltage1 setCh1Voltage1 Ch1_Current1 Ch1_Voltage2 setCh1Voltage2 Ch1_Current2 Ch2_Voltage1 setCh2Voltage1 Ch2_Current1 Ch2_Voltage2 setCh2Voltage2 Ch2_Current2 Ch1_SafetyTemp Ch2_SafetyTemp SafetyTempInt Fan1 Fan2 Fan3 Fan4 LicorTemp LicorPressure LicorCO2 LicorCO2abs LicorH2O LicorH2Oabs LicorH2Odewpoint LicorVoltage CPU RAM CPU_TEMP"
        head = ",".join(head.split())

        ## filename
        typename = 'Data'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'
        newfile = True if not os.path.exists(filename) else False
        
        ## write to file
        fdat = open(filename, 'a')
        if newfile:
            fdat.write(head + "\n")
        fdat.write(self.buff + '\n')
        fdat.flush()
        fdat.close()
        
        ## check errors and write errors and warnings to bot
        errors = parse_data_errors(self.buff, head, self.device_name)
        if errors:
            self.write_to_bot(errors)
        ## write errors to logfile
        self.print_message(errors)
        print("===============================")


    ## ----------------------------------------------------------------
    ##  Get ONLINERESULT with '$TCA:LAST ONLINERESULT' command
    ## ----------------------------------------------------------------
    def get_online_result(self, dummy=False):
        ## Data file header
        head = "ID SampleID StartTimeUTC EndTimeUTC StartTimeLocal EndTimeLocal TCcounts TCmass TCconc AE33_BC6 AE33_ValidData AE33_b OC EC CO2 Volume Chamber SetupID a1 b1 c1 d1 e1 f1 a2 b2 c2 d2 e2 f2"

        if not dummy:        
            if self.develop == False:
                self.request('$TCA:LAST ONLINERESULT')
            else:
                ## from COM port
                self.buff = (b'1411 1432 5/19/2022 9:00:00 AM 5/19/2022 10:00:00 AM 5/19/2022 12:00:00 PM 5/19/2022 1:00:00 PM 270.84 4669.2 4722 780 100 1 3942 780 414.88 988.91 1 20 433.513965697825 -0.052493927308238 0.0000621135375773269 -0.0000019112057832946 0.0000000107468045043784 -0.0000000000160651521958029 417.003817069674 -0.00519565725647155 0.0000407358928456258 -0.00000088209278033617 0.0000000036674856614354 -0.00000000000427524100286778\r\n').decode()
                ## from docs
                #self.buff = '1,3,2018-09-05 09:20:00,2018-09-05 09:40:00,2018-09-05 11:20:00,2018-09-05 11:40:00,1618.25,18529.02,58708,0,0,1,0,0,678.83,315.61,1,4,734.11151923016,0.007605128934671236,-0.0008426029126914941,1.2467680585602101e-5,-5.7904734574089255e-8,8.278151418589865e-11,721.7721108681338,0.07058174812424729,-0.0033522482678232687,4.1361800378848836e-5,-1.7473727839550791e-7,2.3652177675724055e-10'
        else:
            self.buff = 'dummy data'

        ## if no response
        if not len(self.buff):
            return

        text = "-------------------\nONLINERESULT:\n" + self.buff
        print(text, sep='')

        ## reformat data to csv string
        if not dummy:
            self.buff = self.join_datetime_in_string(self.buff)
        else:
            datestamp = str(datetime.now() - timedelta(hours=1))[:19]
            self.buff = ",".join([''] * 2 + [datestamp] * 4 + [''] * (len(head.split()) - 6))

        #print("buff:", len(self.buff.split(',')), "head:", len(head.split()))

        ## write to datafile
        typename = 'OnLineResult'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'
        print(filename)

        newfile = True if not os.path.exists(filename) else False
        fdat = open(filename, 'a')
        if newfile:
            fdat.write(",".join(head.split()) + "\n")

        fdat.write(self.buff + '\n')
        fdat.flush()
        fdat.close()
        print("===============================") 

        ## open onlinersult file ans save it as xls
        self.save_csv_as_xls(filename)
    
    
    ## ----------------------------------------------------------------
    ##  file ans save it as xls
    ## ----------------------------------------------------------------
    def save_csv_as_xls(self, filename): 
        filenamexls = filename[:-3] + "xlsx"
        data = pd.read_csv(filename).drop_duplicates()
        
        ## reformat data columns to datetime and float format
        #data = data.apply(lambda col: 
        data.iloc[:, 2:] = data.iloc[:, 2:].apply(lambda col: 
            col.apply(pd.to_datetime) if 'time' in col.name.lower() else col.astype(float))
            #col.astype(float) if col.str.replace('.','').str.isdigit().all() else col)
        #print(data.info())
        
   
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Also set the default datetime and date formats.
        sheetname = self.timestamp
        with pd.ExcelWriter(
            filenamexls,
            engine='xlsxwriter',
            datetime_format="DD.MM.YYYY HH:MM",
            date_format="dd.mm.yyyy",
        ) as writer:
        
            data.style \
                .format(precision=3)\
                .to_excel(writer, 
                          sheet_name=sheetname, 
                          index=False,
                          float_format="%.2f", 
                          freeze_panes=(1,0)
                          )
        
            # Get the xlsxwriter workbook and worksheet objects in order
            # to set the column widths and make the dates clearer.
            workbook  = writer.book
            worksheet = writer.sheets[sheetname]

            # Set the column widths, to make the dates clearer.
            worksheet.set_column(2, 5, 20)



    ## ----------------------------------------------------------------
    ##  Get OFFLINERESULT with '$TCA:LAST OFFLINERESULT' command
    ## ----------------------------------------------------------------
    def get_offline_result(self):
        if self.develop == False:
            self.request('$TCA:LAST OFFLINERESULT')
        else:
            ## simulate data from COM port
            self.buff = (b'\r\n').decode()
            ## from docs
            self.buff = '39,695,5_arso_20170215mm,2018-01-12 12:36:19,2018-01-12 13:36:19,17520.1621,214100,189335,1.1308,0,1,25,653.0881745453704,2.070347518278751,-0.015783676941518294,5.743388472621944e-5,-9.85991925184398e-8,6.435298788574163e-11,-1921.268617466437,20.638064759183404,- Error in docs'

        ## if no response
        if not len(self.buff):
            return

        text = "-------------------\nOFFLINERESULT:\n" + self.buff
        print(text, sep='')

        ## write to datafile
        ## Data file header
        head = "ID SampleID SampleName StartTimeUTC StartTimeLocal TCcounts TCmass TCconc PunchArea DryingTime Chamber SetupID a1 b1 c1 d1 e1 f1 a2 b2 c2 d2 e2 f2"
        typename = 'OffLineData'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'

        newfile = True if not os.path.exists(filename) else False
        fdat = open(filename, 'a')
        if newfile:
            fdat.write(",".join(head.split()) + "\n")
        if len(self.buff):
            fdat.write(self.buff + '\n')
        fdat.flush()
        fdat.close()
        print("===============================")



    ## ----------------------------------------------------------------
    ##  Get SETUP with '$TCA:LAST SETUP' command
    ## ----------------------------------------------------------------
    def get_setup(self):
        if self.develop == False:
            self.request('$TCA:LAST SETUP')
        else:
            ## from COM port
            self.buff = (b'\r\n').decode()
            ## from docs
            self.buff = '1,2017-09-26 14:19:05,TCA-08-S00-00000,16.7,0.5,4.91,7.31204978640517e-5,-0.0357400687309517,10.0655216405797,9.76321196119687e-7,-4.46034050051914e-6,0.0185413211101763,11.45,11.45,1,0,1,0,60,300,3,12,57,3,495,3,12,57,3,180,265,265,220,265,265,220,100,50,100,1,25,101.325,0.1.0.0,301,1,UTC,1,0,0,0.45, string from docs'

        ## if no response
        if not len(self.buff):
            return

        text = "-------------------\nSETUP:\n" + self.buff
        print(text, sep='')

        ## write to datafile
        ## Data file header
        head = "ID TimeStamp SerialNumber SetFlowS SetFlowA Area FlowFormulaA FlowFormulaB FlowFormulaC FlowFormulaD FlowFormulaE FlowFormulaF CCch1 CCch2 SlopeTempCh1 InterceptTempCh1 SlopeTempCh2 InterceptTempCh2 SampleTime C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 P11 P12 P13 P21 P22 P23 A0 A2 A3 FlowRepStd Temp Pressure SoftwareVersion FirmwareVersion AE33_b TimeZone DST TimeProtocol BHparamID FilterIntegrity_threshold"

        #print("buff:", len(self.buff.split(',')), "head:", len(head.split()))
        typename =  'Setup'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'

        newfile = True if not os.path.exists(filename) else False
        fdat = open(filename, 'a')
        if newfile:
            fdat.write(",".join(head.split()) + "\n")

        fdat.write(self.buff.strip() + '\n')
        fdat.flush()
        fdat.close()
        print("===============================")


    ## ----------------------------------------------------------------
    ##  Get LOG with '$TCA:LAST LOG' command
    ## ----------------------------------------------------------------
    def get_log(self):
        if self.develop == False:
            self.request('$TCA:LAST LOG')
        else:
            ## from COM port
            self.buff = (b'\r\n').decode()
            ## from docs
            self.buff = '283891 5/14/2023 3:24:50 PM 1 1 Command Set Fan 1 set to 0%.'

        ## if no response
        if not len(self.buff):
            return

        text = "-------------------\nLOG:\n" + self.buff
        print(text, sep='')

        ## write to datafile
        ## Data file header
        head = "ID TimeStamp SerialNumber SetFlowS SetFlowA Area FlowFormulaA FlowFormulaB FlowFormulaC FlowFormulaD FlowFormulaE FlowFormulaF CCch1 CCch2 SlopeTempCh1 InterceptTempCh1 SlopeTempCh2 InterceptTempCh2 SampleTime C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 P11 P12 P13 P21 P22 P23 A0 A2 A3 FlowRepStd Temp Pressure SoftwareVersion FirmwareVersion AE33_b TimeZone DST TimeProtocol BHparamID FilterIntegrity_threshold"

        #print("buff:", len(self.buff.split(',')), "head:", len(head.split()))
        typename =  'Logs'
        filename = self.pathfile + self.sep + typename + self.sep
        filename += self.timestamp + "_" + typename + '.csv'

        newfile = True if not os.path.exists(filename) else False
        fdat = open(filename, 'a')
        if newfile:
            fdat.write(",".join(head.split()) + "\n")
        
        fdat.write(self.buff + '\n')
        fdat.flush()
        fdat.close()
        print("===============================")





    ## ----------------------------------------------------------------
    ##  END
    ## ----------------------------------------------------------------







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
                filename = self.pathfile +'\\wdat\\' + filename
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
