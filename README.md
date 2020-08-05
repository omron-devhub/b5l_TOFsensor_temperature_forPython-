# b5l_TOFsensor_temperature_forPython-

TOF-Sensor Sample code for get temperature.  (for Python)
------------------------------------------------------------

(1) Contents
  This code provides TOF-Sensor Python sample code for get temperature.

  "Get LED Temperature command" and "Get imager Temperature command" can be executed during measurement only.
  Device error(F7h) occurred and measurement will not be able to start, if these commands are executed
  before execution of "Start measurement command."
  (It is necessary to power on the B5L again or reboot B5L by "Software reset command" in such kind of error situation.)

  This sample code is an example of getting temperature during measurement.
  The outline of processing flow is as follows.
  (Refer to source code about detail information.)

    (a) Execute "Start measurement command."
    (b) Execute "Get imager temperature command" and "Get LED temperature command" alternately.
    (c) If the imager temperature is more than "Stop Temperature(imager)" or LED temperature is more than "Stop Temperature(LED)",
        execute "Stop measurement command" (cooling down the B5L)
    (d) After waiting a time specified as "Time Interval", execute "Start measurement command", and then execute "Get imager temperature command",
        "Get LED temperature command."
        If the imager temperature is less than "Start Temperature(imager)" and LED temperature is less than "Start Temperature(LED)", go back to (b).
        Otherwise, execute "Stop measurement command" and then repeat (d).

     * "Stop Temperature(imager)", "Stop Temperature(LED)", "Start Temperature(LED)", "Start Temperature(LED)"
       and "Time Interval" are arbitrary value set in sample code.

(2) File description
  The following files exist in the TOFSensorSampleGetTemperature/ folder.

    TOFSensorSampleGetTemperature.py	Sample code main
    tof_serial.py                       Serial Port send/receive class
    connect_usb0.sh                     Shell script to connect /dev/ttyUSB0(only for Ubuntu18)

(3) Environment for this sample code
  The sample code is coded to run in Python2.7 environment on both Windows10 and Ubuntu18.
  A module named "pyserial" is needed to run this sample code.

(4）Prepare to execute sample code	
	[Setting Stop Temmprature and Start Temperature]
	Change following lines in about 37st line in TOFSensorSampleGetTemperature.py as you need.
	The unit of temperature is Celsius	

	Stop Temperature (Imager)   STOP_MEASUREMENT_TEMP_IMAGER_C  = 55.0
	Start Temperature (Imager)  START_MEASUREMENT_TEMP_IMAGER_C = 53.0
	Stop Temperature (LED)      STOP_MEASUREMENT_TEMP_LED_C     = 50.0
	Start Temperature (LED)     START_MEASUREMENT_TEMP_LED_C    = 48.0
	
	[Setting Intervel Time]
	Interval Time is the time to wait to make TOF cooler.
	Change the Interval Time value "INTERVEL_TIME_S" in about the 42th line as following 
	as you need. 
	The unit is seconds.
	
	INTERVEL_TIME_S = 10                     # Intervel time from stop measurement in s
	
（5）Executing sammple code
	Move to the folder of sample code in command prompt or power shell, 
	and type following line to execute sammple code .

	python TOFSensorSampleGetTemperature.py[Enter]

[NOTES ON USAGE]
* This sample code and documentation are copyrighted property of OMRON Corporation
* This sample code does not guarantee proper operation
* This sample code is distributed in the Apache License 2.0.

----
OMRON Corporation 
Copyright 2020 OMRON Corporation, All Rights Reserved.
