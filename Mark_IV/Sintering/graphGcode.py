import matplotlib.pyplot as plt
import numpy as np

def graph_gcode():
    count = 0
    x_coords = []
    y_coords = []
    z_coords = []

    file_name = "Cube.gcode"
    pause_file_name = "pause.txt"

    with open(pause_file_name, "w") as f:
        f.write("1")
    with open("./gcode/" + file_name, "r") as f:
        for line in f:
            if "G0" in line or "G1" in line:
                x = -1
                y = -1
                z = -1
                line_segs = line.split(' ')
                for seg in line_segs:
                    if seg[0] == "X":
                        x = float(seg[1:]) / 10
                        
                    elif seg[0] == "Y":
                        y = float(seg[1:]) / 10
                        
                    elif seg[0] == "Z":
                        z = float(seg[1:]) / 10
                        
                if z != -1:
                    z_coords.append(z)
                else:
                    z_coords.append(z_coords[count - 1])
                if x != -1 and y != -1:
                    x_coords.append(x)
                    y_coords.append(y)
                elif x != -1 and y == -1:
                    x_coords.append(x)
                    y_coords.append(y_coords[count - 1])
                elif x == -1 and y != -1:
                    x_coords.append(x_coords[count - 1])
                    y_coords.append(y)
                else:
                    x_coords.append(0)
                    y_coords.append(0)
                count += 1

    x_coords = np.array(x_coords[2:(len(x_coords)-1)])
    y_coords = np.array(y_coords[2:(len(y_coords)-1)])
    z_coords = np.array(z_coords[2:(len(z_coords)-1)])
    # x_coords = np.array(x_coords[2:400])
    # y_coords = np.array(y_coords[2:400])
    # z_coords = np.array(z_coords[2:400])

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_box_aspect([max(x_coords) - min(x_coords), max(y_coords) - min(y_coords), max(z_coords) - min(z_coords)])
    ax.plot_wireframe(x_coords,y_coords,z_coords.reshape(-1, 1))
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel("Z (cm)")
    plt.show()
            
def main():
    graph_gcode()

if __name__ == "__main__":
    main()