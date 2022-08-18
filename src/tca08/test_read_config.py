from TCA08_device import TCA08_device

device = TCA08_device()

device.read_path_file()
device.print_params()
device.write_path_file()

if device.connect() < 0:
    print(f"\nError with COMport opening!!!! \nPlease check {device.portName} port and try again...")
    exit()

device.get_info()
device.get_setup()
device.get_data()
device.get_ext_device_data()
device.get_online_result()
device.get_offline_result()

device.request('$TCA:END')
device.unconnect()

x = input("Press ENTER to finish...")
