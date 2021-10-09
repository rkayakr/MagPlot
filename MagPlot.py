#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plots PSWS magnetometer data from runmag.log
plots either plain text or json format files

windows version hardcoded homepath directory location
expects filename with callsign to process 
expects magnetometer data files in homepath/logs
leaves plots in homepath/Mplot

for Pi comment out windows homepath and uncomment Pi  lines
leaves plots in homepath/Mplot

uses modified WWV_utility2.py now called Mag_utility
Bob Benedict, KD8CGH, 10/02/2021

create text file "files.txt" in homepath directory
  filetype (json or plain)
  plot (all, abs, rel, tot, rlt, total)
  time (all, start and finsh in hours:min:sec)
  filename 
  ...

loads file name
plots absolute, relative, total (if available) and temperature plots
magnetometer results are filtered before plotting
plot appearnce parameters at line 53 including filter parameters

uses modified WWV_utility2.py 
20 February 2020
WWV utility file
Routines and classes used in WWV file management and graphing
David Kazdan, AD8Y
John Gibbons, N8OBJ - mods to plot header 2/3/20

"""
#import os # uncomment for pi
from os import path
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import ticker
from scipy.signal import filtfilt, butter
import datetime  
from Mag_utility import time_string_to_decimals
import json
#import re

# plot appearance parameters
M = 8  # number of plot y ticks
lw=0.6  # plot line width
pdpi=250 # final plot image dpi
fsize='10' # font size
# lowpass butterworth filter parameters
FILTERBREAK=0.1 # filter breakpoint in Nyquist rates. N. rate here is 1/sec, 0.005 used in Grape 1 doppler so is in Hz. 
FILTERORDER=6   # 6

# Pi , comment out for windows
'''
homepath = '/home/pi'
homepath = homepath + "/rm3100-runMag/"
DATADIR = homepath + 'logs/'   # Pi
'''
#comment out windows homepath and data dir for Pi
homepath = "E:\\Documents\\PSWS\\magnetometer\\"  # set your windows path, comment out for Pi
DATADIR = homepath + 'logs/'
#

names = open(homepath+"files.txt","r")

FileType = names.readline() # what format will the data be in?
if FileType[0:4] == 'json':
    isjson=True
    print('json file \n')
else:
    isjson=False
    print('plain text file \n')

# flags for what to plot
Rel=False
Abs=False
Rlt=False
Tot=False
Xo=Yo=Zo=False
Rx=Ry=Rz=False
Plot1=False # plot only 1 item

temp = names.readline()  # what to plot
temp=temp.strip("\n")
ToPlot=temp.split(' ')
#ToPlot=ToPlot[0:3]
if ToPlot[0] == "x":
    Xo=Plot1=True
    print('plot x only \n')
elif ToPlot[0] == "y":
    Yo=Plot1=True
    print('plot y only \n')
elif ToPlot[0] == "z":
    Zo=Plot1=True
    print('plot z only \n')
elif ToPlot[0] == "rx":
    Rx=Plot1=True
    print('plot rx only \n')
elif ToPlot[0] == "ry":
    Ry=Plot1=True
    print('plot ry only \n')
elif ToPlot[0] == "rz":
    Rz=Plot1=True
    print('plot rz only \n')
elif ToPlot[0] == "all":
    print('plot all \n')
    Rel=True
    Abs=True
    Rlt=True
    Tot=Plot1=True
elif ToPlot[0] == "abs":
    Abs=True
    print('plot abs \n')
elif ToPlot[0] == "rel":
    Rel=True
    print('plot rel \n')
elif ToPlot[0] == "rlt":
    Rlt=True
    print('plot rlt \n')
elif ToPlot[0] == "tot":
    Tot=Plot1=True
    print('plot total \n')


temp=names.readline() # plot time range
if len(temp) > 4:
    time1, time2 =temp.split()
    start = time_string_to_decimals(time1,0)
    end = time_string_to_decimals(time2,0)
    PlotAll=False
    print('plot start ',start,'end',end,'\n')
else:
    PlotAll=True
    start=0.0
    end=24.0
    print('plot all times\n')


Filenames=['a' for a in range (10)] # reserve some space for possible future multi file plotting
Filedates=['a' for a in range (10)]
PrFilenames=['a' for a in range (10)]
Callsigns=['a' for a in range (10)]

nfiles = 0 # number of files to plot initialized

colors=['b','g','r','c','m','y','tab:orange','tab:gray','tab:purple','tab:brown']

while True:
    temp = names.readline()  # read with current runmag filename convention
    if  len(temp) == 0:
        break
    print(temp+'\n')
    Filenames[nfiles]=temp.strip("\n")
    fdate = Filenames[nfiles].find("/") # find start of filename after subdirectory
    if fdate==-1 :  # if / not found try \
        fdate = Filenames[nfiles].find("\\")    
    
    Filedates[nfiles]=temp[17:23]
    cstart = Filenames[nfiles].find("-")
    Callsigns[nfiles]=temp[fdate+1:cstart]
    Filedates[nfiles]=temp[cstart+1:cstart+9]
    print(Callsigns[nfiles])
    print(Filedates[nfiles])    
    nfiles=nfiles + 1
        
print('number of files',nfiles)
if nfiles > 1 :
    print('1 file limit this version')
    sys.exit(0)


#saved plot directrory
PlotDir = homepath + 'Mplot/'

'''
read first file
'''
PrFilenames=(DATADIR + Filenames[0])

if (path.exists(PrFilenames)):
    print('File ' + PrFilenames + ' found!\nProcessing...')
else:
    print('File ' + PrFilenames + ' not available.\nExiting disappointed...')
    sys.exit(0)
    
# Prepare data arrays for multifile plotting in future
hours=[[],[],[],[],[],[],[],[],[],[]]
rtemp=[[],[],[],[],[],[],[],[],[],[]]
ltemp=[[],[],[],[],[],[],[],[],[],[]]
x=[[],[],[],[],[],[],[],[],[],[]] 
y=[[],[],[],[],[],[],[],[],[],[]]
z=[[],[],[],[],[],[],[],[],[],[]]
rx=[[],[],[],[],[],[],[],[],[],[]]
ry=[[],[],[],[],[],[],[],[],[],[]]
rz=[[],[],[],[],[],[],[],[],[],[]]
total=[[],[],[],[],[],[],[],[],[],[]]

filtx=[[],[],[],[],[],[],[],[],[],[]]
filty=[[],[],[],[],[],[],[],[],[],[]]
filtz=[[],[],[],[],[],[],[],[],[],[]]
filtrx=[[],[],[],[],[],[],[],[],[],[]]
filtry=[[],[],[],[],[],[],[],[],[],[]]
filtrz=[[],[],[],[],[],[],[],[],[],[]]
filttot=[[],[],[],[],[],[],[],[],[],[]]

jList=[]
istotal = True # does total item exist
LateHour=False 
    
if (isjson==True):  # read json format
    with open(PrFilenames, 'r') as dataFile:
        print('Ready to start processing json records')
        for jsonObj in dataFile:
            jDict = json.loads(jsonObj)
            jList.append(jDict)
    print("Printing each JSON Decoded Object")
    for item in jList:
        decHours=time_string_to_decimals(item["ts"],0)
        if decHours > 23:
           LateHour=True # went past 23:00 hours    
        if (not LateHour) or (LateHour and (decHours>23)):
            hours[0].append(decHours) 
    #        print(item["ts"][12:20])
            rtemp[0].append(float(item["rt"]))
            ltemp[0].append(float(item["lt"]))
            x[0].append(float(item["x"]))
            y[0].append(float(item["y"]))
            z[0].append(float(item["z"]))
            rx[0].append(float(item["rx"]))
            ry[0].append(float(item["ry"]))
            rz[0].append(float(item["rz"]))
            if "Tm" in jDict:
                total[0].append(float(item["Tm"]))
            else:
                istotal=False
        
#    sys.exit(0)
else:      
########### start plain read
    with open(PrFilenames, 'r') as dataFile:  # fead plain format
        dataReader=csv.reader(dataFile)
        data = list(dataReader)
        Header = data.pop(0)

    print('Ready to start processing plain records')

    for row in data:
        decHours=time_string_to_decimals(row[0],12)
        if decHours > 23:
           LateHour=True # went past 23:00 hours    
        if (not LateHour) or (LateHour and (decHours>23)): # Otherwise past 23:59:59.  Omit time past midnight.
            hours[0].append(decHours) # already in float because of conversion to decimal hours.
            rtemp[0].append(float(row[1]))
            ltemp[0].append(float(row[2]))
            x[0].append(float(row[3])) 
            y[0].append(float(row[4]))
            z[0].append(float(row[5]))
            rx[0].append(float(row[6]))
            ry[0].append(float(row[7]))
            rz[0].append(float(row[8]))
            if len(row) > 9 :
                total[0].append(float(row[9]))
            else: 
                print(' no tot\n')
                istotal = False
########################################### end plain read
print('done reading \n')

###############################################################################################
# Find max and min 
min_T=min(np.amin(ltemp[0]),np.amin(rtemp[0]))
max_T=max(np.amax(ltemp[0]),np.amax(rtemp[0]))
min_abs=min(np.amin(x[0]),np.amin(y[0]),np.amin(z[0]))
max_abs=max(np.amax(x[0]),np.amax(y[0]),np.amax(z[0]))
print('min T',min_T,'max T',max_T,'min abs ',min_abs,'max abs ',max_abs)
min_rel=min(np.amin(rx[0]),np.amin(ry[0]),np.amin(rz[0]))
max_rel=max(np.amax(rx[0]),np.amax(ry[0]),np.amax(rz[0]))
min_tot=np.amin(total[0])
max_tot=np.amax(total[0])
print('min rel ',min_rel,'max rel ',max_rel)

#%% Create an order 3 lowpass butterworth filter.
# This is a digital filter (analog=False)
# Filtering at .01 to .004 times the Nyquist rate seems "about right."
# The filtering argument (Wn, the second argument to butter()) of.01
# represents filtering at .05 Hz, or 20 second weighted averaging.
# That corresponds with the 20 second symmetric averaging window used in the 1 October 2019
# Excel spreadsheet for the Festival of Frequency Measurement data.
#FILTERBREAK=.005 #filter breakpoint in Nyquist rates. N. rate here is 1/sec, so this is in Hz.

b, a = butter(FILTERORDER, FILTERBREAK, analog=False, btype='low')

filtrx[0] = filtfilt(b, a, rx[0])
filtry[0] = filtfilt(b, a, ry[0])
filtrz[0] = filtfilt(b, a, rz[0])

filtx[0] = filtfilt(b, a, x[0])
filty[0] = filtfilt(b, a, y[0])
filtz[0] = filtfilt(b, a, z[0])

filttot[0] = filtfilt(b, a, total[0])

'''
============================ relative data plot
'''


if PlotAll: # set tick marks
    xt=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
else:
    tt=end-start
    xt=[start, start+.1*tt, start+.2*tt,start+.3*tt,start+.4*tt,start+.5*tt, start+.6*tt,start+.7*tt,start+.8*tt,start+.9*tt,end]

''' relative data plot
'''
if Rel:
    fig = plt.figure(figsize=(12,8))
    plt.rcParams['font.size'] = fsize
    plt.xlim([start,end])
    gs = fig.add_gridspec(3, 1, hspace=0)
    ax0= fig.add_subplot(gs[0, 0])
    ax1= fig.add_subplot(gs[1, 0])
    ax2= fig.add_subplot(gs[2, 0])
    fig.suptitle(Callsigns[0] + ' Rel Mag Data Plot '+Filedates[0])

    ax0.plot(hours[0], filtrx[0], colors[0], label='rx',linewidth=lw)
    ax0.legend(loc="lower right",  frameon=False)
    ax0.set_xlim(start,end)    
    yticks = ticker.MaxNLocator(M)
    ax0.yaxis.set_major_locator(yticks)

    ax0.set_xticks(xt, minor=False)      
    ax0.grid(axis='both')

    ax1.plot(hours[0], filtry[0], colors[1], label='ry',linewidth=lw)
    ax1.legend(loc="lower right",  frameon=False)
    
    yticks = ticker.MaxNLocator(M)
    ax1.yaxis.set_major_locator(yticks)
    ax1.set_xlim(start,end)
    ax1.set_xticks(xt, minor=False)      
    ax1.grid(axis='both')

    ax2.grid(axis='both')
    ax2.plot(hours[0], filtrz[0], colors[2], label='rz',linewidth=lw)
    ax2.legend(loc="lower right",  frameon=False)
    yticks = ticker.MaxNLocator(M)
    ax2.yaxis.set_major_locator(yticks)
    ax2.grid(axis='both')  # must set before and after !!!

    ax2.set_xlabel('UTC Hour')
    ax2.set_xlim(start,end) 
    ax2.set_xticks(xt, minor=False)

    ax1.label_outer()
    plt.grid(axis='both')
    GraphFile = Filedates[0]+'_' + Callsigns[0] + 'r.png'
    PlotGraphFile = PlotDir + GraphFile
    plt.savefig(PlotDir + GraphFile, dpi=pdpi, orientation='landscape')
    print('Plot File: ' + GraphFile + '\n')

'''absolute data plot
'''
if Abs==True:
    fig = plt.figure(figsize=(12,8))
    plt.rcParams['font.size'] = fsize
    plt.xlim([start,end])
    gs = fig.add_gridspec(3, 1, hspace=0)
    
    ax0= fig.add_subplot(gs[0, 0])
    ax1= fig.add_subplot(gs[1, 0])
    ax2= fig.add_subplot(gs[2, 0])
    
    fig.suptitle(Callsigns[0] + ' Abs Mag Data Plot '+Filedates[0])
    ax0.plot(hours[0], filtx[0], colors[0], label='x',linewidth=lw)
    ax0.legend(loc="lower right",  frameon=False)
    yticks = ticker.MaxNLocator(M)
    ax0.yaxis.set_major_locator(yticks)
    ax0.set_xlim(start,end) 
    ax0.set_xticks(xt, minor=False)
    ax0.grid(axis='both')

    ax1.plot(hours[0], filty[0], colors[1], label='y',linewidth=lw)
    ax1.legend(loc="lower right",  frameon=False)
    yticks = ticker.MaxNLocator(M)
    ax1.yaxis.set_major_locator(yticks)
    ax1.set_xlim(start,end) 
    ax1.set_xticks(xt, minor=False)
    ax1.grid(axis='both')

    ax2.grid(axis='both')
    ax2.plot(hours[0], filtz[0], colors[2], label='z',linewidth=lw)
    ax2.legend(loc="lower right",  frameon=False)
    yticks = ticker.MaxNLocator(M)
    ax2.yaxis.set_major_locator(yticks)
    ax2.grid(axis='both')  # must set before and after !!!

    ax2.set_xlabel('UTC Hour')
    ax2.set_xlim(start,end) 
    ax2.set_xticks(xt, minor=False)

    ax0.label_outer()
    ax1.label_outer()
    ax2.label_outer()
    plt.grid(axis='both')
    GraphFile = Filedates[0]+'_' + Callsigns[0] + 'a.png'
    PlotGraphFile = PlotDir + GraphFile
    plt.savefig(PlotDir + GraphFile, dpi=pdpi, orientation='landscape')
    print('Plot File: ' + GraphFile + '\n')

'''temperature data plot
'''
if Rlt :
    M = 10  # number of plot y ticks
    plt.rcParams['font.size'] = fsize
    fig = plt.figure(figsize=(12,8)) # inches x, y with 72 dots per inch
    ax = fig.add_subplot(111)
    ax.set_xlabel('UTC Hour')
    ax.set_xlim(start,end) 
    ax.set_xticks(xt, minor=False)
    ax.plot(hours[0], rtemp[0], colors[0],label='Remote T') # color k for black
    ax.plot(hours[0], ltemp[0], colors[1],label='Local T')
    yticks = ticker.MaxNLocator(M)
    ax.yaxis.set_major_locator(yticks)
    ax.set_ylabel('C')
    ax.legend(loc="lower right",  frameon=False)
    plt.grid(axis='both')
    plt.title(Callsigns[0] + ' Temperature Data Plot '+Filedates[0])

    GraphFile = Filedates[0]+'_' + Callsigns[0] + 'rt.png'
    PlotGraphFile = PlotDir + GraphFile
    plt.savefig(PlotDir + GraphFile, dpi=pdpi, orientation='landscape')
    print('Plot File: ' + GraphFile + '\n')

#-------------------------------------------------------------------
'''   single plot
'''

if Plot1 :

    M = 10  # number of plot y ticks
    plt.rcParams['font.size'] = fsize
    plt.xlim([start,end])
    fig = plt.figure(figsize=(12,8)) # inches x, y with 72 dots per inch
    ax = fig.add_subplot(111)
    ax.set_xlabel('UTC Hour')
    ax.set_xlim(start,end) 
    ax.set_xticks(xt, minor=False)

    if Xo :
        ax.plot(hours[0], filtx[0], colors[0],label='x') 
    elif Yo :
        ax.plot(hours[0], filty[0], colors[0],label='y')
    elif Zo :
        ax.plot(hours[0], filtz[0], colors[0],label='z')
    elif Rx :
        ax.plot(hours[0], filtrx[0], colors[0],label='rx')
    elif Ry :
        ax.plot(hours[0], filtry[0], colors[0],label='ry')      
    elif Rz :
        ax.plot(hours[0], filtrz[0], colors[0],label='rz')
    elif istotal and Tot:
        ax.plot(hours[0], filttot[0], colors[0],label='total')
    
    yticks = ticker.MaxNLocator(M)
    ax.yaxis.set_major_locator(yticks)
    plt.grid(axis='both')
    plt.title(Callsigns[0] + ' Mag Total Data Plot '+Filedates[0])
    
    ax.legend(loc="lower right",  frameon=False)

    GraphFile = Filedates[0]+'_' + Callsigns[0] + '1.png'
    PlotGraphFile = PlotDir + GraphFile
    plt.savefig(PlotDir + GraphFile, dpi=pdpi, orientation='landscape')
    print('Plot File: ' + GraphFile + '\n')    
    

print('Exiting python magplot program gracefully')
