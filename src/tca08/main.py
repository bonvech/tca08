

from TCA08_device import TCA08_device
#import socket
#import sys
#import socket
import time
#import os




##portx=“COM5”
##bps=9600
##timex=5
### Последовательный порт выполняется до тех пор, пока он не будет открыт, а затем использование команды open сообщит об ошибке
##ser = serial.Serial(portx, int(bps), timeout=1, parity=serial.PARITY_NONE,stopbits=1)
##if (ser.isOpen()):
##print(“open success”)
### Некоторые данные в строке порта должны быть декодированы
##ser.write(“hello”.encode())
##while (True):
##line = ser.readline()
##if(line):
##print(line)
##line=0
##else:
##print(“open failed”)
##ser.close () # Закройте порт
##


device = TCA08_device()

device.read_path_file()
device.print_params()

device.MAXID = device.MINID
print(device.MAXID)

print(device.MINID)
device.MINID = device.MINID+10
print(device.MINID)

device.write_path_file()

##device.connect()
##device.request('$TCA:INFO',0,0)
##
##device.request('$TCA:LAST DATABASEVER',0,0)
##device.request('$TCA:LAST ONLINERESULT',0,0)
##device.request('$TCA:LAST OFFLINERESULT',0,0)
##
##device.request('$TCA:LAST FILTERINTEGRITY',0,0)
##device.request('$TCA:LAST LOG',0,0)
##
##device.request('$TCA:STREAM 0',4471672,4471676)
##
##device.request('$TCA:LAST DATA',0,0)
##
##device.request('$TCA:LAST EXTDEVICEDATA',0,0)
##
##
##time.sleep(1)
##device.request('$TCA:END',0,0)
##device.unconnect()


print("QQ")
#x = input()








###device.request('?',0,0)  #- не работает
##device.request('MAXID DATA',0,0)  #- не работает
###x = input()
##
##delay = 100
##start = device.MAXID - delay
##fin = device.MAXID
##
###device.request('FETCH DATA',start,fin)  #-  не работает, перевести байты в стринги
##
##device.request('$AE33:D'+str(delay),0,0)  #-  то же самое
##
###device.request('$AE33:W'+str(delay),0,0)  #-  то же самое
##
##device.request('CLOSE',0,0)
##device.unconnect()
##
##device.plot_from_excel_file(device.xlsfilename)
##device.write_path_file()
##
