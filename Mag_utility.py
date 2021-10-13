# -*- coding: utf-8 -*-
"""
10/2/2021 mod by Bob Benedict KD8CGH for mag plot
WWV utility file
Routines and classes used in WWV file management and graphing
David Kazdan, AD8Y
John Gibbons, N8OBJ - mods to plot header 2/3/20

"""

#%% utility function needed here to convert ISO time into decimal hours
def time_string_to_decimals(time_string, start): #returns float decimal hours
    
    #print('Input time string=',time_string)
#    if (NewHdr = 'New'):   # if new header strip off date and Zulu stuff
#        time_string = time_string[11:-1]  # Hack off date 'YYYY-MM-DDT' and ending 'Z'
    time_string = time_string[start:]  # start=12 to Hack off date 'YYYY-MM-DDT' and ending 'Z'
#    print('Used Time_String=',time_string)
    fields=time_string.split(":")
    hours=float(fields[0]) if len(fields)>0 else 0.0
    minutes=float(fields[1])/60. if len(fields)>0 else 0.0
    seconds=float(fields[2])/3600. # if len(fields)>0 else 0.0
#    print('Hr=',hours, '  Min=',minutes, '  Sec=',seconds, '  ',float(fields[2]),'\n')
    return (hours + minutes + seconds)

