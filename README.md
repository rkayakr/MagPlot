# MagPlot
plots PSWS magnetometer data from runmag.log
plots either plain text or json format files

windows version hardcoded homepath directory location
expects filename with callsign to process in files.txt in homepath
expects magnetometer data files in homepath/logs
leaves plots in homepath/Mplot

for Pi comment out windows homepath and uncomment Pi  lines
leaves plots in homepath/Mplot

uses modified WWV_utility2.py now called Mag_utility
Bob Benedict, KD8CGH, 10/02/2021

create text file "files.txt" in homepath directory
  filetype (json or plain)
  filename 
  ...

loads file name
plots absolute, relative, total (if available) and temperature plots
magnetometer results are filtered before plotting
plot appearnce parameters at line 51
