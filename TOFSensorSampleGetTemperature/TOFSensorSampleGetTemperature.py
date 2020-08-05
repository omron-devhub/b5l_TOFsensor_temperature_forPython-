# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
# Copyright 2020  OMRON Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------------------------

#----------------------------------------------------
# Environment Ubuntu
#   Ubuntu 18.04.3 LTS
#   pyserial (3.4)
#   Python 2.7.15+ (default, Oct  7 2019, 17:39:04) 
#----------------------------------------------------

#-------------------------------------------------------
# Environment Windows10
#   Windows 10
#   pyserial (3.4)
#   Python 2.7.15 (v2.7.15:ca079a3ea3, Apr 30 2018, 16:22:17) [MSC v.1500 32 bit (Intel)] on win32
#-------------------------------------------------------

import serial
import tof_serial as TS
import time as TM
import datetime

STOP_MEASUREMENT_TEMP_IMAGER_C  = 60.0   # in C degree
START_MEASUREMENT_TEMP_IMAGER_C = 43.0   # in C degree
STOP_MEASUREMENT_TEMP_LED_C     = 40.0   # in C degree
START_MEASUREMENT_TEMP_LED_C    = 38.0   # in C degree

INTERVEL_TIME_S = 10                     # Intervel time from stop measurement in s


CAUSE_NONE      = 0
CAUSE_IMAGER    = 1
CAUSE_LED       = 2

time_starting_point = 0

#-------------------------------------------------------
#  set time starting point
#   input:  none
#   return: timer value of now
#-------------------------------------------------------
def set_time_starting_point():
    time_starting_point = TM.time()
    return time_starting_point

#-------------------------------------------------------
#  get elapsed time from time starting point
#   input:  time starting point
#   return: elapsed time [s]
#-------------------------------------------------------
def get_elapsed_time(time_starting_point):
    elapsed_time = TM.time() - time_starting_point
    return elapsed_time

#-------------------------------------------------------
#  judge if standard time passed
#   input:  time starting_point
#           time_standard
#   return: True: time passed False: not yet passed
#-------------------------------------------------------
def is_time_passed(time_standard,time_starting_point):
    if get_elapsed_time(time_starting_point) > time_standard:
        return True
    else:
        return False 
#-------------------------------------------------------
# get datalength in send flame
#   input: frame data to send(string)
#   return: data length (int)
#-------------------------------------------------------
def get_datalen_in_snd_frame(send_cmd):
    return int("0x" + send_cmd[6:8] + send_cmd[9:11],0)

#-------------------------------------------------------
# main
#   input:  none
#   return: none
#-------------------------------------------------------
def main():

    nodata_timeout = {"80":1.0, "81":1.0, "9B":1.0,"9C":5.0}  # No data received timeout value  
    names_of_command = {"80":"80 : Start Measurement", "81":"81 : Stop Measurement","9B":"9B : Get Imager Temperature","9C":"9C : Get LED Temperature"} 
    measure_tmp_status = 0
    over_temp_cause = CAUSE_NONE

    error_count = 0
    all_count = 0

    print "Enter send command No. and press enter key.:"
    print "80:Start measurement"
    print "81:Stop measurement"
    print "MT:Start measure temperature"
    print "XX:Exit"

    # Input send command
    input_send_cmd_all = raw_input()
    input_send_cmd = input_send_cmd_all[0:2]
    print ""
    print "Command entered:" + (input_send_cmd)
    send_cmd = ""

    input_send_cmd = input_send_cmd[0:2]

    # Command branch 
    if input_send_cmd == "80":
        print "Send 80:Start measurement command"
        send_cmd = "FE-80-00-00"
    if input_send_cmd == "81":
        print "Send 81:Stop measurement command"
        send_cmd = "FE-81-00-00"
    if input_send_cmd == "MT":
        print "MT: Start measure temperature"
        measure_tmp_status = 1
        send_cmd = "FE-9B-00-00"
    if input_send_cmd == "XX":
        print "XX:Exit"
        send_cmd = ""
 
    ser = TS.tof_serial()
    
    while True:
        try:
            # Make send data
            if measure_tmp_status == 0:
                pass                            # Do nothing
            elif measure_tmp_status == 1:
                input_send_cmd = "80"           # start measurement
                send_cmd = "FE-80-00-00"
                time_starting_point = set_time_starting_point()
            elif measure_tmp_status == 2:
                if is_time_passed(time_starting_point,2) == True:   # 2 sec wait
                    input_send_cmd = "9B"      # get Imager temperature
                    send_cmd = "FE-9B-00-00"
                    time_starting_point = set_time_starting_point()
                else:
                    continue
            elif measure_tmp_status == 3:
                if is_time_passed(time_starting_point,1) == True:   # 1 sec wait
                    input_send_cmd = "9C"      # get LED temperature
                    send_cmd = "FE-9C-00-00"
                    time_starting_point = set_time_starting_point()
                else:
                    continue
            elif measure_tmp_status == 4:
                if is_time_passed(time_starting_point,1) == True:   # 1 sec wait
                    input_send_cmd = "9B"      # get Imager temperature
                    send_cmd = "FE-9B-00-00"
                    time_starting_point = set_time_starting_point()
                else:
                    continue

            elif measure_tmp_status == 5:       # When above Stop measurement Temprature
                input_send_cmd = "81"           # stop measurement
                send_cmd = "FE-81-00-00"
                time_starting_point = set_time_starting_point()
            elif measure_tmp_status == 6:       # cooling time wait
                if is_time_passed(time_starting_point,INTERVEL_TIME_S) == True:   # wait cooling time
                    input_send_cmd = "80"       # start measurement
                    send_cmd = "FE-80-00-00"
                    time_starting_point = set_time_starting_point()
                else:
                    continue
            elif measure_tmp_status == 7:
                if is_time_passed(time_starting_point,2) == True:   # 2 sec wait
                    input_send_cmd = "9B"      # get Imager temperature
                    send_cmd = "FE-9B-00-00"
                    time_starting_point = set_time_starting_point()
                else:
                    continue                
            elif measure_tmp_status == 8:
                if is_time_passed(time_starting_point,1) == True:   # 1 sec wait
                    input_send_cmd = "9C"      # get LED temperature
                    send_cmd = "FE-9C-00-00"
                    time_starting_point = set_time_starting_point()
                else:
                    continue
            else:
                print "Invalid status"
                input_send_cmd = "XX"
                break

            time_nodata_timeout = nodata_timeout.get(input_send_cmd)    # No data received timeout value            
            if time_nodata_timeout == None :    # could not find command
                time_nodata_timeout = 10        # 10 s

            # Send and receive
            if send_cmd == "":
                print "No transmission."
            else:
                # Send
                ser.send_command(send_cmd)
                command_name = names_of_command.get(input_send_cmd)    # No data received timeout value            
                if command_name == None :    # could not find command
                    command_name = "Command name error!"
                else:
                    print "<<< "+ command_name +  " >>>"
                snd_len = get_datalen_in_snd_frame(send_cmd)
                print datetime.datetime.now().strftime("%H:%M:%S.%f") + "  " + str(snd_len + 4).zfill(7) + "  Send     " + send_cmd
                
                # Receive
                result = ser.receive_command(time_nodata_timeout)
                rcv_len = ser.get_datalen_in_rcv_frame()
                all_count += 1
                # Receive error
                if result != 0 :
                    error_count += 1
                    print "Receive Error! No." + str(result)
                    print "error / all = " + str(error_count) + " / " + str(all_count)
                    print ""
                    line = ser.receive_garbage_command()
                    continue
                
                # Display received data
                data = ""
                if input_send_cmd == "82" or input_send_cmd == "94":
                    data = ser.log_shape(False)
                else:
                    data = ser.log_shape(True)
                #print "Receive data:" + data
                print datetime.datetime.now().strftime("%H:%M:%S.%f") + "  " + str(rcv_len + 6).zfill(7) + "  Receive  " + data
                print ""
                print "error / all = " + str(error_count) + " / " + str(all_count)
                print""

                # Display temperature
                if data[3:5] == "00":           # Normal response
                    if input_send_cmd == "9B":  # Imager temperature
                        temp_UL = float(int(data[18:20] + data[21:23],16))/10.0
                        temp_UR = float(int(data[24:26] + data[27:29],16))/10.0
                        temp_LL = float(int(data[30:32] + data[33:35],16))/10.0
                        temp_LR = float(int(data[36:38] + data[39:],16))/10.0

                        print "Imager Temperature"
                        print " Upper Left  : " + str(temp_UL)
                        print " Upper Right : " + str(temp_UR)
                        print " Lower Left  : " + str(temp_LL)
                        print " Lower Right : " + str(temp_LR)
                        if (measure_tmp_status >= 5 and over_temp_cause == CAUSE_IMAGER):
                            print " ( Start Temprature = " + str(START_MEASUREMENT_TEMP_IMAGER_C) +" )"
                        else:
                            print " ( Stop Temprature = " + str(STOP_MEASUREMENT_TEMP_IMAGER_C) +" )"
                        print ""

                    elif input_send_cmd == "9C":  # LED temperature
                        temp_led = float(int(data[18:20] + data[21:],16))/10.0
                        print "LED Temperature : " + str(temp_led)
                        if (measure_tmp_status >= 5 and over_temp_cause == CAUSE_LED):
                            print " ( Start Temprature = " + str(START_MEASUREMENT_TEMP_LED_C) +" )"
                        else:
                            print " ( Stop Temprature = " + str(STOP_MEASUREMENT_TEMP_LED_C) +" )"
                        print ""
                    elif input_send_cmd == "81":
                        print ""
                        print "Now Cooling Interval"
                        print ""
                
                    # Status transition
                    if measure_tmp_status == 0:
                        pass                                    # Do nothing
                    # Normal loop
                    elif measure_tmp_status == 1:               # start measurement
                        measure_tmp_status = 2
                    elif measure_tmp_status == 2:               # get Imager temperature
                        measure_tmp_status = 3
                        if ((STOP_MEASUREMENT_TEMP_IMAGER_C < temp_UL) \
                            or  (STOP_MEASUREMENT_TEMP_IMAGER_C < temp_UR) \
                            or  (STOP_MEASUREMENT_TEMP_IMAGER_C < temp_LL) \
                            or  (STOP_MEASUREMENT_TEMP_IMAGER_C < temp_LR)):
                            measure_tmp_status = 5              # To over heat loop (Stop measurement and wait)
                            over_temp_cause = CAUSE_IMAGER
                        else:
                            measure_tmp_status = 3
                    elif measure_tmp_status == 3:               # get LED temperature
                        if STOP_MEASUREMENT_TEMP_LED_C < temp_led:
                            measure_tmp_status = 5              # To over heat loop (Stop measurement and wait)
                            over_temp_cause = CAUSE_LED
                        else:
                            measure_tmp_status = 4
                    elif measure_tmp_status == 4:               # get Imager temperature
                        if ((STOP_MEASUREMENT_TEMP_IMAGER_C < temp_UL) \
                            or  (STOP_MEASUREMENT_TEMP_IMAGER_C < temp_UR) \
                            or  (STOP_MEASUREMENT_TEMP_IMAGER_C < temp_LL) \
                            or  (STOP_MEASUREMENT_TEMP_IMAGER_C < temp_LR)):
                            measure_tmp_status = 5              # To over heat loop (Stop measurement and wait)
                            over_temp_cause = CAUSE_IMAGER
                        else:
                            measure_tmp_status = 3
                    # higher temp loop
                    elif measure_tmp_status == 5:               # When above Stop measurement Temprature
                        measure_tmp_status = 6
                    elif measure_tmp_status == 6:               # after interval time wait start measurement
                        measure_tmp_status = 7          
                    elif measure_tmp_status == 7:               # get Imager temperature
                        if over_temp_cause == CAUSE_LED:    # when cause of high temp is LED
                            measure_tmp_status = 8          # check LED temperature
                            continue
                        if ((START_MEASUREMENT_TEMP_IMAGER_C < temp_UL) \
                            or  (START_MEASUREMENT_TEMP_IMAGER_C < temp_UR) \
                            or  (START_MEASUREMENT_TEMP_IMAGER_C < temp_LL) \
                            or  (START_MEASUREMENT_TEMP_IMAGER_C < temp_LR)):
                            measure_tmp_status = 5              # Stop measurement and wait
                        else:
                            measure_tmp_status = 4          # To Normal Loop - Get imager temprature 
                            over_temp_cause = CAUSE_NONE            
                    elif measure_tmp_status == 8:               # get LED temperature
                        if START_MEASUREMENT_TEMP_LED_C < temp_led:
                            measure_tmp_status = 5              # Stop measurement and wait
                        else:
                            measure_tmp_status = 3              # To Normal Loop - Get LED temprature
                            over_temp_cause = CAUSE_NONE   
                    else:
                        print "Invalid status"
                        input_send_cmd = "XX"
                        break
                else:
                    pass
            if measure_tmp_status == 0: # Other than Getting TeMperaure (Singl Command)
                input_send_cmd = "XX"
                break
        except KeyboardInterrupt:
            print "Ctrl + C:KeyboardInterrupt"
            input_send_cmd = "XX"
            break

    # Delete buffer and quit
    if input_send_cmd == "XX":
        line = ser.receive_garbage_command()

        if measure_tmp_status != 0:             # Only when MT selected
            input_send_cmd = "81"
            send_cmd = "FE-81-00-00"
            print "Send data:" + send_cmd + " # stop measurement"
            ser.send_command(send_cmd)
            time_nodata_timeout = nodata_timeout.get(input_send_cmd)            
            if time_nodata_timeout == None :    # could not find command
                time_nodata_timeout = 10        # 10 s
        
            result = ser.receive_command(time_nodata_timeout)
            data = ser.log_shape(False)
            print "Receive data:" + data
            print "" 

        print "Finished."


#-------------------------------------------------------
# Execute main
#   input:  none
#   return: none
#-------------------------------------------------------
if __name__ == '__main__':
    main()

