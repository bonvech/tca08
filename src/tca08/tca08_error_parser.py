import telebot
import config

## get errors from G3_Status or G4_Status
def get_g34_errors(g3, g=3):
    if g not in [3, 4]:
        print("Invalid status number: not 3 or 4")
        return ''
    errors = ''
    if g3 & 1:
        errors += f"Error G{g}(1). Прерывание напряжения: Превышение времени ожидания по напряжению: источник напряжения для одного из модулей нагрева в камере 1 или камере 2 был включен дольше, чем значение ограничения по времени. Анализатор остановит измерения, перезагрузится и попытается продолжить измерения. Если эта ошибка произойдет 3 раза, анализатор не станет продолжать измерения (G0=64, безопасная остановка).\n"  
    if g3 & 2:
        errors += f"Warning G{g}(2). Предупреждение об утечке: ТСА детектирует утечку в камере 1 или 2 с помощью теста на утечку (см. главу 9.2 «Тест на утечку»). Проверьте камеры и повторите тест на утечку снова.\n"
    if g3 & 4:
        errors += f"Warning G{g}(4). Сбой целостности фильтра: TCA обнаруживает, что один из фильтров в камере 1 или 2 может быть поврежден. Остановите измерения и замените поврежденный фильтр (См. главу 9.1). Дополнительно всплывающее окно WARNING показывается на экране для статуса целостности фильтра.\n"
    if g3 & 8:
        errors += f"Error G{g}(8). Ошибка подогревателя: Анализатор обнаружил, что нагревающая нить в одном из модулей нагрева в камере 1 или камере 2 оборвана или имеет плохой контакт с штырьком блока питания. Анализатор прекратит измерения и запустит статус G0=64, безопасная остановка.\n"
    if g3 & 16:
        errors += f"Error G{g}(16). Превышение по току: Измеренный ток в одном из модулей нагрева в камере 1 или камере 2 выше, чем предельное значение по току. Анализатор остановит измерения, перезагрузится и попытается продолжить измерения. Если эта ошибка произойдет 3 раза, анализатор не станет продолжать измерения (G0=64, безопасная остановка).\n" 
    if g3 & 32:
        errors += f"Error G{g}(32). Ошибка установки напряжения: Установленное значение напряжения для одного из модулей нагрева в камере 1 или камере 2 выше, чем предельное значение напряжения. Анализатор остановит измерения, перезагрузится и попытается продолжить измерения. Если эта ошибка произойдет 3 раза, анализатор не станет продолжать измерения (G0=64, безопасная остановка).\n"
    if g3 & 64:
        errors += f"Error G{g}(64). Не подключен датчик температуры: Сбой термопары сенсора температуры: сенсор в камере 1 или камере 2 не подключен или сломан. Анализатор остановит измерения, перезагрузится и попытается продолжить измерения. Если эта ошибка произойдет 3 раза, анализатор не станет продолжать измерения (G0=64, безопасная остановка).\n"
    if g3 & 128:
        errors += f"Error G{g}(128). Ошибка шарового клапана: Один из шаровых клапанов в пробоотборных каналах 1 или 2 сообщил об ошибке. Анализатор остановит измерения, перезагрузится и попытается продолжить измерения. Если эта ошибка произойдет 3 раза, анализатор не станет продолжать измерения (G0=64, безопасная остановка).\n"
    return errors


## get status from G1_Status or G2_Status
def get_g12_errors(g1, g=1):
    if g not in [1, 2]:
        print("Invalid status number: not 1 or 2")
        return ''
    errors = ''
    if g1 & 4:
        errors += f"Message G{g}(4). Чистка.\n"
    if g1 & 8:
        errors += f"Message G{g}(8). Проверка утечки.\n"   
    if g1 & 16:
        errors += f"Message G{g}(16). Проверка Денудера.\n"
    if g1 & 32:
        errors += f"Message G{g}(32). Zero.\n"
    if g1 & 64:
        errors += f"Message G{g}(64). Проверка температуры.\n"
    return errors
        

def parse_data_errors(buff, head, devicename):
    #print(head)
    #print(buff)
    data = {x: y for x, y in zip(head.split(','), buff.split(','))}
    errors = ''
    #print(data)
    
    ##
    if data["Ch1_Status"] == 'Standby' and data["Ch2_Status"] == 'Standby' and data['Timebase']=='0':
        errors += "Error. Прибор не работает. Находится в режиме ожидания.\n"

    g0 = int(data["G0_Status"])
    if g0 > 0:
        if g0 & 4:
           errors += "Message G0(4). Калибровка.\n"
        if g0 & 8:
           errors += "Message G0(8). Верификация.\n"
        if g0 & 16:
           errors += "Error G0(16). Смените кварц.\n"
        if g0 & 32:
           errors += "Message G0(32). Инициализация дежурного режима.\n" 
        if g0 & 64:
           errors += "Error G0(64). Безопасная остановка.\n" 
        if g0 & 128:
           errors += "Error G0(128). Критическая остановка.\n"

    g1 = int(data["G1_Status"])
    if g1 > 2:
        errors += get_g12_errors(g1, 1)

    g2 = int(data["G2_Status"])
    if g2 > 2:
        errors += get_g12_errors(g2, 2)       

    g3 = int(data["G3_Status"])
    if g3 > 0:
        errors += get_g34_errors(g3, 3)

    g4 = int(data["G4_Status"])
    if g4 > 0:
        errors += get_g34_errors(g4, 4)

    g5 = int(data["G5_Status"])    
    if g5 > 0:
        if g5 & 1:
            errors += "Warning G5(1). Дверца TCA открыта.\n" 
        if g5 & 2:
            errors += "Warning G5(2). Поток для анализа: Усредненный поток для анализа был ниже, чем установленный предел потока при последнем анализе. Убедитесь, что трубка входа воздуха на анализ не заблокирована.\n"  
        if g5 & 4:
            errors += "Warning G5(4). Поток пробы: Усредненный поток пробы был ниже, чем установленный предел потока при последнем пробоотборе. Убедитесь, что трубка входа воздуха пробы не заблокирована.\n"            
        if g5 & 8:
            errors += "Warning G5(8). Вентилятор охлаждения: Охлаждающий вентилятор одной из камер не работает. Проверьте вентилятор на блокировку или отсоединении.\n"   
        if g5 & 16:
            errors += "Error G5(16). Ошибка CO2: Значения от сенсора CO2 в ppm превысили рабочий диапазон. Сенсор СО2 нуждается в обслуживании.\n"              
        if g5 & 32:
            errors += "Error G5(32). Ошибка во внутренней коммуникации: Анализатор переключится на статус G0=64, безопасная остановка.\n" 

    g6 = int(data["G6_Status"])    
    if g6 > 0:
        if g6 & 1:
            errors += "Message G6(1). Сеть обнаружена.\n"
        if g6 & 2:
            errors += "Error G6(2). База данных: Карта памяти CF отсутствует.\n" 
        if g6 & 4:
            errors += "Error G6(4). Установка: Одно из значений в таблице установок вышло за пределы. Анализатор включит статус  G0=64, безопасная остановка.\n"
        if g6 & 8:
            errors += "Warning G6(8). Внешнее устройство: (1) Внешнее устройство подключено, но отсутствует передача данных или данные внешнего устройства вышли за пределы. (2) AE33 подключен, но стандарт отчета по потоку в АЕ33 отличается от стандарта отчета по потоку в ТСА08.\n" 
        if g6 & 16:
            errors += "Warning G6(16). Память: Число рядов данных достигает предела внутренней памяти. Удалите более старые ряды данных, используя команды в меню памяти. Мы рекомендуем резервное копирование базы данных перед удалением рядов.\n"     
    
    ## send errors to bot
    nmax = 4096 ## максимальная длина сообщения в телеграме
    if len(errors):
        #errors = "TCA-08-S02-00209 сообщает:\n" + errors
        errors = f"{devicename} сообщает:\n" + errors
        
        ## send to bot
        bot = telebot.TeleBot(config.token, parse_mode=None)
        for n in range((len(errors) + nmax)// nmax):
            bot.send_message(config.channel, errors[nmax*n: nmax * (n+1)])
    else:
        errors = "No errors in data."
    
    return errors



if __name__ == "__main__":
    head = "ID TimeStamp SetupID Timebase G0_Status G1_Status G2_Status G3_Status G4_Status G5_Status G6_Status Ch1_Status Ch1_SampleID Ch2_Status Ch2_SampleID MainBoardStatus Ch1BoardStatus Ch2BoardStatus SensorBoardStatus FlowS setFlowS FlowS_RAW SamplePumpSpeed FlowA setFlowA FlowA_RAW AnalyticPumpSpeed Solenoid1 Solenoid2 Solenoid5 BallValve1 BallValve2 BallValve3 BallValve4 Ch1_Temp Ch2_Temp Ch1_Voltage1 setCh1Voltage1 Ch1_Current1 Ch1_Voltage2 setCh1Voltage2 Ch1_Current2 Ch2_Voltage1 setCh2Voltage1 Ch2_Current1 Ch2_Voltage2 setCh2Voltage2 Ch2_Current2 Ch1_SafetyTemp Ch2_SafetyTemp SafetyTempInt Fan1 Fan2 Fan3 Fan4 LicorTemp LicorPressure LicorCO2 LicorCO2abs LicorH2O LicorH2Oabs LicorH2Odewpoint LicorVoltage CPU RAM CPU_TEMP"
    head = ",".join(head.split())

    buff = "30562740,2023-03-17 21:15:53,24,0,0,0,0,0,0,0,0,Standby,8647,Standby,8646,N,n,n,n,0,0,220,0,0,0,204,0,0,0,0,C,C,O,O,31,33,0,0,0,0,0,0,0,0,0,0,0,0,28,28,30,0,0,40,40,51.4006,100.806,891.89,0.1440741,3.6613,0.02941906,-6.8021,12.28289,5,2922,59"
    parse_data_errors(buff, head)
