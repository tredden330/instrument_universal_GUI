import dearpygui.dearpygui as dpg
import serial
from serial.tools import list_ports
import math
import threading
import time

dpg.create_context()

width = 1000
height = 800

def port_selected(sender, data):
    #retrieve port name
    for port in ports:
        if str(port) == data:
            portName = port.name

    dpg.delete_item("info_text")
    info_text = dpg.add_text('Querying port...', before='scan_combo', tag='info_text')

    #request the device to identify itself
    id = '?'
    ser = serial.Serial(
        port=portName,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1)

    data = bytes(124) #send a random message to notify the esp32
    ser.write(data)
    id = ser.readline() #the esp32 should send back in id message

    id = str(id)
    print('end of connection with: ', id)
    #select how to proceed based on the machine
    if "pH Meter" in id:

        dpg.delete_item("info_text")
        info_text = dpg.add_text('pH Meter detected! calibrate...', before='scan_combo', tag='info_text')
        dpg.delete_item("scan_combo")

        print(portName)

        #plot the values
        sindatax = [1,2,3,4,5]
        sindatay = [10,10,20,-10,20]

        with dpg.plot(label="Line Series", height=700, width=700, parent='main_window', tag='main_plot'):

            dpg.add_plot_axis(dpg.mvXAxis, label="sample #", tag="x_axis")
            dpg.add_plot_axis(dpg.mvYAxis, label="12-bit ADC Value", tag="y_axis")

            dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)", parent="y_axis", tag="series_tag")


        #this should be spun off into a thread so that the gui can continue to be interactable and stop it eventually
        data = []
        dataIndicies = []
        dataIndex = 0
        global stopThread
        stopThread = False

        def updatePlot(data, dataIndicies, dataIndex):
            global stopThread
            while not stopThread:
                data_raw = ser.readline().decode().strip()
                if data_raw:
                    data.append(int(data_raw))
                    dataIndicies.append(dataIndex)
                    dataIndex += 1
                    dpg.set_value('series_tag', [dataIndicies, data])
                    dpg.fit_axis_data('x_axis')
                    dpg.fit_axis_data('y_axis')
                else:
                    print('empty data')
                print('thread says: ', stopThread)

        print('begin threading...')
        t = threading.Thread(target=updatePlot, args=(data, dataIndicies, dataIndex))  #create a thread to plot data
        t.start()

        def stop():
            global stopThread
            stopThread = True
            t.join()

        dpg.add_button(label="end collection", callback=stop, tag='end', before='main_plot')
        #time.sleep(5)
        #stopThread = True
        #t.join()
        #stop()

        print('end of sleep')



def scan_ports():
    global ports
    ports = list_ports.comports()

    portCombo = dpg.add_combo(items=ports, before='scan_button', callback=port_selected, tag='scan_combo')
    info_text = dpg.add_text('Select a port...', before='scan_combo', tag='info_text')
    dpg.delete_item("scan_button") #remove the scan port delete_button



with dpg.window(label="Serial Connections", width=width, height=height, tag='main_window'):
    #create a button that lists the available serial ports
    dpg.add_button(label="Scan USB ports", callback=scan_ports, tag='scan_button')

dpg.create_viewport(title='Thomas\' Multi-Instrument GUI', width=width, height=height)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
