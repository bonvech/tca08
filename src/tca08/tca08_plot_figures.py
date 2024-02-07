import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from   matplotlib import dates
#import datetime
from datetime import datetime
import os


############################################################################
##  Return possible datatime format
############################################################################
def get_time_format():
    ##  check if format is possible
    fmt = dates.DateFormatter('%d-%2m-%Y\n %H:%M')
    try:
        print(datetime.now().strftime(fmt))
    except:
        fmt = dates.DateFormatter('%d/%m/%Y\n %H:%M')
    return fmt


############################################################################
##  Get folder separator sign
############################################################################
def get_folder_separator():

    if 'ix' in os.name:
        sep = '/'  ## -- path separator for LINIX
    else:
        sep = '\\' ## -- path separator for Windows
    return sep


############################################################################
##  Plot params from TCA Online file
############################################################################
def plot_tca_online(data, period='day'):
    ## get data to plot
    fmt1 = '%Y-%m-%d %H:%M:%S'
    x = pd.to_datetime(data['EndTimeLocal'].astype('string'), format=fmt1)
    #print('x: ', x)
    print(data.tail())
    
    if period == 'day':
        xmin = x.max() - pd.to_timedelta("48:00:00")
    else:
        xmin = x.max() - pd.to_timedelta("336:00:00")
    data = data[pd.to_datetime(data['EndTimeLocal'], format=fmt1) > xmin]
    x = x[x > xmin]
    xlims = (x.min(), x.max() + pd.to_timedelta("2:00:00"))
    print('xmin:', xmin)


    # format graph
    plt.rcParams['xtick.labelsize'] = 10
    facecolor = 'white'
    p1color = 'yellowgreen'  #'green'
    p2color = 'dimgray'
    title = 'TCA08'

    fig = plt.figure(figsize=(10, 5))
    ax_2 = fig.add_subplot(1, 1, 1)
    
    ## plot first param
    param1 = "TCconc"
    y = data[param1].replace(0, np.nan)
    #print(y, data[param1])
    ax_2.plot(x, y, p1color, label=param1)
    ax_2.fill_between(x, y, np.zeros_like(y), color=p1color)
    ## plot second param
    param2 = "AE33_BC6"
    z = data[param2].replace(0, np.nan)
    ax_2.plot(x, z, p2color, label=param2)
    ax_2.fill_between(x, z, np.zeros_like(z), color=p2color)
    
    ## format graph
    ax_2.set_xlim(xlims)
    ax_2.set_ylim(bottom=0)
    ax_2.set_title(title, loc='right')
    ax_2.legend()

    fmt = get_time_format()
    locator = dates.AutoDateLocator(minticks=20, maxticks=30)

    ax_2.xaxis.set_major_formatter(fmt)
    ax_2.xaxis.set_minor_locator(locator)
    ax_2.grid(which='major', alpha=0.9)
    ax_2.grid(which='minor', alpha=0.5, linestyle='--')



############################################################################
##  Parse ExtDevices format data for one device 2, 3 or 18
##  @return parsed padaframe
############################################################################
def parse_device_data(datum, devnum=None):
    ## get device number from the first line of data
    if not devnum:
        devnum = datum.iloc[0, 2]  
    #print(devnum)
    ## set columns names for different devices
    if devnum == 18:  ## Meteostation
        params = ["T", "RH", "p", "DPT", "Status"]
    elif devnum == 3: ## Aethalometer AE33 + Meteostation ## p.42 DocsRus
        params = ["MetId", "BC6_AE33", "Status_AE33", "TimeBase_AE33", "T", "RH", "p", "DPT", 
                  "VingSpeed", "VingDir", "VingDirCorr", 
                  "StatusGill200", "StatusGill300", "StatusGill500"]
    elif devnum == 2: ## Aethalometer AE33
        params = ["par1", "par2", "par3"]
    else:
        print("Error! parse_dev_data: Unknown device!", devnum)
        return
    
    ## parse device data to separate columns
    for i, param in enumerate(params):
        datum.loc[:,param] = datum.loc[:, 'DeviceData'].apply(lambda x: x.split()[i])
        #datum[param] = datum['DeviceData'].apply(lambda x: x.split()[i])
    
    return datum



############################################################################
##  Plot params from TCA Online file
############################################################################
def plot_tca_pressure_and_temp(ext18, period='day'):
    ## plot Temperature and Pressure

    data = ext18[::][['TimeStamp', 'p', 'T']]
    fmt1 = '%Y-%m-%d %H:%M:%S'

    x = pd.to_datetime(data['TimeStamp'].astype(str), format=fmt1)
    if period == 'day':
        xmin = x.max() - pd.to_timedelta("48:00:00")
    else:
        xmin = x.max() - pd.to_timedelta("336:00:00")
    xlims = (xmin, x.max() + pd.to_timedelta("2:00:00"))
    print(xmin)

    data = data[pd.to_datetime(data['TimeStamp'], format=fmt1) > xmin]
    x = x[x>xmin]

    fig = plt.figure(figsize=(10, 5))
    ax_2 = fig.add_subplot(1, 1, 1)

    ## plot temperature
    param1 = "p"
    y = data[param1].astype(float)#.replace(0, np.nan)

    p_color = "black"
    line1, = ax_2.plot(x, y, '-', color=p_color)
    ax_2.tick_params(axis="y", labelcolor=p_color)
    #ax_2.set_ylabel('Pressure, hpa', color=p_color)
    label1 = 'Pressure'


    ## plot pressure
    param2 = "T"
    z = data[param2].astype(float)

    t_color = "blue" #"crimson" #"tab:orange"
    ax = ax_2.twinx()
    line2, = ax.plot(x, z, '--', color=t_color)
    ax.tick_params(axis="y", labelcolor=t_color)
    #ax.set_ylabel('Temperature, C', color=t_color)
    label2 = 'Temperature'

    ## легенда
    ax_2.legend((line1, line2), (label1,label2), borderaxespad=0.1)

    ## # format graph
    plt.rcParams['xtick.labelsize'] = 10
    ax_2.set_xlim(xlims)
    ax_2.set_ylim(min(y) - 0.2 * (max(y) - min(y)))  ## отступить снизу 20% диапазона
    ax_2.set_title('TCA08', loc='right')
    
    fmt = get_time_format()
    locator = dates.AutoDateLocator(minticks=20, maxticks=30)

    ax_2.xaxis.set_major_formatter(fmt)
    ax_2.xaxis.set_minor_locator(locator)
    ax_2.grid(which='major', alpha=0.9)
    ax_2.grid(which='minor', alpha=0.5, linestyle='--')

    

### ------------------------------------------------------------------------
if __name__ == "__main__":
    sep = get_folder_separator()
    
    ## files to read
    #timestamp = '2022-08'
    timestamp = str(datetime.now())[:7]
    print("timestamp:", timestamp)
    datadirname     = ".." + sep + ".." + sep + "data"    + sep
    path_to_figures = ".." + sep + ".." + sep + "figures" + sep
    print(datadirname, path_to_figures, sep='\n')
    ## check path to figures
    if not os.path.exists(path_to_figures):   
        os.system("mkdir " + path_to_figures)


    ## ========================
    ## read OnlineData
    filetype = 'OnlineResult'
    dirname = datadirname + filetype + sep
    csvfilename = dirname + timestamp + "_" + filetype + ".csv"   #-22_13-52.csv"

    if not os.path.exists(datadirname):   
        print(datadirname, "not exists")
    if not os.path.exists(dirname):   
        print(dirname, "not exists")
    if not os.path.exists(csvfilename):   
        print(csvfilename, "not exists")

    datum = pd.read_csv(csvfilename)
    #print(datum)

    ## plot OnlineData day
    plot_tca_online(datum)
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_day.svg', facecolor='white', bbox_inches='tight') 
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_day.png', facecolor='white', bbox_inches='tight') 
    print("Online 2day done")

    ## plot OnlineData week
    plot_tca_online(datum, 'week')
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_week.svg', facecolor='white', bbox_inches='tight') 
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_week.png', facecolor='white', bbox_inches='tight') 
    print("Online twoweeks done")


    ## ========================
    ## read ExtDeviceData datafile
    filetype = 'ExtDeviceData'
    dirname = datadirname + filetype + sep
    #filename = dirname + timestamp + "_" + filetype + ".txt"
    filename = dirname + timestamp + "_" + filetype + ".csv"
    ext = pd.read_csv(filename)
    ext18 = parse_device_data(ext[ext["DeviceID"] == 18][:], 18)
    #print(ext18)

    ## plot ExtDeviceData day
    plot_tca_pressure_and_temp(ext18)
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_day.svg', facecolor='white', bbox_inches='tight') 
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_day.png', facecolor='white', bbox_inches='tight') 
    
    ## plot ExtDeviceData week
    plot_tca_pressure_and_temp(ext18, 'week')
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_week.svg', facecolor='white', bbox_inches='tight') 
    plt.savefig(path_to_figures + 'tca_' + filetype.lower() + '_week.png', facecolor='white', bbox_inches='tight') 
    
    #x = input("Press Enter")