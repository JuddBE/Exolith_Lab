import RPi.GPIO as GPIO
import time
from datetime import date, datetime
from GPS import GPS_Data
from Logging import logger
import axisReset
from sensorGroup import sensor_group
import os
from dotenv import load_dotenv
from elevationTracking import elevation_tracker
# from azimuthTracking import azimuth_tracker
from trackingNew import tracker
import multiprocessing as mp

load_dotenv()
logger = logger()
elevation_tracker = elevation_tracker()
tracker = tracker()
gps = GPS_Data()


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


def sensorGroupCheck():
    sg = sensor_group()
    light_sensor_status = False
    orientation_sensor_status = False

    try:
        light_sensor_status = sg.light_sensor_health()
        orientation_sensor_status = sg.orientation_sensor_health()

    except Exception as e:
        logger.logInfo("Sensor Group Failure: {}".format(e))

    if light_sensor_status and orientation_sensor_status:
        logger.logInfo("Sensor Group Healthy")
        return True

    else:
        logger.logInfo(
            "Sensor Group Failure: light_sensor_status: {} \norientation_sensor_status: {}".format(
                light_sensor_status, orientation_sensor_status
            )
        )
        return False


def solarElevationLogic():
    if(os.getenv("useGPS") == "True"):
        gps_dict = gps.getCurrentCoordinates()
    else:
        gps_dict = gps.userDefinedCoordinates()
    
    today, year, day, month = gps.getDate()

    now, hour, minutes, seconds = gps.getTime()

    if gps_dict["Longitude Direction"] == "W":
        longitude = -gps_dict["Longitude"]
    else:
        longitude = gps_dict["Longitude"]

    location = (gps_dict["Lattitude"], longitude) 
    when = (year, month, day, int(hour), int(minutes), int(seconds), 0)

    azimuth, elevation = elevation_tracker.sunpos(when, location, True)

    logger.logInfo("Current UTC: {}".format(now))

    status = elevation_tracker.solarElevationPositioning(elevation)

    return status


def azimuthLogic():
    try:
        # tracker.stepMovement(1, int(os.getenv("AZIMUTH_Steps")))
        tracker.tracking()
        return True

    except Exception as e:
        logger.logInfo("Azimuth Logic Failure {}".format(e))
        return False


def solarTracking():
    logger.logInfo("Solar Tracking......")
    try:
        while True:
            tracker.tracking()
            time.sleep(1)

    except KeyboardInterrupt:
        logger.logInfo("Tracking Terminated")
        

def main():
    azimuth_status = True  # change to false
    sensorStatus = False

    os.chdir("/home/pi/Exolith_Lab/Mark_IV/Sintering")
    logger.logInfo("Step 1: Checking sensor health")

    # Need to add fail flag to prevent endless loop on failure
    while not sensorStatus:
        sensorStatus = sensorGroupCheck()

    if sensorStatus:
        logger.logInfo("Step 2: Solar Elevation Logic, Solar Azimuth Logic")

        solar_elevation_status = solarElevationLogic()
        azimuth_status = azimuthLogic()

        if solar_elevation_status:
            pass

        else:
            logger.logInfo(
                "Solar Elevation Status Failure: {}".format(solar_elevation_status)
            )

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
