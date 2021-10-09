# MagPlot
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
