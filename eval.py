import json
import os
from natsort import natsorted

output_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/eval_output'

# === BUILD SUPERVISE.LY JOINT DICTIONARY === #
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
        # print('Node: ' + code + ', Label: ' + left_meta_dict[code])

with open("/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/right-annotation/meta.json") as f:
    right_meta_data = json.load(f)
    for code in right_meta_data['classes'][0]['geometry_config']['nodes']:
        label = right_meta_data['classes'][0]['geometry_config']['nodes'][code]['label']
        right_meta_dict[code] = label
        # print('Node: ' + code + ', Label: ' + right_meta_dict[code])

if left_meta_dict == right_meta_dict:
    joint_dict = left_meta_dict
    print('Joint Dictionary built successfully')
else:
    print('ERROR: Joint Dictionary not built successfully - left and right dictionaries are different')
print()

with open(output_path + '/annotation_joint_dict.json', 'w', encoding='utf-8') as f:
    json.dump(joint_dict, f, ensure_ascii=False, indent=4)




# === BUILD ANNOTATION DICTIONARIES === #
# Now we will use the individual json files and joint_dict to extract the position of each joint, for each annotated
# image. We will output dictionaries for the left-small and right-small datasets, including the total number of images
# and images without skeletons ("empty")

# Annotation skeleton to body part Translation dictionary:
annotation_to_body_dict = {
    # Remember: when looking at the image depicting the skeleton, it is as if the human is looking towards us,
    # so right or left here refers to the human's pov
    0: 'Nose',
    1: 'Chest',
    2: 'Right shoulder',
    3: 'Right elbow',
    4: 'Right wrist',
    5: 'Left shoulder',
    6: 'Left elbow',
    7: 'Left wrist',
    8: 'Right hip',
    9: 'Right knee',
    10: 'Right ankle',
    11: 'Left hip',
    12: 'Left knee',
    13: 'Left ankle',
    14: 'Right eye',
    15: 'Left eye',
    16: 'Right ear',
    17: 'Left ear'
}

# Path to directory
left_path_to_json = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/left-annotation/left-small/ann/'
right_path_to_json = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/right-annotation/right-small/ann/'

# Gather json files in a sorted list
left_file_list = natsorted([file for file in os.listdir(left_path_to_json) if file.endswith('.json')])
right_file_list = natsorted([file for file in os.listdir(right_path_to_json) if file.endswith('.json')])

# Counters and dictionaries
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
                temp_dict[joint_dict[code]] = [round(loc[0], 2), round(loc[1], 2)]
                # print('Joint: ' + joint_dict[code] + ', code:' + code + ', loc: ' + str(temp_dict[joint_dict[code]]))
        except IndexError:  # when there are no annotated skeletons, data['objects'] is an empty array
            left_counter_empty += 1
            pass
    # Saves temporary dictionary as the value for the key 'leftx' (the name of the image file)
    left_annot_dict['left-small' + str(left_counter_total)] = temp_dict

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
                temp_dict[joint_dict[code]] = [round(loc[0], 2), round(loc[1], 2)]
                # print('Joint: ' + joint_dict[code] + ', code:' + code + ', loc: ' + str(temp_dict[joint_dict[code]]))
        except IndexError:  # when there are no annotated skeletons, data['objects'] is an empty array
            right_counter_empty += 1
            pass
    # Saves temporary dictionary as the value for the key 'rightx' (the name of the image file)
    right_annot_dict['right-small' + str(right_counter_total)] = temp_dict

print('Left Annotation Dictionary built successfully')
print('Total left dataset images: ' + str(left_counter_total))
left_annot_dict['Total images'] = left_counter_total
print('Empty left images: ' + str(left_counter_empty))
left_annot_dict['Empty images'] = left_counter_empty

with open(output_path + '/left_annot_dict.json', 'w', encoding='utf-8') as f:
    json.dump(left_annot_dict, f, ensure_ascii=False, indent=4)

print()
print('Right Annotation Dictionary built successfully')
print('Total right dataset images: ' + str(right_counter_total))
right_annot_dict['Total images'] = right_counter_total
print('Empty right images: ' + str(right_counter_empty))
right_annot_dict['Empty images'] = right_counter_empty

with open(output_path + '/right_annot_dict.json', 'w', encoding='utf-8') as f:
    json.dump(right_annot_dict, f, ensure_ascii=False, indent=4)





# === BUILD OPENPIFPAF JOINT DICTIONARIES === #

# PifPaf to Annotation Skeletons joint translation dictionary:
openpifpaf_to_annotation_dict = {
    0: 0,       # Nose
                # Pifpaf does not have a Chest keypoint that would correspond to annotation number 1
    6: 2,       # Right shoulder
    8: 3,       # Right elbow
    10: 4,      # Right wrist
    5: 5,       # Left shoulder
    7: 6,       # Left elbow
    9: 7,       # Left wrist
    12: 8,      # Right hip
    14: 9,      # Right knee
    16: 10,     # Right ankle
    11: 11,     # Left hip
    13: 12,     # Left knee
    15: 13,     # Left ankle
    2: 14,      # Right eye
    1: 15,      # Left eye
    4: 16,      # Right ear
    3: 17,      # Left ear
}

openpifpaf_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/openpifpaf_output/run'
left_openpifpaf_run = 7
right_openpifpaf_run = 12

# Gather json files in a sorted list
openpifpaf_left_file_list = \
    natsorted([file for file in os.listdir(openpifpaf_path + str(left_openpifpaf_run)) if file.endswith('keypoints'
                                                                                                        '.json')])
openpifpaf_right_file_list = \
    natsorted([file for file in os.listdir(openpifpaf_path + str(right_openpifpaf_run)) if file.endswith('keypoints'
                                                                                                         '.json')])

# Counters and Dictionaries
# left_counter_total = 0  # number of total images in left openpifpaf run (reused variable)
# right_counter_total = 0  # number of total images in right openpifpaf run (reused variable)
left_counter_empty = 0  # number of empty (no skeletons) images in left openpifpaf run (reused variable)
right_counter_empty = 0  # number of empty (no skeletons) images in right openpifpaf run (reused variable)
left_counter_extra = 0  # number of images in left openpifpaf run with more than 1 skeleton detected
right_counter_extra = 0  # number of images in right openpifpaf run with more than 1 skeleton detected
left_openpifpaf_dict = {}  # empty dictionary for openpifpaf results of left-small dataset
right_openpifpaf_dict = {}  # empty dictionary for openpifpaf results of right-small dataset

for left_counter_total, file_name in enumerate(openpifpaf_left_file_list):
    temp_dict = {}  # temporary dictionary for node label and location tuple

    # Open .json file to extract annotated joints
    with open(openpifpaf_path + str(left_openpifpaf_run) + '/' + file_name) as json_file:
        data = json.load(json_file)

    # Save total number of skeletons detected, both true and eventual false positives
    temp_dict['skeleton_number'] = len(data)
    if len(data) == 0:
        left_counter_empty += 1
    elif len(data) > 1:
        left_counter_extra += 1

    for skeleton_counter, skeleton in enumerate(data):
        skeleton_dict = {}  # temporary dictionary to build the joint locations for this specific skeleton
        keypoint_list = [skeleton['keypoints'][x:x + 3] for x in range(0, len(skeleton['keypoints']), 3)]  # From the
        # keypoint list of this skeleton, we extract the joint values in sets of 3: (x, y, c) where x and y are the
        # coordinates and c is the confidence score.

        for joint_counter, joint in enumerate(keypoint_list):
            if joint[2] > 0:  # If the confidence score, c is greater than 0, a joint is detected
                skeleton_dict[joint_counter] = joint

        temp_dict[skeleton_counter + 1] = skeleton_dict

    left_openpifpaf_dict['left-small' + str(left_counter_total + 1)] = temp_dict

print()
print('Left OpenPifPaf Dictionary built successfully')
print('Total left OpenPifPaf images: ' + str(left_counter_total + 1))
left_openpifpaf_dict['Total images'] = left_counter_total + 1
print('Empty (0 skeletons) left images: ' + str(left_counter_empty))
left_openpifpaf_dict['Empty images'] = left_counter_empty
print('Extra (>1 skeletons) left images: ' + str(left_counter_extra))
left_openpifpaf_dict['Extra images'] = left_counter_extra

with open(output_path + '/left_openpifpaf_dict.json', 'w', encoding='utf-8') as f:
    json.dump(left_openpifpaf_dict, f, ensure_ascii=False, indent=4)


for right_counter_total, file_name in enumerate(openpifpaf_right_file_list):
    temp_dict = {}  # temporary dictionary for skeletons, node label and location tuple

    # Open .json file to extract annotated joints
    with open(openpifpaf_path + str(right_openpifpaf_run) + '/' + file_name) as json_file:
        data = json.load(json_file)

    # Save total number of skeletons detected, both true and eventual false positives
    temp_dict['skeleton_number'] = len(data)
    if len(data) == 0:
        right_counter_empty += 1
    elif len(data) > 1:
        right_counter_extra += 1

    for skeleton_counter, skeleton in enumerate(data):
        skeleton_dict = {}  # temporary dictionary to build the joint locations for this specific skeleton
        keypoint_list = [skeleton['keypoints'][x:x + 3] for x in range(0, len(skeleton['keypoints']), 3)]  # From the
        # keypoint list of this skeleton, we extract the joint values in sets of 3: (x, y, c) where x and y are the
        # coordinates and c is the confidence score.

        for joint_counter, joint in enumerate(keypoint_list):
            if joint[2] > 0:  # If the confidence score, c is greater than 0, a joint is detected
                skeleton_dict[joint_counter] = joint

        temp_dict[skeleton_counter + 1] = skeleton_dict

    right_openpifpaf_dict['right-small' + str(right_counter_total + 1)] = temp_dict

print()
print('Right OpenPifPaf Dictionary built successfully')
print('Total right OpenPifPaf images: ' + str(right_counter_total + 1))
right_openpifpaf_dict['Total images'] = right_counter_total + 1
print('Empty (0 skeletons) right images: ' + str(right_counter_empty))
right_openpifpaf_dict['Empty images'] = right_counter_empty
print('Extra (>1 skeletons) right images: ' + str(right_counter_extra))
right_openpifpaf_dict['Extra images'] = right_counter_extra

with open(output_path + '/right_openpifpaf_dict.json', 'w', encoding='utf-8') as f:
    json.dump(right_openpifpaf_dict, f, ensure_ascii=False, indent=4)


# # === BUILD OPENPOSE JOINT DICTIONARIES === #

# OpenPose to Annotation Skeletons joint translation dictionary:
openpose_to_annotation_dict = {
    0: 0,       # Nose
    1: 1,       # Chest
    2: 2,       # Right shoulder
    3: 3,       # Right elbow
    4: 4,       # Right wrist
    5: 5,       # Left shoulder
    6: 6,       # Left elbow
    7: 7,       # Left wrist
    # OpenPose has an extra keypoint with label 8, that is located between the left and right hip
    9: 8,       # Right hip
    10: 9,      # Right knee
    11: 10,     # Right ankle
    12: 11,     # Left hip
    13: 12,     # Left knee
    14: 13,     # Left ankle
    15: 14,     # Right eye
    16: 15,     # Left eye
    17: 16,     # Right ear
    18: 17,     # Left ear
}

openpose_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/openpose_output/run'
left_openpose_run = 5
right_openpose_run = 10

# Gather json files in a sorted list
openpose_left_file_list = \
    natsorted([file for file in os.listdir(openpose_path + str(left_openpose_run)) if file.endswith('keypoints'
                                                                                                        '.json')])
openpose_right_file_list = \
    natsorted([file for file in os.listdir(openpose_path + str(right_openpose_run)) if file.endswith('keypoints'
                                                                                                         '.json')])

# Counters and Dictionaries
# left_counter_total = 0  # number of total images in left openpose run (reused variable)
# right_counter_total = 0  # number of total images in right openpose run (reused variable)
left_counter_empty = 0  # number of empty (no skeletons) images in left openpose run (reused variable)
right_counter_empty = 0  # number of empty (no skeletons) images in right openpose run (reused variable)
left_counter_extra = 0  # number of images in left openpose run with more than 1 skeleton detected
right_counter_extra = 0  # number of images in right openpose run with more than 1 skeleton detected
left_openpose_dict = {}  # empty dictionary for openpose results of left-small dataset
right_openpose_dict = {}  # empty dictionary for openpose results of right-small dataset

for left_counter_total, file_name in enumerate(openpose_left_file_list):
    temp_dict = {}  # temporary dictionary for skeletons, node label and location tuple

    # Open .json file to extract annotated joints
    with open(openpose_path + str(left_openpose_run) + '/' + file_name) as json_file:
        data = json.load(json_file)

    # Save total number of skeletons detected, both true and eventual false positives
    skeletons = data['people']
    temp_dict['skeleton_number'] = len(skeletons)
    if len(skeletons) == 0:
        left_counter_empty += 1
    elif len(skeletons) > 1:
        left_counter_extra += 1

    for skeleton_counter, skeleton in enumerate(skeletons):
        skeleton_dict = {}  # temporary dictionary to build the joint locations for this specific skeleton
        keypoint_list = [skeleton['pose_keypoints_2d'][x:x + 3] for x in range(0, len(skeleton['pose_keypoints_2d']),
                                                                               3)]  # From the keypoint list of this
        # skeleton, we extract the joint values in sets of 3: (x, y, c),  where x and y are the coordinates and c is
        # the confidence score.

        for joint_counter, joint in enumerate(keypoint_list):
            if joint[2] > 0:  # If the confidence score, c is greater than 0, a joint is detected
                skeleton_dict[joint_counter] = joint

        temp_dict[skeleton_counter + 1] = skeleton_dict

    left_openpose_dict['left-small' + str(left_counter_total + 1)] = temp_dict

print()
print('Left OpenPose Dictionary built successfully')
print('Total left OpenPose images: ' + str(left_counter_total + 1))
left_openpose_dict['Total images'] = left_counter_total + 1
print('Empty (0 skeletons) left images: ' + str(left_counter_empty))
left_openpose_dict['Empty images'] = left_counter_empty
print('Extra (>1 skeletons) left images: ' + str(left_counter_extra))
left_openpose_dict['Extra images'] = left_counter_extra

with open(output_path + '/left_openpose_dict.json', 'w', encoding='utf-8') as f:
    json.dump(left_openpose_dict, f, ensure_ascii=False, indent=4)

for right_counter_total, file_name in enumerate(openpose_right_file_list):
    temp_dict = {}  # temporary dictionary for skeletons, node label and location tuple

    # Open .json file to extract annotated joints
    with open(openpose_path + str(right_openpose_run) + '/' + file_name) as json_file:
        data = json.load(json_file)

    # Save total number of skeletons detected, both true and eventual false positives
    skeletons = data['people']
    temp_dict['skeleton_number'] = len(skeletons)
    if len(skeletons) == 0:
        right_counter_empty += 1
    elif len(skeletons) > 1:
        right_counter_extra += 1

    for skeleton_counter, skeleton in enumerate(skeletons):
        skeleton_dict = {}  # temporary dictionary to build the joint locations for this specific skeleton
        keypoint_list = [skeleton['pose_keypoints_2d'][x:x + 3] for x in range(0, len(skeleton['pose_keypoints_2d']),
                                                                               3)]  # From the keypoint list of this
        # skeleton, we extract the joint values in sets of 3: (x, y, c),  where x and y are the coordinates and c is
        # the confidence score.

        for joint_counter, joint in enumerate(keypoint_list):
            if joint[2] > 0:  # If the confidence score, c is greater than 0, a joint is detected
                skeleton_dict[joint_counter] = joint

        temp_dict[skeleton_counter + 1] = skeleton_dict

    right_openpose_dict['right-small' + str(right_counter_total + 1)] = temp_dict

print()
print('Right OpenPose Dictionary built successfully')
print('Total right OpenPose images: ' + str(right_counter_total + 1))
right_openpose_dict['Total images'] = right_counter_total + 1
print('Empty (0 skeletons) right images: ' + str(right_counter_empty))
right_openpose_dict['Empty images'] = right_counter_empty
print('Extra (>1 skeletons) right images: ' + str(right_counter_extra))
right_openpose_dict['Extra images'] = right_counter_extra

with open(output_path + '/right_openpose_dict.json', 'w', encoding='utf-8') as f:
    json.dump(right_openpose_dict, f, ensure_ascii=False, indent=4)

# === COMPARISONS === #

# OpenPifPaf
# for image in left_annot_dict:
    # for joint in left_annot_dict[image]
