# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 13:11:19 2021

@author: Angus Khaw
"""

from tkinter import *
import time
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.animation as animation 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from datetime import datetime
import csv

# datetime object containing current date and time
now = datetime.now()
dtString = now.strftime("%d%m%Y %H%M%S")
pathString = "./" + "SensorData" + dtString + ".csv"

ports = list(serial.tools.list_ports.comports())
for p in ports:
    if 'Arduino' in p[1]:
        port = p[0]
        
print(port)
arduinoData = serial.Serial(port, 9600)

def request():
    arduinoData.write("Get list".encode())
    listStr = arduinoData.readline()
    signals = listStr.decode().split(',')
    signals[-1] = signals[-1].replace('\r\n','')
    return signals

x = request()

window = Tk()
window.geometry('600x600')

plt.rcParams["figure.figsize"] = (5,5)

# Choosing selectmode as multiple 
# for selecting multiple options
lstbox = Listbox(window, selectmode = "multiple")
  
# Widget expands horizontally and
# vertically by assigning both to 
# fill option
lstbox.pack(expand = YES, fill = "both")
  
# Taking a list 'x' with the items 
# as languages
  
for each_item in range(len(x)):
      
    lstbox.insert(END, x[each_item])
      
    # coloring alternative lines of listbox
    lstbox.itemconfig(each_item,
             bg = "yellow" if each_item % 2 == 0 else "cyan")

def select():
    selected = lstbox.curselection()
    global signalList, signalIdx
    signalList = []
    signalIdx = []
    for i in selected:
        signal = lstbox.get(i)
        signalList.append(signal)
        signalIdx.append(i)
    arduinoData.write("Start plotting".encode())
    plot()
    lstbox.destroy()
    plot_button.destroy()

plot_button = Button(master = window, 
                     command = select,
                     height = 2, 
                     width = 10,
                     text = "Plot & Record")
  
# place the button 
# in main window
plot_button.pack()

xs = []
ys = []
line = []
serialData = []
xAxisLowerLim = 0
xAxisLength = 5

def record(row):
    with open(pathString, 'a', newline = '') as f:
        # create the csv writer
        writer = csv.writer(f)

        # write a row to the csv file
        writer.writerow(row)

def plot():
    global numOfPlots
    numOfPlots = len(signalList)
    header = []
    for i in range(0, numOfPlots):
        if signalList[i] == "IMU":
            header += ["Time"] + ["IMU (g)"]
        else:
            header += ["Time"] + [signalList[i] + " (V)"]
    if not not len(signalList):
        record(header)
    global fig, ax
    fig, ax = plt.subplots(numOfPlots, 1)
    plt.subplots_adjust(hspace=0.5)
    fig.supxlabel('Time (s)')
    if numOfPlots == 1:
        ax = [ax]
    for i in range(0,numOfPlots):
        xs.append([])
        ys.append([])
        li, = ax[i].plot([],[])
        line.append(li)
        if signalList[i] == "IMU":
            ax[i].set_ylim(0,4.5)
            ax[i].set_ylabel("RMS acceleration (g)")
        else:
            ax[i].set_ylim(0,3.5)
            ax[i].set_ylabel("Voltage (V)")
        ax[i].grid(True)
        ax[i].title.set_text(signalList[i])
    global canvas
    plt.figure(figsize=(10, 6), dpi=80)
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().pack()
    global ani
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1, blit=True)
    
def animate(i, xs, ys):
    arduinoString = arduinoData.readline() #read the line of text from the serial port
    print(arduinoString)
    serialData = arduinoString.decode().split(',')
    for i in range(0,len(serialData)):
        serialData[i] = float(serialData[i])
    # Add x and y to lists
    # Append xs data
    for i in range(0,numOfPlots):
        currTime = serialData[0+2*i]/1000000
        if signalList[i] == "IMU":
            currData = serialData[1+2*i]/1000
        else:
            currData = serialData[1+2*i]/1023*3.3
        xs[i].append(currTime)
        ys[i].append(currData)
        line[i].set_data(xs[i], ys[i])
        if len(xs[0]) == 1:
            ax[i].set_xlim(xs[0][0], xs[0][0 ] + 8)
    record(serialData)
    if len(xs[0]) == 500:
        for i in range(0,numOfPlots):
            ax[i].set_xlim(xs[0][-1], xs[0][-1] + 8)
            xs[i] = [] + [xs[i][-1]]
            ys[i] = [] + [ys[i][-1]]
        fig.canvas.draw()
    return line

# placing the canvas on the Tkinter window

window.mainloop()

