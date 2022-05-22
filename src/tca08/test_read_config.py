from TCA08_device import TCA08_device

device = TCA08_device()

device.read_path_file()
device.print_params()
device.write_path_file()

device.get_info()
device.get_ext_device_data()
device.get_data()
device.get_online_result()
