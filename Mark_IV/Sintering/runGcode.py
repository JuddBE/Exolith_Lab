from yMoveCoord import yMoveCoord
from xMoveCoord import xMoveCoord
from xyMoveCoord import xyMoveCoord
from zMoveCoord import zMoveCoord
from axisReset import axis_reset
import os
import sys

"""
Sinters an object according to a GCODE file.
"""

def read_gcode(file_name="Cube32mm.gcode", layer_height=0.15):
    # Initialize start coord, offsets, speed values, and file names
    current_layer = 0
    start_coord = [5, 5, 1.4]
    x_offset = 0.0
    y_offset = 0.0
    z_offset = 0.0
    xy_fast = 1.0
    xy_slow = 0.1
    set_offset = True
    z_speed_mod = 0.3
    pause = 1
    pause_file_name = "./txtfiles/pause.txt"
    x_file_name = "./txtfiles/x_coord.txt"
    y_file_name = "./txtfiles/y_coord.txt"
    z_file_name = "./txtfiles/z_coord.txt"
    file_name = "./gcode/" + file_name
    os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")

    # Get current x, y, and z coords. Set start coords for the print to be the current coords.
    if(os.path.exists(x_file_name)) and os.stat(x_file_name).st_size != 0:
        with open(x_file_name, "r") as f:
            start_coord[0] = float(f.readline())
    else:
        with open(x_file_name, "w") as f:
            f.write("0\n")

    if(os.path.exists(y_file_name)) and os.stat(y_file_name).st_size != 0:
        with open(y_file_name, "r") as f:
            start_coord[1] = float(f.readline())
    else:
        with open(y_file_name, "w") as f:
            f.write("0\n")
    
    if(os.path.exists(z_file_name)) and os.stat(z_file_name).st_size != 0:
        with open(z_file_name, "r") as f:
            start_coord[2] = float(f.readline())
    else:
        with open(z_file_name, "w") as f:
            f.write("0\n")

    # Update pause value (will now pause after a layer)
    with open(pause_file_name, "w") as f:
        f.write("1")

    # Read gcode file and interpret instructions
    with open(file_name, "r") as f:
        for line in f:
            light_pause = True
            # Prepare for G0 function (move without sintering)
            if "G0" in line:
                xy_speed_mod = xy_fast
                light_pause = False

            # Prepare for G1 function (move while sintering)
            if "G1" in line:
                xy_speed_mod = xy_slow

            # Perform movement function
            if "G0" in line or "G1" in line:
                x = -1
                y = -1
                z = -1
                line_segs = line.split(' ')

                # Set x, y, z destinations for a line
                for seg in line_segs:
                    if seg[0] == "X":
                        x = float(seg[1:]) / 10
                        
                    elif seg[0] == "Y":
                        y = float(seg[1:]) / 10
                        
                    elif seg[0] == "Z":
                        z = current_layer * layer_height + start_coord[2]

                # The first time all axes are moved, set the offset for each axis based on this.
                # That is because the first coordinate is the starting coordinate for the gcode,
                # and we want to consider that coordinate as (0, 0, 0) for the print.
                if x != -1 and y != -1 and z != -1 and set_offset:
                    set_offset = False
                    if start_coord[0] > 0.5:
                        x_offset = start_coord[0] - x
                    if start_coord[1] > 0.5:
                        y_offset = start_coord[1] - y
                    if start_coord[2] > 0.5:
                        z_offset = start_coord[2] - z
                
                # Move x and y
                if x != -1 and y != -1:
                    xyMoveCoord(x + x_offset, y + y_offset, xy_speed_mod, pause=light_pause)
                # Move x
                elif x != -1 and y == -1:
                    xMoveCoord(x + x_offset, xy_speed_mod, pause=light_pause)
                # Move y
                elif x == -1 and y != -1:
                    yMoveCoord(y + y_offset, xy_speed_mod, pause=light_pause)
                # Move z
                if z != -1:
                    current_layer += 1
                    zMoveCoord(z + z_offset, z_speed_mod)

                    # If not first layer (gcode files have 2 z movements before needing to start the 2nd layer)
                    # Then pause and wait until user starts the new layer.
                    if current_layer > 2:
                        while(pause != "0"):
                            with open(pause_file_name, "r") as f:
                                pause = f.readline()
                        with open(pause_file_name, "w") as f:
                            pause = "1"
                            f.write("1")
                
def main():
    num_args = len(sys.argv)
    if num_args == 2:
        read_gcode(sys.argv[1])
    if num_args == 3:
        read_gcode(sys.argv[1], float(sys.argv[2]))
    else:
        read_gcode()

if __name__ == "__main__":
    main()