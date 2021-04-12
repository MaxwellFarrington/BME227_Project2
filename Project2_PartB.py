# -*- coding: utf-8 -*-

"""
Created on Mon Mar  1 18:22:44 2021

@author: dakot
"""
#%% Import packages

import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
import serial
import argparse
import os
import time


def read_and_plot_serial_data(com_port, recording_duration, n_channels, fs, out_folder, save):
    """
    
    
    Parameters
    ----------
    com_port : str
        COM port that arduino is connected to
    recording_duration : int
        duration (in seconds) of the recording
    n_channels : int
        number of EMG channels that data is collected from
    fs : int
        sampling frequency of the sensors (typically ranges from 1-500 Hz)
    out_folder : str
        name of folder where plots and data will be saved to
    save : str
        promts user to enable saving of outputted plot and data, if user 
        types 'yes' then this information will be saved in the out_folder

    """
    
    
    
    
    # Part A - Initializing an array
    def initialize_arrays(recording_duration,n_channels,fs):
        """
        

        Parameters
        ----------
        recording_duration : int
            duration (in seconds) of the recording
        n_channels : int
            number of EMG channels that data is collected from
        fs : int
            sampling frequency of the sensors (typically ranges from 1-500 Hz)

        Returns
        -------
        sample_data : numpy array
            array contains NaN's where rows are each data point and is
            n_channels wide
        sample_time : numpy array
            array contains estimate timestamps for each data point

        """
  
        period = 1/fs # converting frequency to period
        
        rows = int(recording_duration/period) # number of rows needed
        
        # empty array w/ required number of rows and columns
        sample_data = np.empty([rows, n_channels])
    
        sample_data[:] = np.NaN # array with NaN's
        
        # empty array w/ required number of rows and one column
        sample_time = np.empty([rows, 1]) 
                
        # filling time array with estimated timestamps
        for i in range(rows):
            sample_time[i] = period*(i)
            
        return sample_data, sample_time

 
    # Part B - Plot the array
    # get the number of channels to be plotted
    def initialize_plot(sample_time, sample_data):
        """
        

        Parameters
        ----------
        sample_time : numpy array
            array contains NaN's where rows are each data point and is
            n_channels wide
        sample_data : numpy array
            array contains estimate timestamps for each data point

        Returns
        -------
        plot_list : list
            list of pyplot line objects where there's only one line object
            for each data channel
        ax : pyplot axis object
            axis object that controls axis of figure

        """
        
        channel_count = np.size(sample_data, axis = 1)
        
        # setting up figure 
        plt.figure()
        plt.clf()
        plt.xlabel('Time (sec)')
        plt.ylabel('EMG Amplitude (V)')
        plt.title('Time vs. EMG Amplitude')
        plt.grid()
        ax = plt.axes()
        os.system('cls')
        
        # plotting three channels
        color_list = ['red', 'blue', 'green']
        
        # initializing line objects list
        plot_list = []
        
        # create a line for each channel
        for i in range(channel_count):
            label_string = f'Channel {i+1}'
            new_line =  plt.plot(sample_time, sample_data[:,i], color = color_list[i], linewidth = 2, 
                     label = label_string)
            plot_list.append(new_line)
        return plot_list, ax
            

    # Calling initialization functions  
    
    # Initializing and then saving arrays 
    out = initialize_arrays(recording_duration, n_channels, fs)
    data_array = out[0]
    time_array = out[1]
    
    # Initializing plot and saving lines and axis objects
    out = initialize_plot(time_array, data_array)
    lines_list = out[0]
    ax = out[1]
    
    
    # Choosing an appropriate plotting frequency based on sampling rate
    if(fs<=100):
        x = 15
    elif(fs<=200):
        x = 30
    elif(fs<=300):
        x = 55
    elif(fs<=400):
        x = 80
    else:
        x = 100        
    
    
    print('Data collection will be begin shortly.')
    time.sleep(3) # pauses three seconds
    print('The following tasks will include a combination of left arm, left leg, and right leg movements. ')
    time.sleep(3) # pauses three seconds  
    
    # allows time to pass for user to read statement, then begin countdown
    time.sleep(3)
    seconds = 10
    for i in range(10):
        print (seconds)
        seconds -= 1
        time.sleep(1)
    print('...\n')
     
    
    
    
    # initializing index of action array/list
    action_index = 0
    
    # array of action items for user
    action_array = ['Rest', 'Left', 'Right', 'Down', 'Up', 'Click']
    
    #initializing nan (will be changed to arduino_data)
    nan_data = np.empty([n_channels])
    nan_data = np.NaN
        
    #Part D - Read serial data into the array      
    with serial.Serial(port = com_port, baudrate = 500000) as arduino:        
        
        # # runs for time specified by user for recording_duration
        # t_end = time.time() + recording_duration
        # while time.time() < t_end:

        #start_time = int(nan_data_list[0])/1000
        start_time = 0

        samp_count = int(recording_duration/(1/fs))      
        
        # for each data point get data        
        for samp_index in range(samp_count):
            # time loop starts
            now = time.time()
               
            try:
                # get first data point and save the time
                nan_data = arduino.readline().decode('ascii')
                nan_data_list = nan_data.split()
            except:
                pass
            
            # if data is not complete then get a new datapoint
            while(len(nan_data_list) != 4):
                nan_data = arduino.readline()
                nan_data_list = nan_data.split()
                print('Incomplete Data')
            
            # saving time 
            time_array[samp_index] = (int(nan_data_list[0])/1000)-start_time
            
            # saving correct number of data points, updating data array accordingly
            temp = np.array(nan_data_list[1:n_channels+1]).astype(int)*(5/1024)
            data_array[samp_index] = temp
            
            # updating line objects with new x,y data 
            for chan_index in range(n_channels):
                lines_list[chan_index][0].set_xdata(time_array[0:samp_index+1])
                lines_list[chan_index][0].set_ydata(data_array[:samp_index+1,chan_index])
            
            # speeding up plotting through only plotting every x number of samples
            # allowing real time plotting for higher sampling rates
            if(samp_index % x == 0):
                plt.pause(.001)
                # update axis as more data comes in
                ax.relim()
                ax.autoscale_view()
                plt.legend()
 
            if(samp_index % (12*fs) == 0):
                action_index =  0

            if(samp_index % (2*fs) == 0):
                print(action_array[action_index])
                action_index =  action_index + 1
                
            
                
        
            # elapse_time = time.time() - now
            # try:
            #     time.sleep(1/fs- elapse_time)
            # except:
            #     print ('Timing error') 
                
    # SAVING FUNCTIONS 
            
    # current time, setting up time string       
    now = datetime.now()
    t_string = f'{now.year}-{now.month}-{now.day}_{now.hour}-{now.minute}-{now.second}'
     
    # save function "activated" then...
    if(save == 'yes'):
        
        print('Saving Figure and Data...')
     
        # creating folder where outputs are saved
        dir = os.getcwd()
        out_folder = os.path.join(dir, f'{out_folder}')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
                
        # file names being saved
        data_string = f'ArduinoData_{t_string}'
        time_string = f'ArduinoTime_{t_string}'
            
        # making directory new folder, saving, returning to orig directory
        os.chdir(out_folder)
        np.save(data_string, data_array)
        np.save(time_string, time_array)
        os.chdir(dir)
            
        # creating title string, renaming plot
        title_string = f'ArduinoData_{t_string}.png'
        plt.title(title_string)
        
        # changing, saving, returning directories
        os.chdir(out_folder)
        plt.savefig(title_string)
        os.chdir(dir)
        
        print('Completed Saving!')
    
        # showing plot to user
        plt.show()


    # if saving not specified, shows plot to user
    else:
        print('Complete!')
        plt.show()
    
    data_array[samp_index]
    print(time_array[samp_index], samp_index)    
    
    # Part F - Command Line Interface
# This function runs whenever this script is called from the command line
print('Input the COMPORT number, recording duration, channel number, arduino sampling frequency, and output folder name individually')
parser = argparse.ArgumentParser(description= 'Reading and plotting serial data from Arduino.')
# Add an argument where the user can specify where the output figure should be saved
parser.add_argument('-cp', '--com_port', type = str, default = 'COM4', help = 'Input the com-port path')
parser.add_argument('-rd', '--recording_duration', type = float,default = 60,  help = 'Input the recording duration')
parser.add_argument('-nc', '--n_channels', type = int, default = 3, help = 'Input the number of channels')
parser.add_argument('-fs', '--fs', type = float, default = 500, help = 'Input the frequency of arduino')
parser.add_argument('-of', '--out_folder', type = str, default = 'Proj1_DataOutput', help = 'Input the output folder path')
parser.add_argument('-save', '--save', default = 'yes', 
                help = 'Save the figure and data input? (yes or no)')   
    
if __name__ == "__main__":
    args = parser.parse_args() 
    read_and_plot_serial_data(args.com_port, args.recording_duration, 
                              args.n_channels, args.fs, args.out_folder, args.save)
