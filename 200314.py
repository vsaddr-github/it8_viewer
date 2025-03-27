# This script is licensed under the GNU GENERAL PUBLIC LICENSE
# All credits go to Vlads Test Target
# https://medium.com/@vladstesttarget
# email: vlads.test.target@gmail.com

# version 1.1 3/26/2025 Vlads Test Target Scale changed to 100
# extra reference https://www.easyrgb.com/en/math.php

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

show_rgb_text = True  # Toggle for RGB text overlay
# Conversion mode flags
use_prophoto = False
use_srgb_d50 = True
apply_gamma = True
black_mask=True # mask colors not compliant
threshold=0.035

num_clip=0
conversion=""

# Load the file
file_path = "F210418.txt"
it8name=os.path.splitext(os.path.basename(file_path))[0]
script_name = os.path.basename(__file__)

# Read file and extract data lines
with open(file_path, "r") as file:
    lines = file.readlines()

# Find the start and end of the data section
start_index = next(i for i, line in enumerate(lines) if line.strip() == "BEGIN_DATA") + 1
end_index = next(i for i, line in enumerate(lines) if line.strip() == "END_DATA_FORMAT")

# Extract and clean column headers
columns = ['SAMPLE_ID', 'XYZ_X', 'XYZ_Y', 'XYZ_Z']

# Extract data for XYZ columns only
data_lines = lines[start_index:start_index + 286]  # 286 color patches
data = [line.strip().split()[:4] for line in data_lines]
df = pd.DataFrame(data, columns=columns)
df[['XYZ_X', 'XYZ_Y', 'XYZ_Z']] = df[['XYZ_X', 'XYZ_Y', 'XYZ_Z']].astype(float)

# Find the highest value in XYZ and normalize by it
max_xyz_value = df[['XYZ_X', 'XYZ_Y', 'XYZ_Z']].values.max()
print(f"Maximum XYZ value from data: {max_xyz_value}")
max_xyz_value = 100# 80.63 #76.01
print(f"Maximum XYZ value actually used: {max_xyz_value}")
xyz_normalized = df[['XYZ_X', 'XYZ_Y', 'XYZ_Z']] / max_xyz_value


# Apply gamma correction (sRGB gamma approximation)
def gamma_correct(r, g, b):
    def correct(c):
        return ((1.055 * (c ** (1 / 2.4))) - 0.055) if c > 0.0031308 else 12.92 * c
    return correct(r), correct(g), correct(b)

# Convert XYZ to RGB (sRGB D65, sRGB D50, or ProPhotoRGB)
# see also http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
# https://computergraphics.stackexchange.com/questions/13878/what-are-the-exact-math-steps-to-convert-srgb-d65-to-lab-d50-colorspace
def xyz_to_rgb(sample_id,x, y, z, prophoto=False, srgb_d50=False, gamma=False):
    global num_clip,conversion
    if prophoto:
        r =  1.3459433*x - 0.2556075*y - 0.0511118*z
        g = -0.5445989*x + 1.5081673*y + 0.0205351*z
        b =  0.0000000*x + 0.0000000*y + 1.2118128*z
    elif srgb_d50:
        # https://www.image-engineering.de/library/technotes/958-how-to-convert-between-srgb-and-ciexyz
        r =  3.1338561*x - 1.6168667*y - 0.4906146*z
        g = -0.9787684*x + 1.9161415*y + 0.0334540*z
        b =  0.0719453*x - 0.2289914*y + 1.4052427*z
    else:
        # https://www.easyrgb.com/en/math.php   XYZ → Standard-RGB  D65 
        r =  3.2406*x - 1.5372*y - 0.4986*z
        g = -0.9689*x + 1.8758*y + 0.0415*z
        b =  0.0557*x - 0.2040*y + 1.0570*z
        
     
    if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
        # we apply gamma correctin to unclippped value exclusively to be able to 
        # match those clipped patches with ones shown on screen
        r1, g1, b1 = gamma_correct(r, g, b)
        num_clip += 1
        print(f"{num_clip: 4}. Patch {sample_id:<3}, unclipped  RGB=({r1*255: >+7.3f}, {g1*255: >+7.3f}, {b1*255: >+7.3f}) XYZ {x} {y} {z} ")
        if black_mask:
            if not ( (0-threshold) <= r <= (1+threshold) and (0-threshold) <= g <= (1+threshold) and (0-threshold) <= b <= (1+threshold)):
               brightness = 0.299 * r + 0.587 * g + 0.114 * b
               if brightness < 0.5:
                   r, g, b = 0, 0, 0
               else:
                   r, g, b = 1, 1, 1
            else:
               r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))   
        else:
           r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))
    else:  
        r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))
    if gamma:
        r, g, b = gamma_correct(r, g, b)
    return r, g, b

colors = []


if use_prophoto:
    conversion="ProPhotoRGB" # efficincy 
elif use_srgb_d50:
    conversion="sRGB_d50"
else:
    conversion="sRGB_d65"


for i, (x, y, z) in enumerate(xyz_normalized.values):
    sample_id = df.iloc[i]['SAMPLE_ID']
    r, g, b = xyz_to_rgb(sample_id, x, y, z, prophoto=use_prophoto, srgb_d50=use_srgb_d50, gamma=apply_gamma)
    colors.append((r, g, b))

# Plotting 286 patches in rows of 22 columns
num_patches = 286
columns_per_row = 22
rows = (num_patches + columns_per_row - 1) // columns_per_row


fig, ax = plt.subplots(figsize=(18, 9))
for idx, color in enumerate(colors[:num_patches]):
    row = idx // columns_per_row
    col = idx % columns_per_row
    rect = mpatches.Rectangle((col, row), 1, 1, color=color)
    ax.add_patch(rect)
    r_disp, g_disp, b_disp = [int(c * 255) for c in color]
    brightness = 0.299 * r_disp + 0.587 * g_disp + 0.114 * b_disp
    text_color = 'black' if brightness > 128 else 'white'
    if show_rgb_text:
        ax.text(col + 0.5, row + 0.5, f"{r_disp},{g_disp},{b_disp}",
                ha='center', va='center', fontsize=6, color=text_color)

ax.set_xlim(0, columns_per_row)
ax.set_ylim(rows, 0)
ax.set_aspect('equal')
ax.axis('off')

# Add column numbers (1 to 22) below the chart
for col_num in range(columns_per_row):
    ax.text(col_num + 0.5, rows + 0.2, str(col_num + 1), ha='center', va='top', fontsize=8, fontweight='bold', color='0.5')

# Add row letters (A to L) on the left (A to L) on the left
import string
for row_num in range(rows):
    ax.text(-0.5, row_num + 0.5, string.ascii_uppercase[row_num], ha='right', va='center', fontsize=8, fontweight='bold', color='0.5')
plt.title(f"IT8 Chart - Visualized from XYZ Data (286 patches, 22 per row) WF#: {it8name} Scale {max_xyz_value}. {script_name}. {conversion} nc-{num_clip}. By VLADS TEST TARGET", fontsize=16, pad=30)
plt.subplots_adjust(top=0.5)
plt.tight_layout()

from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%dT%H-%M-%S")
plt.savefig(f"{it8name}_{script_name}_chart_{timestamp}_m{max_xyz_value}_black_mask{black_mask}_{conversion}_{num_clip}.png", dpi=300)
plt.show()
