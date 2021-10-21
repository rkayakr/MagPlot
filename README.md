plots PSWS magnetometer data from runmag.log
plots either plain text or json format files
v2.0
   X = the absolute value of reported Z and Z = X for absolute data for PSWS orientated RM3100
   absolute Y axis meets convention of 10 nT ticks
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
Bob Benedict, KD8CGH, 10/02/2021

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
plot appearnce parameters at line 67 including filter parameters
using guassian filter, default sigma is from intermag_4-6_tech ref manual sec 2.2 

uses modified WWV_utility2.py 
20 February 2020
WWV utility file
Routines and classes used in WWV file management and graphing
David Kazdan, AD8Y
John Gibbons, N8OBJ - mods to plot header 2/3/20
