import RPi.GPIO as GPIO
from time import sleep
from Limit_Switches import limitSwitches
import time
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

'''
Moves both motor 1 and motor 2 of the Y axis. Currently CW || 0 moves the y axis forward
'''

ls = limitSwitches()

def yMove(distance=10, clockwise=True, speed_mod=0.6, pause=True):
    GPIO.setwarnings(False)

    if speed_mod > 1:
        print("Speed mod too large, set to 1")
        speed_mod = 1

    if(speed_mod < 0.001):
        return
    
    if distance == 0:
        return

    # Direction pin from controller
    DIR = int(os.getenv("MOTOR_Y_Direction")) #DIR+
    STEP = int(os.getenv("MOTOR_Y_Pulse")) #PULL+
    pixMin = float(os.getenv("pixMin"))
    useGPS = os.getenv("useGPS")

    # Max y coordinate in cm
    Y_MAX = 20

    # 0/1 used to signify clockwise or counterclockwise.
    CW = 0
    CCW = 1
    motor_flag = 0
    y_coord = 0.0
    pixVal = 255
    manual_pause = False
    file_name = "./txtfiles/y_coord.txt"
    brightness_file_name = "./txtfiles/brightness_val.txt"
    manual_pause_file_name = "./txtfiles/manual_pause.txt"
    os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")

    # Based on distance traveled each step of the motor along the threaded rod.
    increment = 0.000635

    # Setup y limit switches
    GPIO.setmode(GPIO.BCM)
    motor1_switch = int(os.getenv("limitSwitchY_1"))
    motor2_switch = int(os.getenv("limitSwitchY_2"))
    GPIO.setup(motor1_switch,GPIO.IN,pull_up_down=GPIO.PUD_UP)    
    GPIO.setup(motor2_switch,GPIO.IN,pull_up_down=GPIO.PUD_UP)

    # Establish Pins in software
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)

    # Set the first direction you want it to spin
    if clockwise == True:
        GPIO.output(DIR, CW)
    else:
        GPIO.output(DIR, CCW)
        increment *= -1

    try:
        # Read y coordinate if file exists, otherwise make the file
        if(os.path.exists(file_name)) and os.stat(file_name).st_size != 0:
            with open(file_name, "r") as f:
                y_coord = float(f.readline())
        else:
            with open(file_name, "w") as f:
                f.write("0\n")

        # Check if the print has been manually paused by the app
        if(os.path.exists(manual_pause_file_name)) and os.stat(manual_pause_file_name).st_size != 0:
            with open(manual_pause_file_name, "r") as f:
                manual_pause = float(f.readline())
                if manual_pause == "1":
                    manual_pause = True
        else:
            with open(manual_pause_file_name, "w") as f:
                f.write("0\n")

        # Calculate number of steps to move desired distance
        num_steps = int(round(distance / 0.000635, 0))
        
        # Start updating y coordinate from the current coordinate
        f = open(file_name, "w")
        f.write(str(y_coord) + "\n")
        f.seek(0)
        brightness_file = open(brightness_file_name, "r+")
        manual_pause_file = open(manual_pause_file_name, "r+")

        # Move y motors step by step
        for x in range(num_steps):
            # Update pause variable
            manual_pause = manual_pause_file.readline()
            if manual_pause == "1":
                manual_pause = True
            else:
                # If manual pause changes from True to False, check for new brightness val.
                if manual_pause:
                    pixVal = brightness_file.readline()
                    if pixVal != "":
                        pixVal = float(pixVal)
                    else:
                        pixVal = pixMin
                    brightness_file.seek(0)
                manual_pause = False
            manual_pause_file.seek(0)

            # Check if the stand should pause when sun is not detected
            if (pause and useGPS == "True") or manual_pause:
                # Only check if x movement should pause every 50 motor steps
                if x % 50 == 0:
                    brightness_file.seek(0)
                    pixVal = brightness_file.readline()
                    if pixVal != "":
                        pixVal = float(pixVal)
                    else:
                        pixVal = pixMin
                    brightness_file.seek(0)

                # Enter pausing loop until the brightness value passes a certain threshold
                # or until the manual pause is disabled
                while (pixVal < pixMin and useGPS == "True" and pause) or manual_pause:
                    time.sleep(0.01)
                    pixVal = brightness_file.readline()
                    manual_pause = manual_pause_file.readline()
                    if pixVal != "":
                        pixVal = float(pixVal)
                    else:
                        pixVal = 0
                    if manual_pause == "1":
                        manual_pause = True
                    else:
                        manual_pause = False
                    manual_pause_file.seek(0)
                    brightness_file.seek(0)
                    
            if y_coord + increment > Y_MAX and clockwise:
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
            y_coord += increment
            f.write(str(y_coord) + "\n")
            f.seek(0)

            # Check limit switch actuation
            if (GPIO.input(motor2_switch) == 0 or GPIO.input(motor1_switch) == 0) and clockwise == False:
                motor_flag += 1
            else:
                motor_flag = 0

            # Stop y motors if limit switch was activated 5 times in a row or more
            if motor_flag >= 5:
                y_coord = 0.0
                f.close()
                with open(file_name, "w") as f:
                    f.write(str(y_coord) + "\n")
                break
        f.close()
        print("y: " + str(y_coord))
        GPIO.cleanup()

    # Once finished clean everything up
    except KeyboardInterrupt:
        print("cleanup")
        f.close()
        GPIO.cleanup()


def main():
    num_args = len(sys.argv)
    if num_args == 2:
        yMove(float(sys.argv[1]))
    elif num_args == 3:
        yMove(float(sys.argv[1]), bool(int(sys.argv[2])))
    elif num_args == 4:
        yMove(float(sys.argv[1]), bool(sys.argv[2]), float(sys.argv[3]))
    else:
        yMove()

if __name__ == '__main__':
    main()