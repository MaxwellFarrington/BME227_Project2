#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 17:03:28 2021

@author: maxwellfarrington
"""

#%% import
import numpy as np
import serial
import time
import pyautogui
import argparse

def HMI_GUI_control():
    # Definitions
    channel_count = 3
    fs = 500 #per second
    epoch_length = 0.200 #seconds
    tshld = [0.00006, 0.00006, 0.00006] #  Arm, Left Leg, Right Leg
    com_port='/dev/cu.usbserial-1430'
    pyautogui.PAUSE = 0
    
    GUI_speed_x = args.speed_x
    GUI_speed_y = args.speed_y
    run_duration = args.duration #number of seconds
    
    # Setup and Calculations
    epoch_count = int(run_duration // epoch_length)
    sample_count = int(fs * epoch_length)
    sample_data = np.empty((int(sample_count),channel_count)) # An array of nans in which each row is a sample and each column is a channel
    
    # Define Mouse movements
    def GUI_rest(): # 'rest'
        print('rest')
        
    def GUI_left():# 'left'
        print('left')
        pyautogui.moveRel(-40 * GUI_speed_x, 0 , duration = 0)
        
    def GUI_right():# 'right'
        print('right')
        pyautogui.moveRel(40 * GUI_speed_x, 0 , duration = 0)
        
    def GUI_up():# 'up'
        print('up')
        pyautogui.moveRel(0, -20 * GUI_speed_y, duration = 0)
        
    def GUI_down():# 'down'
        print('down')
        pyautogui.moveRel(0, 20 * GUI_speed_y, duration = 0)
        
    def GUI_click():# 'click'
        print('click')
        pyautogui.click(clicks=1, button='left')
    
    
    def select_case(argument): # Dictionary to Define actions to take given channel_predicted's state
        switcher = {
        '[False False False]':GUI_rest,
        '[ True False False]':GUI_rest,
        '[False  True  True]':GUI_rest,
        '[False  True False]':GUI_left,
        '[False False  True]':GUI_right,
        '[ True  True False]':GUI_down,
        '[ True False  True]':GUI_up,
        '[ True  True  True]':GUI_click,
        }
        return switcher.get(str(argument), 'not_found')
    print(f'Mouse control will run for {run_duration} seconds')
    time.sleep(3)
    print('Starting...')
    
    seconds = 3
    for i in range(3):
        print (seconds)
        seconds -= 1
        time.sleep(1)
    print('...\n')

    # Open serial port
    arduino_data = serial.Serial(port=com_port,baudrate=500000)
    for epoch_index in range(epoch_count):
        now = time.time()
        # Reset data with NaNs
        sample_data[:] = np.NaN 
 
        
        for sample_index in range(int(sample_count)): # For every sample I expect to receive:
            try:
                arduino_string = arduino_data.readline().decode('ascii') # Read the new sample from the serial port
                arduino_list = np.array(arduino_string.split(),dtype=int)  
                sample_data[sample_index] = arduino_list[1:channel_count+1] * 5/1024
            except:
                pass
                # print('Serial Read Error')  
        emg_var =  np.transpose(np.nanvar(sample_data,axis=0))
        channel_predicted = emg_var > tshld
        
        select_case(channel_predicted)()
        
        elapsed = time.time() - now  # how long was it running?
        try:         
            time.sleep(0.2-elapsed)
        except:
            print('timing error')
    arduino_data.close()
#%% Run code
parser = argparse.ArgumentParser(description='Read live data from serial port in order to move the mouse')
parser.add_argument('speed_x', type=float, default = 1.0, help='X axis Multiplier (default is 1.0)')
parser.add_argument('speed_y', type=float, default = 1.0, help='Y axis Multiplier (default is 1.0)')
parser.add_argument('duration', type=float, default = 10, help='duration of mouse control')

args = parser.parse_args()

HMI_GUI_control()


