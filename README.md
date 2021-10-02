# MagPlot
plots PSWS magnetometer data in runmag.log

windows version hardcoded homepath directory location
for Pi comment out windows homepath and uncomment Pi  lines

expects filemane to process in files.txt in PSWS/magnetometer
expects magnetometer data files in PSWS/magnetometer/Mdata
leaves plots in PSWS/magnetometer/Mplot

uses modified WWV_utility2.py
Bob Benedict, KD8CGH, 10/02/2021

create text file "files.txt" in homepath directory
  filename 

  ...

loads file name
plots absolute, relative, total (if available) and temperature plots
magnetometer results are filtered before plotting

