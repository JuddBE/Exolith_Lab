import RPi.GPIO as GPIO
from time import sleep
from Limit_Switches import limitSwitches
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

"""
Moves motor for Z axis a specified distance, direction, and speed.
"""

ls = limitSwitches()

def zMove(distance=0.35, down=True, speed_mod=0.3):
    GPIO.setwarnings(False)

    if speed_mod > 0.5:
        print("Speed modifier above 0.5 , z motor cannot go above max speed.")
        exit()

    if speed_mod < 0.001:
        return
    
    if distance == 0:
        return
    
    if distance < 0:
        distance = abs(distance)
        down = False

    # Direction pin from controller
    DIR = int(os.getenv("MOTOR_Z_Direction"))  # DIR+
    STEP = int(os.getenv("MOTOR_Z_Pulse"))  # PULL+

    # 0/1 used to signify clockwise or counterclockwise.
    CW = 0
    CCW = 1
    Z_MAX = 10.6
    motor_flag_top = 0
    z_coord = 0.0
    z_file_name = "./txtfiles/z_coord.txt"
    os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")

    # Based on distance traveled each step of the motor along the threaded rod.
    increment = 0.001

    # Setup z limit switch
    GPIO.setmode(GPIO.BCM)
    motor1_switch = int(os.getenv("limitSwitchZ_1"))
    GPIO.setup(motor1_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Establish Pins in software
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)

    # Set the first direction you want it to spin
    if down == True:
        GPIO.output(DIR, CCW)
    else:
        GPIO.output(DIR, CW)
        increment *= -1

    try:
        # Read z coordinate if file exists, otherwise make the file
        if(os.path.exists(z_file_name)) and os.stat(z_file_name).st_size != 0:
            with open(z_file_name, "r") as f:
                z_coord = float(f.readline())
        else:
            with open(z_file_name, "w") as f:
                f.write("0\n")

        # Calculate number of steps to move desired distance
        num_steps = int(round(distance / abs(increment), 0))
        
        # Start updating z coordinate from the current coordinate
        f = open(z_file_name, "w")

        # Move z motors step by step
        for x in range(num_steps):
            # No need to pause z axis since stand will never sinter while this axis moves

            if z_coord + increment > Z_MAX:
                print("Y Coordinate out of bounds")
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
            z_coord += increment
            f.write(str(z_coord) + "\n")
            f.seek(0)

            # Check limit switch actuation
            if GPIO.input(motor1_switch) == 0 and not down:
                motor_flag_top += 1
            else:
                motor_flag_top = 0

            # Stop z motors if limit switch was activated 5 times in a row or more
            if motor_flag_top >= 5:
                z_coord = 0
                f.close()
                with open(z_file_name, "w") as f:
                    f.write(str(z_coord) + "\n")
                break
        f.close()
        print("z: " + str(z_coord))
        GPIO.cleanup()

    # Once finished clean everything up
    except KeyboardInterrupt:
        print("cleanup")
        f.close()
        GPIO.cleanup()


def main():
    num_args = len(sys.argv)
    if num_args == 2:
        zMove(float(sys.argv[1]))
    elif num_args == 3:
        zMove(float(sys.argv[1]), bool(int(sys.argv[2])))
    elif num_args == 4:
        zMove(float(sys.argv[1]), bool(sys.argv[2]), float(sys.argv[3]))
    else:
        zMove()
    
if __name__ == '__main__':
    main()