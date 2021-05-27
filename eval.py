import cv2
import glob
import json
import os
from natsort import natsorted


# === BUILD JOINT DICTIONARY === #
# In supervise.ly, a 'Skeleton' class is defined with nodes that represent each skeleton joint, labelled from 0 to
# 17. Once exported, the annotated datasets come with a meta.json file that, among other information, assigns codes
# to each of these nodes. Therefore, we need to build a dictionary that associates the codes with each joint so that
# we can later extract the position of each joint in the annotated images.

left_meta_dict = {}
right_meta_dict = {}
joint_dict = {}

with open("/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/left-annotation/meta.json") as f:
    left_meta_data = json.load(f)
    for code in left_meta_data['classes'][0]['geometry_config']['nodes']:
        label = left_meta_data['classes'][0]['geometry_config']['nodes'][code]['label']
        left_meta_dict[code] = label
        # print('Node: ' + code + ', Label: ' + left_meta_dict['code'])

with open("/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/right-annotation/meta.json") as f:
    right_meta_data = json.load(f)
    for code in right_meta_data['classes'][0]['geometry_config']['nodes']:
        label = right_meta_data['classes'][0]['geometry_config']['nodes'][code]['label']
        right_meta_dict[code] = label
        # print('Node: ' + code + ', Label: ' + right_meta_dict['code'])

if left_meta_dict == right_meta_dict:
    joint_dict = left_meta_dict
    print('Joint Dictionary built successfully')
else:
    print('ERROR: Joint Dictionary not built successfully - left and right dictionaries are different')
print()

# === BUILD ANNOTATION DICTIONARIES === #

# Path to directory
left_path_to_json = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/left-annotation/left-small/ann/'
right_path_to_json = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/right-annotation/right-small/ann/'

# Gather json files in a sorted list
left_file_list = natsorted([file for file in os.listdir(left_path_to_json) if file.endswith('.json')])
right_file_list = natsorted([file for file in os.listdir(right_path_to_json) if file.endswith('.json')])

# Counters
left_counter_total = 0  # number of total images in left annotated dataset
left_counter_empty = 0  # photos without people/annotated skeletons in left annotated dataset
right_counter_total = 0  # number of total images in right annotated dataset
right_counter_empty = 0  # photos without people/annotated skeletons in right annotated dataset

left_annot_dict = {}  # empty dictionary for left annotations
right_annot_dict = {}  # empty dictionary for right annotations

for file_name in left_file_list:
    # print(file_name)
    left_counter_total += 1
    temp_dict = {}  # temporary dictionary for node label and location tuple

    # Open .json file to extract annotated joints
    with open(left_path_to_json + file_name) as json_file:
        data = json.load(json_file)
        try:
            for code in data['objects'][0]['nodes']:
                # the coordinates of each joint are extracted
                loc = data['objects'][0]['nodes'][code]['loc']
                # these are rounded and saved in the temporary dictionary
                temp_dict[joint_dict[code]] = [round(loc[0]), round(loc[1])]
                # print('Joint: ' + joint_dict[code] + ', code:' + code + ', loc: ' + str(temp_dict[joint_dict[code]]))
        except IndexError:  # when there are no annotated skeletons, data['objects'] is an empty array
            left_counter_empty += 1
            pass
    # Saves temporary dictionary as the value for the key 'leftx' (the name of the image file)
    left_annot_dict['left' + str(left_counter_total)] = temp_dict

for file_name in right_file_list:
    # print(file_name)
    right_counter_total += 1
    temp_dict = {}  # temporary dictionary for node label and location tuple

    # Open .json file to extract annotated joints
    with open(right_path_to_json + file_name) as json_file:
        data = json.load(json_file)
        try:
            for code in data['objects'][0]['nodes']:
                # the coordinates of each joint are extracted
                loc = data['objects'][0]['nodes'][code]['loc']
                # these are rounded and saved in the temporary dictionary
                temp_dict[joint_dict[code]] = [round(loc[0]), round(loc[1])]
                # print('Joint: ' + joint_dict[code] + ', code:' + code + ', loc: ' + str(temp_dict[joint_dict[code]]))
        except IndexError:  # when there are no annotated skeletons, data['objects'] is an empty array
            right_counter_empty += 1
            pass
    # Saves temporary dictionary as the value for the key 'rightx' (the name of the image file)
    right_annot_dict['right' + str(right_counter_total)] = temp_dict

print('Left Annotation Dictionary built successfully')
print('Total left dataset images: ' + str(left_counter_total))
print('Empty left images: ' + str(left_counter_empty))

print()
print('Right Annotation Dictionary built successfully')
print('Total right dataset images: ' + str(right_counter_total))
print('Empty right images: ' + str(right_counter_empty))
