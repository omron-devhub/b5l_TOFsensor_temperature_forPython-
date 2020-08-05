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

import serial
import time as TM
import os
import datetime
import platform as PF
import serial.tools.list_ports

TIMEOUT_s = 5    # timeout setting in second from beginning to end of reception  

#=======================
# TOF Seiral class
#=======================
class tof_serial():

    start_time = 0  # Transmission / reception start time 

    usb_device = ""

    ser = 0
    receive_buffer = 16384
    send_command_no = "00"

    all_data_len = 0            # Received data length 
    all_data = ""
    data_len_val_in_frame = 0   # Data length value in frame

    #------------
    # Constructor
    #------------
    def __init__(self):

        valuelist = []
        comlist = serial.tools.list_ports.comports()
        for element in comlist:
            if(element.pid == 202 and element.vid == 1424):
                 valuelist.append(element.device)
        if(len(valuelist) > 0):
            self.usb_device = valuelist[0]
            #print valuelist
        else:
            self.usb_device = ""
                   
        self.ser = serial.Serial(self.usb_device, timeout=0.01)

    #------------
    # Destructor
    #------------
    def __del__(self):
        self.ser.close()

    #-------------------------------------------------------
    # Transmission process
    #   input:  send_cmd command data to send 
    #   return: none
    #-------------------------------------------------------
    def send_command(self, send_cmd):
        # Transmission Time
        self.start_time = TM.time()
        self.ser.write(send_cmd.replace("-", "").decode("hex"))
        self.send_command_no = send_cmd[3:5]        
 
    #-------------------------------------------------------
    # Reception process
    #   input:  none
    #   return: result  0: Receive Success     
    #                   -1: Received other than result 0x00
    #                   -2: Received data whose first data is not 0xFE  
    #                   -10: Timeout from data send (data missing)
    #                   -11: Timeout from receive begin (data missing)
    #                   -12: Received data whose data number more than data_len_val_in_frame
    #-------------------------------------------------------
    def receive_command(self,no_data_timeout_s):
        response_header = ""
        data_legth = ""
        response_data = ""
        result = 0
        first_receive_flag = True
        receive_begin_time = 0

        # First 6 bytes
        while True:
            val = self.ser.read()   # receive one byte
            if  (len(val) != 0):
                if first_receive_flag == True:
                    receive_begin_time = TM.time()

                response_header = response_header + val
                val = str(hex(ord(val))).replace("0x", "").rjust(2, "0")
                data_legth = data_legth + val
                if (len(response_header) == 6):
                    #print "Header data reception completed!"
                    if hex(ord(response_header[0])).replace("0x", "").rjust(2, "0") != "fe" :
                        print ">>>> First heeader data is not 0xfe!"
                        self.all_data = response_header
                        self.all_data_length = 6
                        result = -2         # Abnormal Header
                        return result
                    elif hex(ord(response_header[1])) .replace("0x","").rjust(2, "0") != "00":
                        print ">>>> Responce is not 0x00!"
                        result = -1         # Return result is not normal
                    break
                else:   # Timeout from receive begin
                    if TM.time() - receive_begin_time > TIMEOUT_s:
                        print ">>>> Timeout from receive begin."
                        self.all_data = response_header
                        self.all_data_length = 12
                        result = -11 
                        return result
            else:
                # Timeout from data send 
                if self.time_outpt() > no_data_timeout_s:
                    print ">>>> No data received from data send"
                    self.all_data = ""
                    self.all_data_length = 0
                    result = -10 
                    return result

        # Parameter part
        data_legth = "0x" + data_legth[4:]
        self.data_len_val_in_frame = int(data_legth, 0)
        #print "Data Length :" + str(data_legth)
        if (self.data_len_val_in_frame != 0):
            while True:
                val = self.ser.read(self.receive_buffer)
                response_data = response_data + val
                if (len(response_data) == self.data_len_val_in_frame):
                    #print "All data received!"
                    break
                elif (self.data_len_val_in_frame < len(response_data)):
                    print ">>>> All data received. But some more data received too."
                    result = -12
                    break
                else:
                    if TM.time() - receive_begin_time   > TIMEOUT_s:
                        print ">>>> Timeout from receive begin."
                        result = -11 
                        break

        # These two values are used in main program
        self.all_data = response_header + response_data
        self.all_data_length = self.data_len_val_in_frame + 6

        return result                 
 
    #-------------------------------------------------------
    # Clear receive data buffer
    #   input:  none
    #   return: line    mode
    #-------------------------------------------------------
    def receive_garbage_command(self):
        line = ""
        time_before = TM.time()
        while True:
            self.ser.write("FE-87-00-00".replace("-", "").decode("hex"))
            line = self.ser.read(self.receive_buffer)
            #print len(line)
            if (len(line) == 6 or len(line) == 7):
                print ">>>> Clear receive data buffer!"
                break
            if TM.time() - time_before > 10:            
                print ">>>> Clear buffer failed!"
                line = ""                       # Clear receive buffer failed
                break

        return line

    #-------------------------------------------------------
    # Shaping log data to display
    #   input:  is_full_output  Display Full log or not
    #   return: receive_data    Received data (format for display)
    #-------------------------------------------------------
    def log_shape(self, is_full_output):
        receive_data = ""
        disp_data_length = 0

        omit_mark = ""

        # Display log data
        if (is_full_output == False and 16 < self.all_data_length):
            disp_data_length = 16               # Display only the beginning of data
            omit_mark = "..."
        else:
            disp_data_length = self.all_data_length

        for i in range(0, disp_data_length):    # Change data format to display
            val = self.all_data[i:i + 1]        
            val = str(hex(ord(val))).replace("0x", "").rjust(2, "0").upper()
            receive_data = receive_data + val + "-"
        
        receive_data = receive_data.rstrip("-")

        receive_data = receive_data + " " + omit_mark

        return receive_data                     # Received data (format for display)
    
    #-------------------------------------------------------
    # Display time from transmisson to receive
    #   input:  none
    #   return: elapsed_time    Time from send to receive
    #-------------------------------------------------------
    def time_outpt(self):
        elapsed_time = TM.time() - self.start_time
        return elapsed_time
        
    #-------------------------------------------------------
    # get data length in received frame data
    #   input:  none
    #   return: data length (int)
    #-------------------------------------------------------
    def get_datalen_in_rcv_frame(self):
        return self.data_len_val_in_frame
