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
# define main function to call later in order to keep more variables local rather than have tons of global variables
def HMI_GUI_control():
    # Define constants
    channel_count = 3 #number of EMG channels 
    fs = 500 #samples per second
    epoch_length = 0.200 # seconds in an epoch
    tshld = [0.000014, 0.000085, 0.00003] # Thresholds for Arm, Left Leg, Right Leg
    pyautogui.PAUSE = 0 
    
    com_port = args.com_port #get a com port from the user
    GUI_speed_x = args.speed_x # get speed multipliers from the user
    GUI_speed_y = args.speed_y
    run_duration = args.duration #get the number of seconds from user
    
    # Setup and Calculations for variables based off of constants
    epoch_count = int(run_duration // epoch_length) # Total number of epochs that will happen
    sample_count = int(fs * epoch_length) #number of samples in an epoch
    sample_data = np.empty((int(sample_count),channel_count)) # An array of nans in which each row is a sample and each column is a channel
    
    # Define Mouse movements
    def GUI_rest(): # 'rest'
        print('rest')
        
    def GUI_left():# 'left'
        print('left')
        # move the mouse 40 pixles left relative to its current location instantly
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
        # click the mouse
        pyautogui.click(clicks=1, button='left')
    
    
    def select_case(argument): # Dictionary to Define actions to take given channel_predicted's state
        switcher = {
        # these arrays match the incoming prediced array from the three channels
        # one will be picked if it matches the incoming array (in string format) and will wall the definition which is a function
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
    # at the start of the program, tell the user how long it will run and count down
    print(f'Mouse control will run for {run_duration} seconds')
    time.sleep(3)
    print('Starting...')
    
    #count down
    seconds = 3
    for i in range(3):
        print (seconds)
        seconds -= 1
        time.sleep(1)
    print('...\n')

    # Open serial port
    arduino_data = serial.Serial(port=com_port,baudrate=500000)
    # loop until the determined stop time (counted by epochs)
    for epoch_index in range(epoch_count):
        now = time.time() # start a timer to properly time the loop
        # Reset data with NaNs
        sample_data[:] = np.NaN # make sure the data is empty before each epoch
 
        for sample_index in range(int(sample_count)): # For every sample I expect to receive:
        # there are often problems with reading serial data, so to redice latency, we skip the sample if there's trouble
            try: 
                arduino_string = arduino_data.readline().decode('ascii') # Read the new sample from the serial port
                arduino_list = np.array(arduino_string.split(),dtype=int)  # make it into an array
                sample_data[sample_index] = arduino_list[1:channel_count+1] * 5/1024 # transform the data
            except:
                pass
                # print('Serial Read Error') # used for debugging, for the sake of real time funciton, returning no errors is preferable
        
        # take the variance of the sample_data array
        emg_var =  np.transpose(np.nanvar(sample_data,axis=0)) 
        
        # test if the emg_varience array passes the array of thresholds
        channel_predicted = emg_var > tshld
        
        # find the matching dictionary definition and run the function that is defined
        select_case(channel_predicted)()
        
        # timing helper that kills time if any remains
        elapsed = time.time() - now  # how long was it running?
        try:    
            ## sleep for the remaning time in the epoch
            time.sleep(0.2-elapsed) 
        except:
            # rarely occurs
            print('timing error')
    arduino_data.close()
    
#%% Run code
# get all the required inputs from the user through argparse 
parser = argparse.ArgumentParser(description='Read live data from serial port in order to move the mouse')
parser.add_argument('speed_x', type=float, default = 1.0, help='X axis Multiplier (default is 1.0)')
parser.add_argument('speed_y', type=float, default = 1.0, help='Y axis Multiplier (default is 1.0)')
parser.add_argument('duration', type=float, default = 10, help='duration of mouse control')
parser.add_argument('com_port', type=str, default = '/dev/cu.usbserial-1430', help='Arduino Nano port matching arduino software')

args = parser.parse_args()

# run the main function
HMI_GUI_control()


