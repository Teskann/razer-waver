import json
import colorsys
import os
import argparse
import numpy as np

parser = argparse.ArgumentParser(description="Generate an RGB wave effect for polychromatic.")
parser.add_argument("-d", "--duration", help="Wave period in seconds. Default is 5.", default="5")
parser.add_argument("-D", "--direction", help="Wave direction. `LR` for left to right, `RL` for right to left. Default is `LR`", default='LR')
parser.add_argument("--fps", help="Frames per seconds of the wave. Defaults to 24.", default='24')
parser.add_argument("-c", "--columns", help="Number of columns in the keyboard. Default is 22.", default="22")
parser.add_argument("-r", "--rows", help="Number of rows in the keyboard. Default is 6.", default="6")
parser.add_argument("--device", help="Name of the Razer device. Defaults to `Razer Ornata V2`. Please, enter the real name of the device, "
                                     "as it shows up in Polychromatic. You will probably need to fix the number of rows and columns"
                                     " so they fit your device, using `-r` and `-c` parameters. To know how many columns and rows your "
                                     "device has, you can create a dummy Polychromatic effect and check how many rows/columns appear in the "
                                     "matrix. Underglow should be supported with the correct values.", default="Razer Ornata V2")
parser.add_argument("-o", "--output", help="Output file path. Default is `~/.config/polychromatic/effects/wave.json`", default="~/.config/polychromatic/effects/wave.json")
parser.add_argument("-v", "--vertical", help="Make wave which moves vertically instead of wave which moves horizontally (which is default)", action="store_true")
parser.add_argument("--delta", help="Delta hue between adjacent cols (if the wave moves horizontally) or between rows (if the wave moves vertically)", default = None)
parser.add_argument("-p", "--pretend", help="Generate frames, but don't save", action="store_true")
parser.add_argument("--offset", help = 'Add offset in the beginning and at the end of hue spectrum', default = 5)

args = parser.parse_args()
direction = args.direction
cols = int(args.columns)
rows = int(args.rows)
duration = float(args.duration)  # seconds
device = args.device
fps = int(args.fps)
vertical = args.vertical
pretend = args.pretend
name = args.output.split("/")[-1].split(".")[0].title()
delta = None if args.delta is None else float(args.delta)
frames = []
offset = int(args.offset)

data = {"name": name,
        "type": 3,
        "author": "Teskann",
        "author_url": "https://github.com/Teskann/razer-waver",
        "icon": "img/options/wave.svg",
        "summary": "",
        "map_device": device,
        "map_device_icon": "keyboard",
        "map_graphic": "blackwidow_m_keys_en_GB.svg",
        "map_cols": cols,
        "map_rows": rows,
        "save_format": 8,
        "revision": 1,
        "fps": fps,
        "loop": True,
        "frames": frames
        }

nb_frames = int(duration * fps)
delta_hue_frames = 1 / nb_frames

hues = ((np.sin(np.linspace(0, 1, nb_frames) * np.pi + 3 * np.pi / 2) + 1) / 2).tolist()

if offset > 0:
    hues = hues[offset:-offset]

for i_frame in range(nb_frames - offset * 2):
    current_frame = {}
    frames.append(current_frame)

    if vertical:  # color is constant across columns
        delta_hue_row = 1 / rows if delta is None else delta
        for i_row in range(rows):
            hue = (hues[i_frame] + i_row * delta_hue_row) % 1
            rgb = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
            hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
            row_key = str(i_row)
            for i_cols in range(cols):
                col_key = str(i_cols)
                if col_key in current_frame:
                    current_frame[col_key][row_key] = hex_color
                else:
                    current_frame[col_key] = {row_key: hex_color}
    else:  # color is constant across rows
        delta_hue_col = 1 / cols if delta is None else delta
        for i_col in range(cols):
            hue = (hues[i_frame] + i_col * delta_hue_col) % 1
            rgb = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
            hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
            row_values = {}
            for i_rows in range(rows):
                row_values[str(i_rows)] = hex_color  # Constant across rows
            frames[-1][str(i_col)] = row_values

if direction == 'LR':
    data["frames"] = frames[::-1]

if pretend:
    exit(0)

save_path = os.path.expanduser(args.output)
if os.path.exists(save_path):
    ans = input(f"The file {save_path} already exists. Do you want to overwrite it ? (y/[n]) ")
    if ans.lower() != 'y':
        print("Aborting ...")
        exit(-1)
try:
    with open(save_path, 'w') as f:
        f.write(json.dumps(data, indent=4))
    print("Wave effect file successfully created ! Open polychromatic to apply it on your keyboard !")
except FileNotFoundError as e:
    print(f"No such file or directory: '{save_path}'. Be sure you have "
          f"installed polychromatic ! If you have installed it, launch it and "
          f"retry. You can also use --output to save your file elsewhere.")
    exit(-1)
