import RPi.GPIO as GPIO
import time
# from GPS import GPS_Data
from Logging import logger
import axisReset
from sensorGroup import sensor_group
import os
from dotenv import load_dotenv
from elevationTracking import elevation_tracker
from azimuthElevationTracking import tracker

load_dotenv()
logger = logger()
elevation_tracker = elevation_tracker()
tracker = tracker()

# Not needed unless date is used again in the future
# gps = GPS_Data()

# Reset lens elevation, azimuth does not need resetting
def axisResets():
    ar = axisReset.axis_reset()
    ev_status = False

    try:
        ev_status = ar.elevation_reset()

    except Exception as e:
        logger.logInfo("Axis Reset Failure: {}".format(e))

    if ev_status:
        logger.logInfo("Successful reset")
        return True

    else:
        logger.logInfo("Axis Reset Failure")
        logger.logInfo(
            "ev_status: {}".format(
                ev_status
            )
        )
        return False

# Checks that orientation sensor (and any others that may be added) are connected properly.
def sensorGroupCheck():
    sg = sensor_group()
    orientation_sensor_status = False

    try:
        orientation_sensor_status = sg.orientation_sensor_health()

    except Exception as e:
        logger.logInfo("Sensor Group Failure: {}".format(e))

    if orientation_sensor_status:
        logger.logInfo("Sensor Group Healthy")
        return True

    else:
        logger.logInfo(
            "Sensor Group Failure: orientation_sensor_status: {}".format(
                orientation_sensor_status
            )
        )
        return False

# Set initial elevation angle
def solarElevationLogic():
    # Commented code relies on current date, and the pi requires wifi to update its current date and time.
    # if(os.getenv("useGPS") == "True"):
    #     gps_dict = gps.getCurrentCoordinates()
    # else:
    #     gps_dict = gps.userDefinedCoordinates()
    # gps_dict = gps.userDefinedCoordinates()
    
    # today, year, day, month = gps.getDate()

    # now, hour, minutes, seconds = gps.getTime()

    # if gps_dict["Longitude Direction"] == "W":
    #     longitude = -gps_dict["Longitude"]
    # else:
    #     longitude = gps_dict["Longitude"]

    # location = (gps_dict["Lattitude"], longitude) 
    # when = (year, month, day, int(hour), int(minutes), int(seconds), 0)

    # azimuth, elevation = elevation_tracker.sunpos(when, location, True)

    # logger.logInfo("Current UTC: {}".format(now))

    # Since clock does not work, set elevation and have it interupt when the sun is in camera's view.
    status = elevation_tracker.solarElevationPositioning(75.0)
    status = True

    return status

# Scan sky until sun is in frame for the first time.
def azimuthLogic():
    try:
        tracker.tracking(firstTime=True)
        return True

    except Exception as e:
        logger.logInfo("Azimuth Logic Failure {}".format(e))
        return False

# After sun is in frame, track it by keeping it in a certain area of the frame.
def solarTracking():
    logger.logInfo("Solar Tracking......")
    try:
        while True:
            tracker.tracking(firstTime=False)
            time.sleep(1)

    except KeyboardInterrupt:
        logger.logInfo("Tracking Terminated")
        
def main():
    azimuth_status = False
    sensorStatus = False

    os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")
    logger.logInfo("Step 1: Checking sensor health")

    # Solar alignment does not start until sensors are responding
    while not sensorStatus:
        sensorStatus = sensorGroupCheck()

    if sensorStatus:
        logger.logInfo("Step 2: Solar Elevation Logic, Solar Azimuth Logic")

        # Set initial elevation
        solar_elevation_status = solarElevationLogic()

        # Scan and find sun for first time
        azimuth_status = azimuthLogic()

        if not solar_elevation_status:
            logger.logInfo(
                "Solar Elevation Status Failure: {}".format(solar_elevation_status)
            )

        # If elevation and azimuth are set and sun is in frame, track it.
        if solar_elevation_status and azimuth_status:
            logger.logInfo("Step 3: Solar Tracking")
            solarTracking()

        else:
            logger.logInfo(
                "Failure: solar_elevation_status: {} \n azimuth_status: {}".format(
                    solar_elevation_status, azimuth_status
                )
            )
    else:
        logger.logInfo(
            "Step 1 Failure: sensorStatus: {}".format(
                sensorStatus
            )
        )


if __name__ == "__main__":
    main()
