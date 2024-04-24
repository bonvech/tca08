from tca08_device import TCA08_device
#import time

device = TCA08_device()

device.read_path_file()
device.print_params()
device.write_path_file()

if device.connect() < 0:
    print(f"\nError with COMport opening!!!! \nPlease check {device.portName} port and try again...")
    device.get_ext_device_data(dummy=True)
    device.get_online_result(dummy=True)
    exit()

device.get_info()
device.get_setup()
device.get_log()
device.get_data()
device.get_ext_device_data()
device.get_online_result()
device.get_offline_result()

device.request('$TCA:END')
device.unconnect()

## pause for write files
#time.sleep(5)

#x = input("Press ENTER to finish...")
