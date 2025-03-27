# it8_viewer
IT8ProfileView

This will read data file provided by Wolf Faust along with his IT8 transparency target and show on the screen RGB equivalent of XYZ data stored in file. The png file is also written on disk for review late

# Sample png files included

In the following files XYZ data has been scaled by factor 100 

F210418_200314.py_chart_20250326T21-37-14_m100_black_maskTrue_ProPhotoRGB_0.png - converted to ProPhotoRGB

F210418_200314.py_chart_20250326T21-37-37_m100_black_maskTrue_sRGB_d65_58.png - converted to sRGB with D65
 
F210418_200314.py_chart_20250326T21-58-22_m100_black_maskTrue_sRGB_d50_57.png - converted to sRGB with D50


# Python version: 

$python -V
Python 3.10.11

# Running

It is expected that data file "F210418.txt" is located in the same folder. 
File name is hardcoded for simplicity 

 python 200314.py