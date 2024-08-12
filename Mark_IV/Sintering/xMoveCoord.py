import RPi.GPIO as GPIO
from time import sleep
from Limit_Switches import limitSwitches
from elevationTracking import elevation_tracker
import time
import math
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

"""
Moves both motor 1 and motor 2 of the X axis. Currently CW || 0 moves the x axis forward
DOES NOT HAVE LIMIT SWITCH FUNCTIONALITY INCLUDED. POTENTIALLY DESTRUCTIVE 
"""

et = elevation_tracker()
ls = limitSwitches()


def xMoveCoord(coord=5, speed_mod=0.6, pause=False):
    GPIO.setwarnings(False)
    
    if speed_mod > 1:
        print("Speed mod too large, set to 1")
        speed_mod = 1
    
    if coord < 0:
        print("Coordinate less than 0, set to 0")
        coord = 0

    # Direction pin from controller
    DIR = int(os.getenv("MOTOR_X_Direction"))  # DIR+
    STEP = int(os.getenv("MOTOR_X_Pulse"))  # PULL+
    pixMin = float(os.getenv("pixMin"))
    useGPS = os.getenv("useGPS")

    # Max x coordinate in cm
    X_MAX = 32

    # 0/1 used to signify clockwise or counterclockwise.
    CW = 0
    CCW = 1
    motor_flag = 0
    x_coord = 0.0
    file_name = "./txtfiles/x_coord.txt"
    brightness_file_name = "./txtfiles/brightness_val.txt"
    os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")

    # Based on distance traveled each step of the motor along the threaded rod.
    increment = 0.000635

    # Setup x limit switch
    GPIO.setmode(GPIO.BCM)
    motor1_switch = int(os.getenv("limitSwitchX_1"))
    GPIO.setup(motor1_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Establish Pins in software
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)

    try:
        # Read x coordinate if file exists, otherwise make the file
        if(os.path.exists(file_name)) and os.stat(file_name).st_size != 0:
            with open(file_name, "r") as f:
                x_coord = float(f.readline())
        else:
            with open(file_name, "w") as f:
                f.write("0\n")

        # # currentTiltAngleX, currentTiltAngleY = et.tiltAngle() # Get current elev angle.
        # currentTiltAngleX = et.kalAngleX # Get current elev angle.
        # print(currentTiltAngleX)

        # print("Before: " + str(coord))
        # # Calculate x offset due to angle of sun by focusing the lens 
        # # at the F1 (more positive x coordinate side) focus of the ellipse.
        # focal_diameter = 0.6
        # ellipse_b = focal_diameter / 2.0
        # ellipse_a = ellipse_b * (1.0 / (1 - math.cos(float(currentTiltAngleX) * math.pi / 180)))
        # # coord = coord + math.sqrt(abs(ellipse_a * ellipse_a - ellipse_b * ellipse_b))
        # coord += abs(ellipse_a / 2)
        # print("After: " + str(coord))
        
        # Distance between target and current coords
        distance = abs(coord - x_coord)

        # Set direction
        if coord > x_coord and distance > increment / 2:
            GPIO.output(DIR, CW)
        elif coord < x_coord and distance > increment / 2:
            GPIO.output(DIR, CCW)
            increment *= -1
        else:
            # If the distance is too small (or 0), keep the previous coordinate and don't move
            with open(file_name, "w") as f:   
                f.write(str(x_coord) + "\n")
            print("x: " + str(x_coord))
            return

        # Calculate number of steps to move desired distance
        num_steps = int(round(distance / 0.000635, 0))
        
        # Start updating x coordinate from the current coordinate
        f = open(file_name, "w")
        f.write(str(x_coord) + "\n")
        f.seek(0)
        brightness_file = open(brightness_file_name, "r+")

        # Move x motors step by step
        for x in range(num_steps):
            # Check if the stand should pause when sun is not detected
            if pause and useGPS == "True":
                # Only check if x movement should pause every 50 motor steps
                if x % 50 == 0:
                    pixVal = brightness_file.readline()
                    if pixVal != "":
                        pixVal = float(pixVal)
                    else:
                        pixVal = pixMin
                    brightness_file.seek(0)

                # Enter pausing loop until the brightness value passes a certain threshold
                while(pixVal < pixMin):
                    time.sleep(0.01)
                    pixVal = brightness_file.readline()
                    if pixVal != "":
                        pixVal = float(pixVal)
                    else:
                        pixVal = 0
                    brightness_file.seek(0)

            if x_coord + increment > X_MAX:
                print("X Coordinate out of bounds")
                return
            
            # Set one coil winding to high
            GPIO.output(STEP,GPIO.HIGH)

            #.5 == super slow
            # .00005 == breaking
            sleep(.001 / speed_mod) # Dictates how fast stepper motor will run

            # Set coil winding to low
            GPIO.output(STEP,GPIO.LOW)
            sleep(.001 / speed_mod) # Dictates how fast stepper motor will run

            # Update coordinate
            x_coord += increment
            f.write(str(x_coord) + "\n")
            f.seek(0)

            # Check limit switch actuation
            if GPIO.input(motor1_switch) == 0 and increment < 0:
                motor_flag += 1
            else:
                motor_flag = 0

            # Stop x motors if limit switch was activated 5 times in a row or more
            if motor_flag >= 5:
                f.close()
                with open(file_name, "w") as f:
                    f.write(str(x_coord) + "\n")
                break
        print("x: " + str(x_coord))
        GPIO.cleanup()

    # Once finished clean everything up
    except KeyboardInterrupt:
        print("cleanup")
        f.close()
        GPIO.cleanup()


def main():
    num_args = len(sys.argv)
    if num_args == 2:
        xMoveCoord(float(sys.argv[1]))
    elif num_args == 3:
        xMoveCoord(float(sys.argv[1]), float(sys.argv[2]))
    else:
        xMoveCoord()
    
if __name__ == '__main__':
    main()