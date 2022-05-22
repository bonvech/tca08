import sys
import socket
import time
import datetime
from datetime import datetime
#import pandas as pd
import os
import serial


class TCA08_device:
    def __init__(self):
        self.MINID = 0
        self.MAXID = 0

        ## for data files
        self.yy = '0'        ##  year for filename of raw file
        self.mm = '0'        ## month for filename of raw file
        self.yy_D = '0'      ##  year for filename of D-file
        self.mm_D = '0'      ## month for filename of D-file 
        self.pathfile = ''   ## work directory name
        self.xlsfilename = ''      ## exl file name
        self.file_raw = None       ## file for raw data
        self.file_format_D = None  ## file for raw data
        self.file_header = ''

        self.buff = ''
        self.info = ''
        self.portName = ''
        self.BPS = 115200
        self.PARITY = serial.PARITY_NONE
        self.STOPBITS = serial.STOPBITS_ONE
        self.BYTESIZE = serial.EIGHTBITS
        self.TIMEX = 1

        self.fill_header()


    def fill_header(self):
        self.file_header = ""


    def read_path_file_0(self):
        # check file
        #print("read file")
        try:
            f = open("PATHFILES.CNF")
        except:
            print("Error!! No file PATHFILES.CNF\n\n")
            return -1

        params = [x.replace('\n','') for x in f.readlines() if x[0] != '#']
        f.close()
        #print(params)

        for param in params:
            if "COM" in param:
                self.portName = (param.split('=')[1])
##            elif "BPS" in param:
##                self.BPS = int(param.split('=')[1])
##            elif "STOPBITS" in param:
##                self.STOPBITS   = int(param.split('=')[1])
##            elif "PARITY" in param:
##                parity   = int(param.split('=')[1])
##                if parity:
##                    self.PARITY = serial.PARITY_EVEN
##                else:
##                    self.PARITY = serial.PARITY_NONE
##            elif "TIMEX" in param:
##                self.TIMEX   = int(param.split('=')[1])
            elif "MINID" in param:
                self.MINID = int(param.split('=')[1])
                self.MAXID = self.MINID
            else:
                self.pathfile = param
                os.system("mkdir " + param)
                path = self.pathfile + '\\Data\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\OffLineData\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\OnLineData\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\Logs\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\\table\\'
                os.system("mkdir " + path)
    #    # \todo ПОПРАВИТЬ в конфигурацилонном файле СЛЕШИ В ИМЕНИ ДИРЕКТОРИИ  !!!   для ВИНДА


    def read_path_file(self):
        import PATHFILES
        # check file
        #print("read file")
        try:
            f = open("PATHFILES.CNF")
        except:
            print("Error!! No file PATHFILES.CNF\n\n")
            return -1

        params = [x.replace('\n','') for x in f.readlines() if x[0] != '#']
        f.close()
        #print(params)

        for param in params:
            if "COM" in param:
                self.portName = (param.split('=')[1])
##            elif "BPS" in param:
##                self.BPS = int(param.split('=')[1])
##            elif "STOPBITS" in param:
##                self.STOPBITS   = int(param.split('=')[1])
##            elif "PARITY" in param:
##                parity   = int(param.split('=')[1])
##                if parity:
##                    self.PARITY = serial.PARITY_EVEN
##                else:
##                    self.PARITY = serial.PARITY_NONE
##            elif "TIMEX" in param:
##                self.TIMEX   = int(param.split('=')[1])
            elif "MINID" in param:
                self.MINID = int(param.split('=')[1])
                self.MAXID = self.MINID
            else:
                self.pathfile = param
                os.system("mkdir " + param)
                path = self.pathfile + '\\Data\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\OffLineData\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\OnLineData\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\Logs\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\\table\\'
                os.system("mkdir " + path)
    #    # \todo ПОПРАВИТЬ в конфигурацилонном файле СЛЕШИ В ИМЕНИ ДИРЕКТОРИИ  !!!   для ВИНДА


    def write_path_file(self):
        f = open("PATHFILES.CNF.bak", 'w')
        f.write("#\n")
        f.write("# Directorry for DATA:\n")
        f.write("#\n")
        f.write(self.pathfile+"\n")
        f.write("#\n")
        f.write("#\n")
        f.write("# TCA08:   Serial Port:\n")
        f.write("#\n")
        f.write("COM="+self.portName+"\n")
        f.write("#\n")
        f.write("#\n")
##        f.write("BPS=115200\n")
##        f.write("#\n")
##        f.write("STOPBIT=1\n")
##        f.write("#\n")
##        f.write("PARITY=0\n")
##        f.write("#\n")
##        f.write("TIMEX=5\n")
##        f.write("#\n")
        f.write("# TCA08:  Last Records:\n")
        f.write("#\n")
        f.write("MINID="+str(self.MINID)+"\n")
        f.write("#\n")
        f.close()


    def print_params(self):
        print("Directory for DATA:   ",self.pathfile)
        print("portName = ", self.portName)
        print("BPS = ", self.BPS)
        print("STOBITS = ", self.STOPBITS)
        print("PARITY = ", self.PARITY)
        print("BYTESIZE = ",self.BYTESIZE)
        print("TIMEX = ", self.TIMEX)
        print("MINID = ", self.MINID)

    def connect(self):
# Последовательный порт выполняется до тех пор, пока он не будет открыт, а затем использование команды open сообщит об ошибке
##        self.ser = serial.Serial(
##                port=self.COM,
##                baudrate=self.BPS,
##                timeout=1,
##                parity=self.PARITY,
##                stopbits=self.STOPBIT
##                )

        self.ser = serial.Serial(
                port=self.portName,
                baudrate=self.BPS,
                parity=self.PARITY,
                stopbits=self.STOPBITS,
                bytesize=self.BYTESIZE
                )

##        self.ser = serial.Serial(
##                port=self.portName,
##                baudrate=115200,
##                parity=serial.PARITY_NONE,
##                stopbits=serial.STOPBITS_ONE,
##                bytesize=serial.EIGHTBITS
##                )


        if (self.ser.isOpen()):
            print("open success\n")
        else:
            print("open failed\n")
        



    def unconnect(self):
        self.ser.close() # Закройте порт


    def request(self,command,start,stop):
        f =open("data.dat", 'a') 

        if command == '$TCA:STREAM 0':
            command += ' ' + str(start) + ' ' + str(stop)
        command += '\r\n'
        print(command)
        f.write(str(command))

        self.ser.write(command.encode())
        time.sleep(1)

        while self.ser.in_waiting:
            line = str(self.ser.readline())
            if (line):
                print("{{"+line+"}}")
                f.write("{{"+str(line)+"}}\n")
                line=0
            else:
                print("open failed\n")
                break
        f.write("\n")       
        f.close()

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
##
##        ##### excel file #####                
##        xlsfilename = yy + '_TCA-S08-01006.xlsx'
##        xlsfilename = self.pathfile + 'tableW/' + xlsfilename
##        self.xlsfilename = xlsfilename
##        ## read or cleate datafame
##        xlsdata = self.read_dataframe_from_excel_file(xlsfilename)
##        print(xlsdata.head())
##        if xlsdata.shape[0]:
##            dropset = ['Date', 'Time (Moscow)']
##            xlsdata = xlsdata.append(dataframe_from_buffer, ignore_index=True).drop_duplicates(subset=dropset, keep='last')
##            #print("Append:", xlsdata)
##            xlsdata.set_index('Date').to_excel(xlsfilename, engine='openpyxl')
##        else:
##            print("New data:")
##            dataframe_from_buffer.set_index('Date').to_excel(xlsfilename, engine='openpyxl')
##            #dataframe_from_buffer.to_excel(xlsfilename, engine='openpyxl')

    def parse_format_D_data(self):
        ## main
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
                filename = '_'.join((yy, mm)) + '_TCA-S08-01006.ddat'
                filename = self.pathfile +'\ddat\\' + filename
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
            

        ## ##### write dataframe to excel file
        ## make dataFrame from list
        excel_columns = ['Date', 'Time (Moscow)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6',
            'BC7', 'BB(%)', 'BCbb', 'BCff', 'Date.1', 'Time (Moscow).1']
        dataframe_from_buffer = pd.DataFrame(rows_list, columns=excel_columns[:-4])
        ## add columns
        dataframe_from_buffer['BCbb'] = dataframe_from_buffer['BB(%)'].astype(float) * dataframe_from_buffer['BC5'].astype(float) / 100
        dataframe_from_buffer['BCff'] = (100 - dataframe_from_buffer['BB(%)'].astype(float)) / 100 *  dataframe_from_buffer['BC5'].astype(float)
        dataframe_from_buffer['Date.1'] = dataframe_from_buffer['Date']
        dataframe_from_buffer['Time (Moscow).1'] = dataframe_from_buffer['Time (Moscow)']
        print(dataframe_from_buffer.head())

        ##### excel file #####                
        xlsfilename = yy + '_TCA-S08-01006.xlsx'
        xlsfilename = self.pathfile + 'table/' + xlsfilename
        self.xlsfilename = xlsfilename
        ## read or cleate datafame
        xlsdata = self.read_dataframe_from_excel_file(xlsfilename)
        print(xlsdata.head())
        if xlsdata.shape[0]:
            dropset = ['Date', 'Time (Moscow)']
            xlsdata = xlsdata.append(dataframe_from_buffer, ignore_index=True).drop_duplicates(subset=dropset, keep='last')
            #print("Append:", xlsdata)
            xlsdata.set_index('Date').to_excel(xlsfilename, engine='openpyxl')
        else:
            print("New data:")
            dataframe_from_buffer.set_index('Date').to_excel(xlsfilename, engine='openpyxl')
            #dataframe_from_buffer.to_excel(xlsfilename, engine='openpyxl')


    def read_dataframe_from_excel_file(self, xlsfilename):
        columns = ['Date', 'Time (Moscow)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6',
            'BC7', 'BB(%)', 'BCbb', 'BCff', 'Date.1', 'Time (Moscow).1']
        try:
            ## read excel file to dataframe
            ## need to make "pip install openpyxl==3.0.9" if there are problems with excel file reading
            datum = pd.read_excel(xlsfilename)
            print(xlsfilename, "read")
        except:
            # create excel 
            datum = pd.DataFrame(columns=columns)
            print("No file", xlsfilename)
            
        return datum


    def plot_from_excel_file(self, xlsfilename):
        try:
            ## read excel file to dataframe
            ## need to make "pip install openpyxl==3.0.9" if there are problems with excel file reading
            datum = pd.read_excel(xlsfilename)
        except:
            print("Error! No excel data file:", xlsfilename)
            return

        fig = plt.figure(figsize=(14, 5))
        plt.plot(datum["BCff"][-2880:], 'k', label='BCff')
        plt.plot(datum["BCbb"][-2880:], 'orange', label='BCbb')
        plt.legend()
        plt.grid()
        plt.savefig('Moscow_bb.png', bbox_inches='tight')
