#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plots PSWS magnetometer data from runmag.log
plots either plain text or json format files
v2.0
   X = the absolute value of reported Z and Z = X for absolute data for PSWS orientated RM3100
   raw data axes unchanged
   filtering changed to gaussian with default sigma=16 -> 95 x 1s samples ~95 s
   intermag uses 19 x 5s samples ~ 95 s   "intermag_4-6_tech ref manual sec 2.2"

expects filename with callsign to process 
expects magnetometer data files in homepath/logs
leaves plots in homepath/Mplot
note - reports min & max remote temperatures to shell, can also plot as a single item

windows version hardcoded homepath directory location
for Pi comment out windows homepath and uncomment Pi  lines

uses modified WWV_utility2.py now called Mag_utility
Bob Benedict, KD8CGH, 10/21/2021

create text file "files.txt" in homepath directory, uses keyword and value, i.e. "type json"
  type (json or plain)
  plot (all, abs, raw, tot, rlt, total, x, y, z, rx, ry, rz, rt (remote temperature))  
  time (all, start and finsh in hours:min:sec)
  scale (matp, 10nT)  divisions on y scales - matp is matplotlib's best estimate, 10nT is fixed 10 nT 
  filename 
  
  example:
type json
plot abs
time 09:33:00 12:59:00
scale 10nT
KD8CGH-20211020-runmag.log 

loads file name
plots absolute, relative, total (if available) and temperature plots, reports min/max remote T to shell
magnetometer results are filtered before plotting
plot appearnce parameters at line 66 including filter parameters
using guassian filter, default sigma is from intermag_4-6_tech ref manual sec 2.2 

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
from scipy.ndimage import gaussian_filter
import datetime  
from Mag_utility import time_string_to_decimals
import json

# plot appearance parameters
M = 6  # number of plot y axis ticks, except abs Y data y axis set to 10 nT by convention
lw=0.6  # plot line width
pdpi=250 # final plot image dpi
fsize='10' # font size
# lowpass butterworth filter parameters , deprecated for gaussian
#FILTERBREAK=0.01 # filter breakpoint in Nyquist rates. N. rate here is 1/sec, 0.005 used in Grape 1 doppler so is in Hz. 
#FILTERORDER=6   # 6
gf_simga=16 # guassian filter sigma
# A gaussian kernel requires 6 σ − 1  values, e.g. for a σ of 3 it needs a kernel of length 17.
# sigma=16 -> 95 x 1s samples ~95 s
# intermagnet uses 19 x 5s samples ~ 95 s

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

temp = names.readline() # what format will the data be in?
temp=temp.strip("\n")
FileType=temp.split(' ')
if FileType[1] == 'json':
    isjson=True
    print('json file \n')
else:
    isjson=False
    print('plain text file \n')

# flags for what to plot
Raw=False
Abs=False
Rlt=False
Tot=False
Xo=Yo=Zo=False
Rx=Ry=Rz=Rt=False
Plot1=nT=False # plot only 1 item

temp = names.readline()  # what to plot
temp=temp.strip("\n")
ToPlot=temp.split(' ')
if ToPlot[1] == "x":
    Xo=Plot1=True
    print('plot x only \n')
elif ToPlot[1] == "y":
    Yo=Plot1=True
    print('plot y only \n')
elif ToPlot[1] == "z":
    Zo=Plot1=True
    print('plot z only \n')
elif ToPlot[1] == "rx":
    Rx=Plot1=True
    print('plot rx only \n')
elif ToPlot[1] == "ry":
    Ry=Plot1=True
    print('plot ry only \n')
elif ToPlot[1] == "rz":
    Rz=Plot1=True
    print('plot rz only \n')
elif ToPlot[1] == "rt":
    Rt=Plot1=True
    print('plot remote temperature only \n')    
elif ToPlot[1] == "all":
    print('plot all \n')
    Raw=True
    Abs=True
    Rlt=True
    Tot=Plot1=True
elif ToPlot[1] == "abs":
    Abs=True
    print('plot abs \n')
elif ToPlot[1] == "raw":
    Raw=True
    print('plot raw \n')
elif ToPlot[1] == "rlt":
    Rlt=True
    print('plot rlt \n')
elif ToPlot[1] == "tot":
    Tot=Plot1=True
    print('plot total \n')

temp=names.readline() # plot time range
temp=temp.strip("\n")
Times=temp.split(' ')
if len(Times[1]) > 4:
    start = time_string_to_decimals(Times[1],0)
    end = time_string_to_decimals(Times[2],0)
    PlotAll=False
    print('plot start ',start,'end',end,'\n')
else:
    PlotAll=True
    start=0.0
    end=24.0
    print('plot all times\n')

temp = names.readline()  # scales
temp=temp.strip("\n")
Scale=temp.split(' ')
if Scale[1] == "10nT":
    nT=True
    print('scale y axis by 10nT \n')
else:
    print('let matplotlib scale y axis\n')


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
#    print("Printing each JSON Decoded Object")
    for item in jList:
        decHours=time_string_to_decimals(item["ts"],11)  # was 0
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
    with open(PrFilenames, 'r') as dataFile:  # read plain format file
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
                istotal = False
                
########################################### end plain read
print('done reading \n')



min_rT=min(np.amin(rtemp[0]),np.amin(rtemp[0]))
max_rT=max(np.amax(rtemp[0]),np.amax(rtemp[0]))
print('minimum remote temperature ',min_rT,' maximum remote temperature ',max_rT, '\n')

###############################################################################################
'''
# Find max and min 
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

'''
# *********************************************** gaussian filtering
filtrx[0] = gaussian_filter(rx[0], sigma=gf_simga, mode='nearest')
filtry[0] = gaussian_filter(ry[0], sigma=gf_simga, mode='nearest')
filtrz[0] = gaussian_filter(rz[0], sigma=gf_simga, mode='nearest')

# *********************************************note direction swap !!!
filtz[0] = gaussian_filter(x[0], sigma=gf_simga, mode='nearest')
filty[0] = gaussian_filter(y[0], sigma=gf_simga, mode='nearest')
filtx[0] = abs(gaussian_filter(z[0], sigma=gf_simga, mode='nearest'))
if istotal == True :
    filttot[0] = gaussian_filter( total[0], sigma=gf_simga, mode='nearest')

if PlotAll: # set x axis tick marks
    xt=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
else:
    tt=end-start
    xt=[start, start+.1*tt, start+.2*tt,start+.3*tt,start+.4*tt,start+.5*tt, start+.6*tt,start+.7*tt,start+.8*tt,start+.9*tt,end]

''' raw data plot
'''
if Raw:
    fig = plt.figure(figsize=(12,8))
    plt.rcParams['font.size'] = fsize
    plt.xlim([start,end])
    plt.tick_params(labelleft=False, left=False)
    plt.tick_params(labelbottom=False, bottom=False)
    gs = fig.add_gridspec(3, 1, hspace=0)
    
    ax0= fig.add_subplot(gs[0, 0])
    ax1= fig.add_subplot(gs[1, 0])
    ax2= fig.add_subplot(gs[2, 0])
    fig.suptitle(Callsigns[0] + ' Raw Mag Data Plot '+Filedates[0])

    ax0.plot(hours[0], filtrx[0], colors[0], label='rx',linewidth=lw)
    ax0.legend(loc="lower right",  frameon=False)
    ax0.set_xlim(start,end)    
    yticks = ticker.MaxNLocator(M)
    ax0.yaxis.set_major_locator(yticks)
    
#    plt.tick_params(bottom=False)
    ax0.set_xticks(xt, minor=False)
    ax0.set(xticklabels=[])
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
#    plt.show()

'''absolute data plot
'''
if Abs==True:
    fig = plt.figure(figsize=(12,8))
    plt.rcParams['font.size'] = fsize
    plt.xlim([start,end])
    plt.tick_params(labelleft=False, left=False)
    plt.tick_params(labelbottom=False, bottom=False)
    gs = fig.add_gridspec(3, 1, hspace=0)
    
    ax0= fig.add_subplot(gs[0, 0])
    ax1= fig.add_subplot(gs[1, 0])
    ax2= fig.add_subplot(gs[2, 0])
    
    fig.suptitle(Callsigns[0] + ' Abs Mag Data Plot, PSWS orientation'+Filedates[0])
    ax0.plot(hours[0], filtx[0], colors[0], label='x, N',linewidth=lw)
    ax0.legend(loc="lower right",  frameon=False)
 
    if nT :
        miny = np.amin(filtx[0])//10.0
        maxy = np.amax(filtx[0])//10.0 + 1
        nyticks=(maxy-miny) + 1
        yticks = ticker.MaxNLocator(nyticks)
    else:
        yticks = ticker.MaxNLocator(M)
        
    ax0.yaxis.set_major_locator(yticks)
      
    ax0.set_xlim(start,end) 
    ax0.set_xticks(xt, minor=False)
    ax0.grid(axis='both')

    ax1.plot(hours[0], filty[0], colors[1], label='y, E',linewidth=lw)
    ax1.legend(loc="lower right",  frameon=False)
    
    #  find number of yticks so spaced 10 apart
    if nT :
        miny = np.amin(filty[0])//10.0
        maxy = np.amax(filty[0])//10.0 + 1
        nyticks=(maxy-miny) + 1
        yticks = ticker.MaxNLocator(nyticks)
    else:
        yticks = ticker.MaxNLocator(M)
        
    ax1.yaxis.set_major_locator(yticks)
    
    ax1.set_xlim(start,end) 
    ax1.set_xticks(xt, minor=False)
    ax1.grid(axis='both')

    ax2.grid(axis='both')
    ax2.plot(hours[0], filtz[0], colors[2], label='z',linewidth=lw)
    ax2.legend(loc="lower right",  frameon=False)
 
    if nT :
        miny = np.amin(filtz[0])//10.0
        maxy = np.amax(filtz[0])//10.0 + 1        
        nyticks=(maxy-miny)
        ax2.set_ylim(miny*10, maxy*10)
        yticks = ticker.MaxNLocator(nyticks)
    else:
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
#    plt.show()

'''temperature data plot
'''
if Rlt :
    M = 10  # number of plot y ticks
    plt.rcParams['font.size'] = fsize
    fig = plt.figure(figsize=(12,8)) # inches x, y with dpdi dots per inch
    plt.tick_params(labelleft=False, left=False)
    plt.tick_params(labelbottom=False, bottom=False)
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

    plt.rcParams['font.size'] = fsize
    plt.xlim([start,end])
    fig = plt.figure(figsize=(12,8)) # inches x, y with dpdi dots per inch
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
    elif Rt : 
        ax.plot(hours[0], rtemp[0], colors[0],label='remote T')        
    else:
        print('nothing to plot \n')
           
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
