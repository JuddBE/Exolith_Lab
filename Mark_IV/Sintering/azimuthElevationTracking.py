import RPi.GPIO as GPIO
from time import sleep
from Logging import logger
from dotenv import load_dotenv
from cv_tracking import find_correction
from picamera import PiCamera
import os 

# Load environment variables from .env file
load_dotenv()

azVal = None

class tracker:
    def __init__(self):
        self.logger = logger()
        self.maxVal = 200
 
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

        camera = PiCamera()
        camera.start_preview()
        sleep(3.0)

        try:
            self.logger.logInfo("Adjusting....")

            for x in range(steps):
                pic_info = find_correction(camera)
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
            camera.stop_preview()
            camera.close()

        # Once finished clean everything up
        except Exception as e:
            self.logger.logInfo("Step Movement Exception: " + str(e))
            GPIO.cleanup()
            camera.stop_preview()
            camera.close()

    def azimuthPositioning(self):
        self.tracking(0)
        return True

    def tracking(self, az_direction=1, firstTime=True):
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

        camera = PiCamera()
        camera.start_preview()
        sleep(3.0)

        try:
            while True:
                self.logger.logInfo("Azimuth Adjustment...")
                
                pic_info = find_correction(camera)
                az_dir = pic_info[0]
                elev_dir = pic_info[1]
                bright_val = pic_info[2]
                
                # Set the initial azimuth and elevation movement step numbers.
                # When the sun is not in frame, move for these number of steps.
                min_az_steps = 25
                min_elev_steps = 5
                max_az_steps = 1200
                max_elev_steps = 40
                az_steps = max_az_steps
                elev_steps = max_elev_steps

                if bright_val >= self.maxVal:
                    self.logger.logInfo("Sun in frame...")

                    # Set number of azimuth and elevations steps to take.
                    # Take more movement steps the farther from the middle of the pic the sun is located.
                    az_steps = int(round(pic_info[3] * 3, 0))
                    elev_steps = int(round(pic_info[4] / 4, 0))
                    if az_steps < min_az_steps: az_steps = min_az_steps
                    elif az_steps > max_az_steps: az_steps = max_az_steps
                    if elev_steps < min_elev_steps: elev_steps = min_elev_steps
                    elif elev_steps > max_elev_steps: elev_steps = max_elev_steps

                    # Detemine direction of azimuth and elevation motors.
                    run = True
                    # Set the azimuth direction.
                    if az_dir == "right":
                        GPIO.output(DIR_1, 1)
                    elif az_dir == "left":
                        GPIO.output(DIR_1, 0)
                    else:
                        run = False

                    # Get elevation direction and move.
                    if elev_dir == "up":
                        run = True
                        GPIO.output(DIR, 0)
                    elif elev_dir == "down":
                        run = True
                        GPIO.output(DIR, 1)
                        
                    # If neither azimuth or elevation needed to move, exit since it found the sun.
                    if not run:
                        break
                    
                    if elev_dir != "stay":
                        for x in range(elev_steps):
                            GPIO.output(STEP, GPIO.HIGH)
                            sleep(0.15)  # Dictates how fast stepper motor will run
                            GPIO.output(STEP, GPIO.LOW)
                elif not firstTime:
                    break
                
                # Move azimuth as long as the sun is not in the middle of the image.
                if az_dir != "stay" :
                    for _ in range(az_steps):
                        GPIO.output(STEP_1, GPIO.HIGH)
                        # .5 == super slow
                        # .00005 == breaking
                        sleep(0.0011)
                        GPIO.output(STEP_1, GPIO.LOW)
                        sleep(0.0011)
                sleep(0.5)
            camera.stop_preview()
            camera.close()

        # Once finished clean everything up
        except Exception as e:
            self.logger.logInfo("Exception in track: {}".format(e))
            GPIO.cleanup()
            camera.stop_preview()
            camera.close()
            
def main():
    at = tracker()
    # at.stepMovement(1, 100)
    at.tracking()

if __name__ == "__main__":
    main()