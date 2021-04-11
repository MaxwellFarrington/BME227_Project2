# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 15:36:57 2021

Created by Lianna Klinger 

Due on Monday, 4/12/2021 for BME 227

This code is a portion of Project 2. Part C reads in the data collected in part B, separates it into epochs and a series of boolean arrays that indicate the true and predictd actions/movements performed. The comparison between the true and predicted arrays are used to calculate accuarcy, ITR, and create a confusion matrix.
define a threshold to then create predictions and compare the predictions to true values. This information will result in the creation of a confusion matrix.

The following actions are listed next to its corresponding mouse movement:
    Rest = Rest
    Left leg flexion  = Left
    Right leg flexion = Right
    Arm and left leg flexion = Down
    Arm and right leg flexion = Up
    Arm, left leg, and right leg flexion = Click

"""
# %% Import packages
import numpy as np
from matplotlib import pyplot as plt

# %% Epoch data
# set varaibles 
recording_duration = 60
channel_count = 3
fs = 500
out_folder = '.'

# load in data obtained from part B
emg_voltage = np.load('C:/Users/lkkli/OneDrive/Documents/Spring 2021/BME227-S21/ArduinoData_2021-4-9_16-24-26.npy') 
emg_time = np.load('C:/Users/lkkli/OneDrive/Documents/Spring 2021/BME227-S21/ArduinoTime_2021-4-9_16-24-26.npy') 

# number of EMG samples in each 200 ms chunk 
epoch_sample_count = int(fs*0.2) 
sample_count = recording_duration*fs
# number of 200 ms epochs in data
epoch_count = int(sample_count/epoch_sample_count)

# reshape or epoch data into a 3d array
emg_epoch = np.reshape(emg_voltage,(epoch_count,epoch_sample_count,channel_count))

# save the 3D array
# obtain proper name for epoch array and set to proper folder
name_epoch_array = 'ArduinoData_2021-4-9_16-24-26_epochs'
save_epoch = '%s/%s.npy'%(out_folder,name_epoch_array)
np.save(save_epoch,emg_epoch)

# %% Set is_true variables
# calculate the variance 
emg_epoch_var = np.var(emg_epoch,axis=1)

# create 3 boolean arrays that is true when squeezing arm, left leg, and right leg
# 200 ms epochs, 60 seconds recording with each action for 2 second --> 10 epochs per command
is_true_left_leg =  np.array([0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1]*5, dtype=bool)
is_true_right_leg = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]*5, dtype=bool)
is_true_arm =       np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]*5, dtype=bool)

# %% Plot histograms and chose threshold
# plot histogram of the variances in epochs when squeezing left leg
plt.figure(0)
plot_left_true = plt.hist(emg_epoch_var[is_true_left_leg == 1,1], bins=50, alpha=0.5)
plot_left_false = plt.hist(emg_epoch_var[is_true_left_leg == 0,1], bins=50, alpha=0.5)

# add line for threshold cutoff
threshold_left = 0.000085
plt.axvline(x=threshold_left,color = 'r', linewidth = 1)

# add plot labels
plt.ylabel('Number of Trials')
plt.xlabel('Variance on Channel 1 (V^2)')
plt.title('HMI Histogram for Left Leg Squeeze')
plt.legend(['Threshold','True Left','Not True Left'])

# save histogram for left leg'
name_HMI_left = 'Project2_HMI_Histogram_Left'
plt.savefig('{0}/{1}.png'.format(out_folder,name_HMI_left))

# plot histogram of the variances in epochs when squeezing right leg
plt.figure(1)
plot_right_true = plt.hist(emg_epoch_var[is_true_right_leg == 1,2], bins=50, alpha=0.5)
plot_right_false = plt.hist(emg_epoch_var[is_true_right_leg == 0,2], bins=50, alpha=0.5)

# add line for threshold cutoff 
threshold_right = 0.00003
plt.axvline(x=threshold_right,color = 'r', linewidth = 1)
plt.ylabel('Number of Trials')
plt.xlabel('Variance on Channel 2 (V^2)')
plt.title('HMI Histogram for Right Leg Squeeze')
plt.legend(['Threshold','True Right','Not True Right'])

# save histogram for right leg
name_HMI_right = 'Project2_HMI_Histogram_Right'
plt.savefig('{0}/{1}.png'.format(out_folder,name_HMI_right))

# plot histogram of the variances in epochs when squeezing arm
plt.figure(2)
plot_arm_true = plt.hist(emg_epoch_var[is_true_arm == 1,0], bins=50, alpha=0.5)
plot_arm_false = plt.hist(emg_epoch_var[is_true_arm == 0,0], bins=50, alpha=0.5)

# add line for threshold cutoff 
threshold_arm = 0.000014
plt.axvline(x=threshold_arm,color = 'r', linewidth = 1)
plt.ylabel('Number of Trials')
plt.xlabel('Variance on Channel 0 (V^2)')
plt.title('HMI Histogram for Arm Squeeze')
plt.legend(['Threshold','True Arm','Not True Arm'])

# save histogram for arm
name_HMI_arm = 'Project2_HMI_Histogram_Arm'
plt.savefig('{0}/{1}.png'.format(out_folder,name_HMI_arm))

# %% Create is_predicted variables
# use cuttoff to create boolean array for left leg, right leg, and arm
is_predicted_left_leg =  emg_epoch_var[:,1] >= threshold_left
is_predicted_right_leg = emg_epoch_var[:,2] >= threshold_right
is_predicted_arm = emg_epoch_var[:,0] >= threshold_arm

# %% Evaluate HMI
# --- LEFT LEG
# true postive 
true_positive_left_leg = np.sum((is_true_left_leg == 1) & (is_predicted_left_leg == 1))
print(f'TP for left leg is {true_positive_left_leg}...')
# false positive 
false_positive_left_leg = np.sum((is_true_left_leg == 0) & (is_predicted_left_leg == 1))
print(f'FP for left leg is {false_positive_left_leg}...')
# false negative
false_negative_left_leg = np.sum((is_true_left_leg == 1) & (is_predicted_left_leg == 0))
print(f'FN for left leg is {false_negative_left_leg}...')
#true negative
true_negative_left_leg = np.sum((is_true_left_leg == 0) & (is_predicted_left_leg == 0))
print(f'TN for left leg is {true_negative_left_leg}...')
# calculate accuracy
total_predictions = len(emg_epoch_var)
P_left_leg = (true_positive_left_leg + true_negative_left_leg)/total_predictions
print(f'Accuracy for left leg is {P_left_leg}...')
# calculate sensitivity 
sensitivity_left_leg = true_positive_left_leg/(true_positive_left_leg + false_negative_left_leg)
print(f'Sensitivity for left leg is {sensitivity_left_leg}...')
# calculate specificity 
specificity_left_leg = 1 - (false_positive_left_leg/(false_positive_left_leg + true_negative_left_leg)) 
print(f'Specificity for left leg is {specificity_left_leg}...')
# calculate ITR in bits per second
# n is classes, left and not left
n_left_leg = 2
ITR_left_trial = np.log2(n_left_leg) + P_left_leg*(np.log2(P_left_leg)) + (1-P_left_leg) * np.log2((1-P_left_leg)/(n_left_leg-1))
# now convert ITR from bits per trial to bits per second
# 5 epochs per second 
ITR_left_sec = ITR_left_trial * 5
print(f'ITR for left leg in bits per second is {ITR_left_sec}...\n')

# --- RIGHT LEG
# true postive 
true_positive_right_leg = np.sum((is_true_right_leg == 1) & (is_predicted_right_leg == 1))
print(f'TP for right leg is {true_positive_right_leg}...')
# false positive 
false_positive_right_leg = np.sum((is_true_right_leg == 0) & (is_predicted_right_leg == 1))
print(f'FP for right leg is {false_positive_right_leg}...')
# false negative
false_negative_right_leg = np.sum((is_true_right_leg == 1) & (is_predicted_right_leg == 0))
print(f'FN for right leg is {false_negative_right_leg}...')
#true negative
true_negative_right_leg = np.sum((is_true_right_leg == 0) & (is_predicted_right_leg == 0))
print(f'TN for right leg is {true_negative_right_leg}...')
# calculate accuracy
P_right_leg = (true_positive_right_leg + true_negative_right_leg)/total_predictions
print(f'Accuracy for right leg is {P_right_leg}...')
# calculate sensitivity 
sensitivity_right_leg = true_positive_right_leg/(true_positive_right_leg + false_negative_right_leg)
print(f'Sensitivity for right leg is {sensitivity_right_leg}...')
# calculate specificity 
specificity_right_leg = 1 - (false_positive_right_leg/(false_positive_right_leg + true_negative_right_leg)) 
print(f'Specificity for right leg is {specificity_right_leg}...')
# calculate ITR in bits per second
# n is classes, right and not right
n_right_leg = 2
ITR_right_trial = np.log2(n_right_leg) + P_right_leg*(np.log2(P_right_leg)) + (1-P_right_leg) * np.log2((1-P_right_leg)/(n_right_leg-1))
# now convert ITR from bits per trial to bits per second
# 5 epochs per second
ITR_right_sec = ITR_right_trial * 5
print(f'ITR for right leg in bits per second is {ITR_right_sec}...\n')

# --- ARM
# true postive
true_positive_arm = np.sum((is_true_arm == 1) & (is_predicted_arm == 1))
print(f'TP for arm is {true_positive_arm}...')
# false positive 
false_positive_arm = np.sum((is_true_arm == 0) & (is_predicted_arm == 1))
print(f'FP for arm is {false_positive_arm}...')
# false negative
false_negative_arm = np.sum((is_true_arm == 1) & (is_predicted_arm == 0))
print(f'FN for arm is {false_negative_arm}...')
#true negative
true_negative_arm = np.sum((is_true_arm == 0) & (is_predicted_arm == 0))
print(f'TN for arm is {true_negative_arm}...')
# calculate accuracy
P_arm = (true_positive_arm + true_negative_arm)/total_predictions
print(f'Accuracy for arm is {P_arm}...')
# calculate sensitivity 
sensitivity_arm = true_positive_arm/(true_positive_arm + false_negative_arm)
print(f'Sensitivity for arm is {sensitivity_arm}...')
# calculate specificity 
specificity_arm = 1 - (false_positive_arm/(false_positive_arm + true_negative_arm)) 
print(f'Specificity for arm is {specificity_arm}...')
# calculate ITR in bits per second
# n is classes, arm and not arm
n_arm = 2
ITR_arm_trial = np.log2(n_arm) + P_arm*(np.log2(P_arm)) + (1-P_arm) * np.log2((1-P_arm)/(n_arm-1))
# now convert ITR from bits per trial to bits per second
# 5 epochs per second
ITR_arm_sec = ITR_arm_trial * 5
print(f'ITR for arm in bits per second is {ITR_arm_sec}...\n')

# %% Create confusion matrix
# create is_true_6 variables
is_true_6_rest = ((is_true_left_leg == 0) & (is_true_right_leg == 0)) & (is_true_arm == 0)
is_true_6_left = ((is_true_left_leg == 1) & (is_true_right_leg == 0)) & (is_true_arm == 0)
is_true_6_right = ((is_true_left_leg == 0) & (is_true_right_leg == 1)) & (is_true_arm == 0)
is_true_6_down = ((is_true_left_leg == 1) & (is_true_right_leg == 0)) & (is_true_arm == 1)
is_true_6_up = ((is_true_left_leg == 0) & (is_true_right_leg == 1)) & (is_true_arm == 1)
is_true_6_click = ((is_true_left_leg == 1) & (is_true_right_leg == 1)) & (is_true_arm == 1)

# create is_predicted_6 variables
is_predicted_6_rest = ((is_predicted_left_leg == 0) & (is_predicted_right_leg == 0)) & (is_predicted_arm == 0)
is_predicted_6_left = ((is_predicted_left_leg == 1) & (is_predicted_right_leg == 0)) & (is_predicted_arm == 0)
is_predicted_6_right = ((is_predicted_left_leg == 0) & (is_predicted_right_leg == 1)) & (is_predicted_arm == 0)
is_predicted_6_down = ((is_predicted_left_leg == 1) & (is_predicted_right_leg == 0)) & (is_predicted_arm == 1)
is_predicted_6_up = ((is_predicted_left_leg == 0) & (is_predicted_right_leg == 1)) & (is_predicted_arm == 1)
is_predicted_6_click = ((is_predicted_left_leg == 1) & (is_predicted_right_leg == 1)) & (is_predicted_arm == 1)

# create array that is filled with correct action
epoch_count = len(is_predicted_6_rest)
true_actions = np.array(['rest']*epoch_count, dtype=object) 
true_actions[is_true_6_rest] = 'rest'
true_actions[is_true_6_left] = 'left'
true_actions[is_true_6_right] = 'right'
true_actions[is_true_6_up] = 'up'
true_actions[is_true_6_down] = 'down'
true_actions[is_true_6_click] = 'click'

# create array that is filled with predictions
predicted_actions = np.array(['rest']*epoch_count, dtype=object)
predicted_actions[is_predicted_6_rest] = 'rest'
predicted_actions[is_predicted_6_left] = 'left'
predicted_actions[is_predicted_6_right] = 'right'
predicted_actions[is_predicted_6_up] = 'up'
predicted_actions[is_predicted_6_down] = 'down'
predicted_actions[is_predicted_6_click] = 'click'

# create confusion matrix
possible_actions = ['rest', 'left', 'right','down','up', 'click']
action_count = len(possible_actions)
confusion_matrix = np.zeros([action_count,action_count])
for predicted_action_index, predicted_action in enumerate(possible_actions):
    for true_action_index, true_action in enumerate(possible_actions):
        confusion_matrix[predicted_action_index,true_action_index] = \
            np.sum((predicted_actions==predicted_action) & (true_actions==true_action))

plt.figure()
plt.clf()
plt.pcolor(confusion_matrix)
plt.title('HMI Confusion Matrix')
plt.xlabel('Actual Action')
plt.xticks(ticks = [0.5,1.5,2.5,3.5,4.5,5.5] ,labels = possible_actions)
plt.ylabel('Predicted Action')
plt.yticks(ticks = [0.5,1.5,2.5,3.5,4.5,5.5] ,labels = possible_actions)
cbar = plt.colorbar()
cbar.set_label('# Trials')

# save confusion matrix
name_confusion_matrix = 'Project2_Confusion_Matrix'
plt.savefig('{0}/{1}.png'.format(out_folder,name_confusion_matrix))

# solve for accuracy
P_con_mat = (confusion_matrix[0,0] + confusion_matrix[1,1] + confusion_matrix[2,2] + confusion_matrix[3,3] + confusion_matrix[4,4] +confusion_matrix[5,5])/total_predictions 
print(f'The accuracy for the confusion matrix is {P_con_mat}...')
# solve for ITR
# classes: left, right, click, rest, up, down, all
n_con_mat = 6
ITR_con_mat_trial = np.log2(n_con_mat) + P_con_mat*(np.log2(P_con_mat)) + (1-P_con_mat) * np.log2((1-P_con_mat)/(n_con_mat-1))
# now convert ITR from bits per trial to bits per second
# 5 epochs per second
ITR_con_mat_sec = ITR_con_mat_trial * 5
print(f'ITR for the confusion matrix in bits per second is {ITR_con_mat_sec}...\n')

 