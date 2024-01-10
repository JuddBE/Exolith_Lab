import RPi.GPIO as GPIO
from time import sleep
from Logging import logger
from dotenv import load_dotenv
from cv_tracking import find_correction
import os 

# Load environment variables from .env file
load_dotenv()

azVal = None

class azimuth_tracker:
    def __init__(self):
        self.logger = logger()
        self.maxVal = 254
 
    def stepMovement(self, direction, steps):
        GPIO.setwarnings(False)
        GPIO.cleanup()

        DIR_1 = int(os.getenv("AZIMUTH_Direction"))  # DIR+
        STEP_1 = int(os.getenv("AZIMUTH_Pulse"))  # PULL+

        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(DIR_1, GPIO.OUT)
        GPIO.setup(STEP_1, GPIO.OUT)

        # Set the first direction you want it to spin
        GPIO.output(DIR_1, direction)

        try:
            self.logger.logInfo("Adjusting....")

            for x in range(steps):
                pic_info = find_correction()
                bright_val = pic_info[2]

                if bright_val >= self.maxVal and pic_info[0] == "stay":
                    break
                
                # About 0.5 degrees each 70 motor steps.
                # 1-50 gear ratio.
                # Moves about 1 degree every 2.75 seconds.
                # 16-17 mins to do 360 degree scan.
                for i in range(40):
                    GPIO.output(STEP_1, GPIO.HIGH)
                    # .5 == super slow
                    # .00005 == breaking
                    sleep(0.001)
                    GPIO.output(STEP_1, GPIO.LOW)
                    sleep(0.001)
                
                sleep(0.3)

        # Once finished clean everything up
        except Exception as e:
            self.logger.logInfo("Step Movement Exception: " + str(e))
            GPIO.cleanup()

    def azimuthPositioning(self):
        self.tracking(0)
        return True

    def tracking(self, az_direction=0):
        os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")
        GPIO.setwarnings(False)
        GPIO.cleanup()

        # Pins for azimuth
        DIR_1 = int(os.getenv("AZIMUTH_Direction"))  # DIR+
        STEP_1 = int(os.getenv("AZIMUTH_Pulse"))  # PULL+
 
        # Pins for elevation
        DIR = int(os.getenv("ELAVATION_Direction"))
        STEP = int(os.getenv("ELAVATION_Pulse"))

        # Setup pin layout on PI for azimuth
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DIR_1, GPIO.OUT)
        GPIO.setup(STEP_1, GPIO.OUT)

        # Setup pin layout on RPI for elevation
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)

        # Set the first direction you want it to spin
        # 0/1 used to signify clockwise or counterclockwise.
        GPIO.output(DIR_1, az_direction)

        try:
            while True:
                self.logger.logInfo("Azimuth Adjustment...")
                
                pic_info = find_correction()
                bright_val = pic_info[2]
                
                # Set the initial azimuth and elevation movement step numbers.
                # When the sun is not in frame, move for these number of steps.
                max_az_steps = 300
                max_elev_steps = 18
                az_steps = max_az_steps
                elev_steps = max_elev_steps

                if bright_val >= self.maxVal:
                    self.logger.logInfo("Sun in frame, adjusting...")

                    # Set number of azimuth and elevations steps to take.
                    # Take more movement steps the farther from the middle of the pic the sun is located.
                    az_steps = round(pic_info[3], 0)
                    elev_steps = round(pic_info[4] / 20, 0)
                    if az_steps < 30: az_steps = 30
                    elif az_steps > max_az_steps: az_steps = max_az_steps
                    if elev_steps < 4: elev_steps = 4
                    elif elev_steps > max_elev_steps: elev_steps = max_elev_steps

                    # Detemine direction of azimuth and elevation motors.
                    az_dir = pic_info[0]
                    elev_dir = pic_info[1]
                    run = True
                    # Set the azimuth direction.
                    if az_dir == "right":
                        GPIO.output(DIR_1, 0)
                    elif az_dir == "left":
                        GPIO.output(DIR_1, 1)
                    else:
                        run = False

                    # Get elevation direction and move.
                    if elev_dir == "up":
                        run = True
                        GPIO.output(DIR, 1)
                    elif elev_dir == "down":
                        run = True
                        GPIO.output(DIR, 0)
                        
                    # If neither azimuth or elevation needed to move, exit since it found the sun.
                    if not run:
                        return
                    
                    if elev_dir != "stay":
                        for x in range(elev_steps):
                            GPIO.output(STEP, GPIO.HIGH)
                            sleep(0.05)  # Dictates how fast stepper motor will run
                            GPIO.output(STEP, GPIO.LOW)
                
                # Move azimuth as long as the sun is not in the middle of the image.
                if az_dir != "stay":
                    for _ in range(az_steps):
                        GPIO.output(STEP_1, GPIO.HIGH)
                        # .5 == super slow
                        # .00005 == breaking
                        sleep(0.001)
                        GPIO.output(STEP_1, GPIO.LOW)
                        sleep(0.001)

        # Once finished clean everything up
        except Exception as e:
            self.logger.logInfo("Exception in track: {}".format(e))
            GPIO.cleanup()

    # def tracking(self):
    #     os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")
    #     while True:
    #         pic_info = find_correction()
    #         if pic_info[0] == "stay" and pic_info[2] >= self.maxVal:
    #             self.logger.logInfo("Azimuth adjustment reached...")
    #             sleep(1)

    #         else:
    #             self.logger.logInfo("Azimuth adjustment required...")
    #             GPIO.setwarnings(False)
    #             GPIO.cleanup()

    #             DIR_1 = int(os.getenv("AZIMUTH_Direction"))  # DIR+
    #             STEP_1 = int(os.getenv("AZIMUTH_Pulse"))  # PULL+

    #             direction = 0  # 0/1 used to signify clockwise or counterclockwise.
                
    #             steps = 5  # small increment of search

    #             # Setup pin layout on PI
    #             GPIO.setmode(GPIO.BCM)

    #             # Establish Pins in software
    #             GPIO.setup(DIR_1, GPIO.OUT)
    #             GPIO.setup(STEP_1, GPIO.OUT)

    #             try:

    #                 for x in range(steps):
    #                     self.logger.logInfo("Adjusting azimuth....")

    #                     # Get movements from image taken by camera.
    #                     pic_info = find_correction()
    #                     az_dir = pic_info[0]

    #                     # If the sun is in the middle of the image, azimuth is correct.
    #                     # 0/1 used to signify clockwise or counterclockwise.
    #                     if az_dir == "right":
    #                         direction = 0
    #                     elif az_dir == "left":
    #                         direction = 1
    #                     else:
    #                         self.logger.logInfo("Azimuth Adjusted")
    #                         sleep(1)
    #                         break
                        
    #                     # Set the first direction you want it to spin
    #                     GPIO.output(DIR_1, direction)

    #                     # Turn azimuth.
    #                     for _ in range(40):
    #                         GPIO.output(STEP_1, GPIO.HIGH)
    #                         # .5 == super slow
    #                         # .00005 == breaking
    #                         sleep(0.001)
    #                         GPIO.output(STEP_1, GPIO.LOW)
    #                         sleep(0.001)

    #             # Once finished clean everything up
    #             except Exception as e:
    #                 self.logger.logInfo("Tracking Exception: {}".format(e))
    #                 GPIO.cleanup()

    #         if pic_info[1] == "stay" and pic_info[2] >= self.maxVal:
    #             self.logger.logInfo("Elevation adjustment reached...")
    #             sleep(1)

    #         else:
    #             self.logger.logInfo("Elevation adjustment required...")
    #             GPIO.setwarnings(False)
    #             GPIO.cleanup()

    #             DIR_1 = int(os.getenv("ELAVATION_Direction"))
    #             STEP_1 = int(os.getenv("ELAVATION_Pulse"))

    #             direction = 0  # 0/1 used to signify clockwise or counterclockwise.
                
    #             steps = 5  # small increment of search

    #             # Setup pin layout on PI
    #             GPIO.setmode(GPIO.BCM)

    #             # Establish Pins in software
    #             GPIO.setup(DIR_1, GPIO.OUT)
    #             GPIO.setup(STEP_1, GPIO.OUT)

    #             try:

    #                 for x in range(steps):
    #                     self.logger.logInfo("Adjusting elevation....")

    #                     # Get movements from image taken by camera.
    #                     pic_info = find_correction()
    #                     elev_dir = pic_info[0]

    #                     # If the sun is in the middle of the image, azimuth is correct.
    #                     # 0/1 used to signify clockwise or counterclockwise.
    #                     if elev_dir == "down":
    #                         direction = 0
    #                     elif elev_dir == "up":
    #                         direction = 1
    #                     else:
    #                         self.logger.logInfo("Elevation Adjusted")
    #                         sleep(1)
    #                         break
                        
    #                     # Set the first direction you want it to spin
    #                     GPIO.output(DIR_1, direction)

    #                     # Move elevation.
    #                     for _ in range(4):
    #                         GPIO.output(STEP_1, GPIO.HIGH)
    #                         # .5 == super slow
    #                         # .00005 == breaking
    #                         sleep(0.05)
    #                         GPIO.output(STEP_1, GPIO.LOW)
    #                         sleep(0.05)

    #             # Once finished clean everything up
    #             except Exception as e:
    #                 self.logger.logInfo("Tracking Exception: {}".format(e))
    #                 GPIO.cleanup()
            

def main():
    at = azimuth_tracker()
    at.stepMovement(1, 100)

if __name__ == "__main__":
    main()