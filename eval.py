import json
import os
from natsort import natsorted
import math

output_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/eval_output'
output_flag = True

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

if output_flag:
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

if output_flag:
    with open(output_path + '/left_annot_dict.json', 'w', encoding='utf-8') as f:
        json.dump(left_annot_dict, f, ensure_ascii=False, indent=4)

print()
print('Right Annotation Dictionary built successfully')
print('Total right dataset images: ' + str(right_counter_total))
right_annot_dict['Total images'] = right_counter_total
print('Empty right images: ' + str(right_counter_empty))
right_annot_dict['Empty images'] = right_counter_empty

if output_flag:
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

if output_flag:
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

if output_flag:
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

if output_flag:
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

if output_flag:
    with open(output_path + '/right_openpose_dict.json', 'w', encoding='utf-8') as f:
        json.dump(right_openpose_dict, f, ensure_ascii=False, indent=4)


# ================================================ #
# ========= EVALUATE AND OUTPUT METRICS ========== #
# ================================================ #

# ======================================================================== OpenPifPaf left-small dataset
results_left_openpifpaf = {}

# Initialize variables that are used to calculate metrics:
joint_total_left_openpifpaf = 0
mpjpe_left_openpifpaf = 0  # Total error for all images in this dataset
fp_joint_total_left_openpifpaf = 0
fn_joint_total_left_openpifpaf = 0

mpjpe_threshold = 50  # This should be a percentage of the bounding box size but we will ballpark to filter out
# false positives for now and then later program an adaptive threshold based on height (ymax-ymin) of the skeleton

for image in left_openpifpaf_dict:
    if image.startswith('left'):  # excludes the keys that are extra information about the number of images
        image_dict = {}

        # Save values related to annotation:
        if len(left_annot_dict[image]) == 0:  # In the annotation, there is either a single skeleton or there is none
            annotated_skeleton_total = 0
            annotated_joint_total = 0
        else:
            annotated_skeleton_total = 1
            annotated_joint_total = len(left_annot_dict[image])
        image_dict['annotated_skeleton_total'] = annotated_skeleton_total
        image_dict['annotated_joint_total'] = annotated_joint_total

        matching_skeleton_total = 0  # the number of skeletons that match with annot (mpjpe is within the threshold)
        # This helps detect cases where the method detects the operator but does not associate all the joints,
        # creating more than one detected skeleton.
        matching_skeleton_dict = {}  # contains dictionaries of each skeleton that matches with annotation

        for skeleton in left_openpifpaf_dict[image]:
            if str(skeleton).startswith('skeleton_number'):  # extract the number of skeletons OpenPifPaf detected
                pifpaf_skeleton_total = left_openpifpaf_dict[image][skeleton]
            else:  # all other keys are skeletons
                skeleton_dict = {}  # Temporary dict to save this skeleton's results. The key corresponds to the
                # joint, using the annotation label, or relevant variables such as joint_counter_total

                joint_counter_total = 0  # Number of total joints detected by OpenPifPaf
                fp_joint_total = 0  # Number of false positive joints detected by OpenPifPaf (no match in annotation)
                fn_joint_total = 0  # Number of false negative joints (present in annotation but no detected by PifPaf)
                error_total = 0  # Used to calculate mpjpe

                for joint in left_openpifpaf_dict[image][skeleton]:
                    pifpaf_coordinates = [int(left_openpifpaf_dict[image][skeleton][joint][index]) for index in [0, 1]]
                    pifpaf_confidence = left_openpifpaf_dict[image][skeleton][joint][2]
                    label = openpifpaf_to_annotation_dict[int(joint)]  # corresponding joint label in annotation
                    annotated_coordinates: object = left_annot_dict[image].get(str(label))  # We use the .get()
                    # method to handle the cases where the annotation does not have a matching joint, aka,
                    # a joint false positive

                    if annotated_coordinates:
                        error = round(math.sqrt(
                            math.pow(pifpaf_coordinates[0] - annotated_coordinates[0], 2) +
                            math.pow(pifpaf_coordinates[1] - annotated_coordinates[1], 2)), 3)
                        skeleton_dict[label] = [error, pifpaf_confidence]  # for each joint, we save its error and
                        # confidence score (so that we can later plot them both)
                        error_total += error
                    else:
                        #  There is no matching joint in the annotation, this is a "false" positive joint.
                        skeleton_dict[label] = ['fp', pifpaf_confidence]  # fp = false positive
                        fp_joint_total += 1

                    joint_counter_total += 1

                # Check if any annotated joints are missing from this skeleton (false negatives)
                for label in left_annot_dict[image]:
                    if int(label) in skeleton_dict:
                        continue
                    else:
                        if label != '1':
                            skeleton_dict[label] = ['fn', 0]
                            fn_joint_total += 1
                        else:  # Because OpenPifPaf does not have a corresponding 'Chest' keypoint (label 1)
                            skeleton_dict[label] = ['invalid', 0]

                # Save in this skeleton's dictionary:
                skeleton_dict['joint_counter_total'] = joint_counter_total
                # Calculate the Mean Per Joint Position Error (in pixels) of this skeleton
                if joint_counter_total != 0:
                    mpjpe = round(error_total / joint_counter_total, 4)
                    skeleton_dict['mpjpe'] = mpjpe
                    skeleton_dict['fp_joint_total'] = fp_joint_total
                    skeleton_dict['fn_joint_total'] = fn_joint_total
                
                if mpjpe_threshold > mpjpe > 0:  # We include the mpjpe > 0 condition in order to not match false
                    # positive skeletons (which would have error exactly equal to 0 since that is the initial value
                    # of error_total)
                    matching_skeleton_total += 1
                    matching_skeleton_dict[skeleton] = skeleton_dict

        image_dict['pifpaf_skeleton_total'] = pifpaf_skeleton_total
        image_dict['matching_skeleton_total'] = matching_skeleton_total
        image_dict['matching_skeletons'] = matching_skeleton_dict

        # Calculate the metrics of this image:
        joint_image_total = 0
        mpjpe_image_total = 0
        mpjpe_image_average = 0
        fp_joint_image_total = 0
        fn_joint_image_total = 0
        if len(matching_skeleton_dict) != 0:
            for matching_skeleton in matching_skeleton_dict:
                joint_image_total += matching_skeleton_dict[matching_skeleton]['joint_counter_total']
                mpjpe_image_total += matching_skeleton_dict[matching_skeleton]['mpjpe']
                fp_joint_image_total += matching_skeleton_dict[matching_skeleton]['fp_joint_total']
                fn_joint_image_total += matching_skeleton_dict[matching_skeleton]['fn_joint_total']
            mpjpe_image_average = round(mpjpe_image_total / len(matching_skeleton_dict), 3)

        # Save to image metrics to its dictionary
        image_dict['joint_image_total'] = joint_image_total
        image_dict['mpjpe_image_average'] = mpjpe_image_average
        image_dict['fp_joint_image_total'] = fp_joint_image_total
        image_dict['fn_joint_image_total'] = fp_joint_image_total

        # Add to variables that will determine overall metrics for this dataset
        joint_total_left_openpifpaf += joint_image_total
        mpjpe_left_openpifpaf += mpjpe_image_average
        fp_joint_total_left_openpifpaf += fp_joint_image_total
        fn_joint_total_left_openpifpaf += fn_joint_image_total

        results_left_openpifpaf[image] = image_dict

# Overall dataset metrics:
image_total = left_openpifpaf_dict['Total images']
results_left_openpifpaf['joint_total_average_per_image'] = round(joint_total_left_openpifpaf / image_total, 3)
results_left_openpifpaf['mpjpe_average_per_image'] = \
    round(mpjpe_left_openpifpaf / image_total, 3)
results_left_openpifpaf['fp_joint_total_average_per_image'] = round(fp_joint_total_left_openpifpaf / image_total, 3)
results_left_openpifpaf['fn_joint_total_average_per_image'] = round(fn_joint_total_left_openpifpaf / image_total, 3)

if output_flag:
    with open(output_path + '/results_left_openpifpaf.json', 'w', encoding='utf-8') as f:
        json.dump(results_left_openpifpaf, f, ensure_ascii=False, indent=4)

print()
print('Left OpenPifPaf Results json built successfully')


# =================================================================== OpenPifPaf right-small dataset
results_right_openpifpaf = {}

# Initialize variables that are used to calculate metrics:
joint_total_right_openpifpaf = 0
mpjpe_right_openpifpaf = 0  # Total error for all images in this dataset
fp_joint_total_right_openpifpaf = 0
fn_joint_total_right_openpifpaf = 0

mpjpe_threshold = 50  # This should be a percentage of the bounding box size but we will ballpark to filter out
# false positives for now and then later program an adaptive threshold based on height (ymax-ymin) of the skeleton

for image in right_openpifpaf_dict:
    if image.startswith('right'):  # excludes the keys that are extra information about the number of images
        image_dict = {}

        # Save values related to annotation:
        if len(right_annot_dict[image]) == 0:  # In the annotation, there is either a single skeleton or there is none
            annotated_skeleton_total = 0
            annotated_joint_total = 0
        else:
            annotated_skeleton_total = 1
            annotated_joint_total = len(right_annot_dict[image])
        image_dict['annotated_skeleton_total'] = annotated_skeleton_total
        image_dict['annotated_joint_total'] = annotated_joint_total

        matching_skeleton_total = 0  # the number of skeletons that match with annot (mpjpe is within the threshold)
        # This helps detect cases where the method detects the operator but does not associate all the joints,
        # creating more than one detected skeleton.
        matching_skeleton_dict = {}  # contains dictionaries of each skeleton that matches with annotation

        for skeleton in right_openpifpaf_dict[image]:
            if str(skeleton).startswith('skeleton_number'):  # extract the number of skeletons OpenPifPaf detected
                pifpaf_skeleton_total = right_openpifpaf_dict[image][skeleton]
            else:  # all other keys are skeletons
                skeleton_dict = {}  # Temporary dict to save this skeleton's results. The key corresponds to the
                # joint, using the annotation label, or relevant variables such as joint_counter_total

                joint_counter_total = 0  # Number of total joints detected by OpenPifPaf
                fp_joint_total = 0  # Number of false positive joints detected by OpenPifPaf (no match in annotation)
                fn_joint_total = 0  # Number of false negative joints (present in annotation but no detected by PifPaf)
                error_total = 0  # Used to calculate mpjpe

                for joint in right_openpifpaf_dict[image][skeleton]:
                    pifpaf_coordinates = [int(right_openpifpaf_dict[image][skeleton][joint][index]) for index in [0, 1]]
                    pifpaf_confidence = right_openpifpaf_dict[image][skeleton][joint][2]
                    label = openpifpaf_to_annotation_dict[int(joint)]  # corresponding joint label in annotation
                    annotated_coordinates: object = right_annot_dict[image].get(str(label))  # We use the .get()
                    # method to handle the cases where the annotation does not have a matching joint, aka,
                    # a joint false positive

                    if annotated_coordinates:
                        error = round(math.sqrt(
                            math.pow(pifpaf_coordinates[0] - annotated_coordinates[0], 2) +
                            math.pow(pifpaf_coordinates[1] - annotated_coordinates[1], 2)), 3)
                        skeleton_dict[label] = [error, pifpaf_confidence]  # for each joint, we save its error and
                        # confidence score (so that we can later plot them both)
                        error_total += error
                    else:
                        #  There is no matching joint in the annotation, this is a "false" positive joint.
                        skeleton_dict[label] = ['fp', pifpaf_confidence]  # fp = false positive
                        fp_joint_total += 1

                    joint_counter_total += 1

                # Check if any annotated joints are missing from this skeleton (false negatives)
                for label in right_annot_dict[image]:
                    if int(label) in skeleton_dict:
                        continue
                    else:
                        if label != '1':
                            skeleton_dict[label] = ['fn', 0]
                            fn_joint_total += 1
                        else:  # Because OpenPifPaf does not have a corresponding 'Chest' keypoint (label 1)
                            skeleton_dict[label] = ['invalid', 0]

                # Save in this skeleton's dictionary:
                skeleton_dict['joint_counter_total'] = joint_counter_total
                # Calculate the Mean Per Joint Position Error (in pixels) of this skeleton
                if joint_counter_total != 0:
                    mpjpe = round(error_total / joint_counter_total, 4)
                    skeleton_dict['mpjpe'] = mpjpe
                    skeleton_dict['fp_joint_total'] = fp_joint_total
                    skeleton_dict['fn_joint_total'] = fn_joint_total

                if mpjpe_threshold > mpjpe > 0:  # We include the mpjpe > 0 condition in order to not match false
                    # positive skeletons (which would have error exactly equal to 0 since that is the initial value
                    # of error_total)
                    matching_skeleton_total += 1
                    matching_skeleton_dict[skeleton] = skeleton_dict

        image_dict['pifpaf_skeleton_total'] = pifpaf_skeleton_total
        image_dict['matching_skeleton_total'] = matching_skeleton_total
        image_dict['matching_skeletons'] = matching_skeleton_dict

        # Calculate the metrics of this image:
        joint_image_total = 0
        mpjpe_image_total = 0
        mpjpe_image_average = 0
        fp_joint_image_total = 0
        fn_joint_image_total = 0
        if len(matching_skeleton_dict) != 0:
            for matching_skeleton in matching_skeleton_dict:
                joint_image_total += matching_skeleton_dict[matching_skeleton]['joint_counter_total']
                mpjpe_image_total += matching_skeleton_dict[matching_skeleton]['mpjpe']
                fp_joint_image_total += matching_skeleton_dict[matching_skeleton]['fp_joint_total']
                fn_joint_image_total += matching_skeleton_dict[matching_skeleton]['fn_joint_total']
            mpjpe_image_average = round(mpjpe_image_total / len(matching_skeleton_dict), 3)

        # Save to image metrics to its dictionary
        image_dict['joint_image_total'] = joint_image_total
        image_dict['mpjpe_image_average'] = mpjpe_image_average
        image_dict['fp_joint_image_total'] = fp_joint_image_total
        image_dict['fn_joint_image_total'] = fp_joint_image_total

        # Add to variables that will determine overall metrics for this dataset
        joint_total_right_openpifpaf += joint_image_total
        mpjpe_right_openpifpaf += mpjpe_image_average
        fp_joint_total_right_openpifpaf += fp_joint_image_total
        fn_joint_total_right_openpifpaf += fn_joint_image_total

        results_right_openpifpaf[image] = image_dict

# Overall dataset metrics:
image_total = right_openpifpaf_dict['Total images']
results_right_openpifpaf['joint_total_average_per_image'] = round(joint_total_right_openpifpaf / image_total, 3)
results_right_openpifpaf['mpjpe_average_per_image'] = \
    round(mpjpe_right_openpifpaf / image_total, 3)
results_right_openpifpaf['fp_joint_total_average_per_image'] = round(fp_joint_total_right_openpifpaf / image_total, 3)
results_right_openpifpaf['fn_joint_total_average_per_image'] = round(fn_joint_total_right_openpifpaf / image_total, 3)

if output_flag:
    with open(output_path + '/results_right_openpifpaf.json', 'w', encoding='utf-8') as f:
        json.dump(results_right_openpifpaf, f, ensure_ascii=False, indent=4)

print()
print('Right OpenPifPaf Results json built successfully')


# ============================================================================= OpenPose left-small dataset
results_left_openpose = {}

# Initialize variables that are used to calculate metrics:
joint_total_left_openpose = 0
mpjpe_left_openpose = 0  # Total error for all images in this dataset
fp_joint_total_left_openpose = 0
fn_joint_total_left_openpose = 0

mpjpe_threshold = 50  # This should be a percentage of the bounding box size but we will ballpark to filter out
# false positives for now and then later program an adaptive threshold based on height (ymax-ymin) of the skeleton

for image in left_openpose_dict:
    if image.startswith('left'):  # excludes the keys that are extra information about the number of images
        image_dict = {}

        # Save values related to annotation:
        if len(left_annot_dict[image]) == 0:  # In the annotation, there is either a single skeleton or there is none
            annotated_skeleton_total = 0
            annotated_joint_total = 0
        else:
            annotated_skeleton_total = 1
            annotated_joint_total = len(left_annot_dict[image])
        image_dict['annotated_skeleton_total'] = annotated_skeleton_total
        image_dict['annotated_joint_total'] = annotated_joint_total

        matching_skeleton_total = 0  # the number of skeletons that match with annot (mpjpe is within the threshold)
        # This helps detect cases where the method detects the operator but does not associate all the joints,
        # creating more than one detected skeleton.
        matching_skeleton_dict = {}  # contains dictionaries of each skeleton that matches with annotation

        for skeleton in left_openpose_dict[image]:
            if str(skeleton).startswith('skeleton_number'):  # extract the number of skeletons OpenPose detected
                openpose_skeleton_total = left_openpose_dict[image][skeleton]
            else:  # all other keys are skeletons
                skeleton_dict = {}  # Temporary dict to save this skeleton's results. The key corresponds to the
                # joint, using the annotation label, or relevant variables such as joint_counter_total

                joint_counter_total = 0  # Number of total joints detected by OpenPose
                fp_joint_total = 0  # Number of false positive joints detected by OpenPose (no match in annotation)
                fn_joint_total = 0  # Number of false negative joints (in annotation but not detected by openpose)
                error_total = 0  # Used to calculate mpjpe

                for joint in left_openpose_dict[image][skeleton]:
                    if int(joint) == 8 or int(joint) > 18:  # OpenPose has an extra keypoint between the left and
                        # right hips, labelled 8, as well as foot keypoints, labelled 19 to 24, that we do not consider
                        continue
                    openpose_coordinates = [int(left_openpose_dict[image][skeleton][joint][index]) for index in [0, 1]]
                    openpose_confidence = left_openpose_dict[image][skeleton][joint][2]
                    label = openpose_to_annotation_dict[int(joint)]  # corresponding joint label in annotation
                    annotated_coordinates: object = left_annot_dict[image].get(str(label))  # We use the .get()
                    # method to handle the cases where the annotation does not have a matching joint, aka,
                    # a joint false positive

                    if annotated_coordinates:
                        error = round(math.sqrt(
                            math.pow(openpose_coordinates[0] - annotated_coordinates[0], 2) +
                            math.pow(openpose_coordinates[1] - annotated_coordinates[1], 2)), 3)
                        skeleton_dict[label] = [error, openpose_confidence]  # for each joint, we save its error and
                        # confidence score (so that we can later plot them both)
                        error_total += error
                    else:
                        #  There is no matching joint in the annotation, this is a "false" positive joint.
                        skeleton_dict[label] = ['fp', openpose_confidence]  # fp = false positive
                        fp_joint_total += 1

                    joint_counter_total += 1

                # Check if any annotated joints are missing from this skeleton (false negatives)
                for label in left_annot_dict[image]:
                    if int(label) in skeleton_dict:
                        continue
                    else:
                        skeleton_dict[label] = ['fn', 0]
                        fn_joint_total += 1

                # Save in this skeleton's dictionary:
                skeleton_dict['joint_counter_total'] = joint_counter_total
                # Calculate the Mean Per Joint Position Error (in pixels) of this skeleton
                if joint_counter_total != 0:
                    mpjpe = round(error_total / joint_counter_total, 4)
                    skeleton_dict['mpjpe'] = mpjpe
                    skeleton_dict['fp_joint_total'] = fp_joint_total
                    skeleton_dict['fn_joint_total'] = fn_joint_total

                if mpjpe_threshold > mpjpe > 0:  # We include the mpjpe > 0 condition in order to not match false
                    # positive skeletons (which would have error exactly equal to 0 since that is the initial value
                    # of error_total)
                    matching_skeleton_total += 1
                    matching_skeleton_dict[skeleton] = skeleton_dict

        image_dict['openpose_skeleton_total'] = openpose_skeleton_total
        image_dict['matching_skeleton_total'] = matching_skeleton_total
        image_dict['matching_skeletons'] = matching_skeleton_dict

        # Calculate the metrics of this image:
        joint_image_total = 0
        mpjpe_image_total = 0
        mpjpe_image_average = 0
        fp_joint_image_total = 0
        fn_joint_image_total = 0
        if len(matching_skeleton_dict) != 0:
            for matching_skeleton in matching_skeleton_dict:
                joint_image_total += matching_skeleton_dict[matching_skeleton]['joint_counter_total']
                mpjpe_image_total += matching_skeleton_dict[matching_skeleton]['mpjpe']
                fp_joint_image_total += matching_skeleton_dict[matching_skeleton]['fp_joint_total']
                fn_joint_image_total += matching_skeleton_dict[matching_skeleton]['fn_joint_total']
            mpjpe_image_average = round(mpjpe_image_total / len(matching_skeleton_dict), 3)

        # Save to image metrics to its dictionary
        image_dict['joint_image_total'] = joint_image_total
        image_dict['mpjpe_image_average'] = mpjpe_image_average
        image_dict['fp_joint_image_total'] = fp_joint_image_total
        image_dict['fn_joint_image_total'] = fp_joint_image_total

        # Add to variables that will determine overall metrics for this dataset
        joint_total_left_openpose += joint_image_total
        mpjpe_left_openpose += mpjpe_image_average
        fp_joint_total_left_openpose += fp_joint_image_total
        fn_joint_total_left_openpose += fn_joint_image_total

        results_left_openpose[image] = image_dict

# Overall dataset metrics:
image_total = left_openpose_dict['Total images']
results_left_openpose['joint_total_average_per_image'] = round(joint_total_left_openpose / image_total, 3)
results_left_openpose['mpjpe_average_per_image'] = \
    round(mpjpe_left_openpose / image_total, 3)
results_left_openpose['fp_joint_total_average_per_image'] = round(fp_joint_total_left_openpose / image_total, 3)
results_left_openpose['fn_joint_total_average_per_image'] = round(fn_joint_total_left_openpose / image_total, 3)

if output_flag:
    with open(output_path + '/results_left_openpose.json', 'w', encoding='utf-8') as f:
        json.dump(results_left_openpose, f, ensure_ascii=False, indent=4)

print()
print('Left OpenPose Results json built successfully')


# ======================================================================= OpenPose right-small dataset
results_right_openpose = {}

# Initialize variables that are used to calculate metrics:
joint_total_right_openpose = 0
mpjpe_right_openpose = 0  # Total error for all images in this dataset
fp_joint_total_right_openpose = 0
fn_joint_total_right_openpose = 0

mpjpe_threshold = 50  # This should be a percentage of the bounding box size but we will ballpark to filter out
# false positives for now and then later program an adaptive threshold based on height (ymax-ymin) of the skeleton

for image in right_openpose_dict:
    if image.startswith('right'):  # excludes the keys that are extra information about the number of images
        image_dict = {}

        # Save values related to annotation:
        if len(right_annot_dict[image]) == 0:  # In the annotation, there is either a single skeleton or there is none
            annotated_skeleton_total = 0
            annotated_joint_total = 0
        else:
            annotated_skeleton_total = 1
            annotated_joint_total = len(right_annot_dict[image])
        image_dict['annotated_skeleton_total'] = annotated_skeleton_total
        image_dict['annotated_joint_total'] = annotated_joint_total

        matching_skeleton_total = 0  # the number of skeletons that match with annot (mpjpe is within the threshold)
        # This helps detect cases where the method detects the operator but does not associate all the joints,
        # creating more than one detected skeleton.
        matching_skeleton_dict = {}  # contains dictionaries of each skeleton that matches with annotation

        for skeleton in right_openpose_dict[image]:
            if str(skeleton).startswith('skeleton_number'):  # extract the number of skeletons OpenPose detected
                openpose_skeleton_total = right_openpose_dict[image][skeleton]
            else:  # all other keys are skeletons
                skeleton_dict = {}  # Temporary dict to save this skeleton's results. The key corresponds to the
                # joint, using the annotation label, or relevant variables such as joint_counter_total

                joint_counter_total = 0  # Number of total joints detected by OpenPose
                fp_joint_total = 0  # Number of false positive joints detected by OpenPose (no match in annotation)
                fn_joint_total = 0  # Number of false negative joints (in annotation but not detected by OpenPose)
                error_total = 0  # Used to calculate mpjpe

                for joint in right_openpose_dict[image][skeleton]:
                    if int(joint) == 8 or int(joint) > 18:  # OpenPose has an extra keypoint between the left and
                        # right hips, labelled 8, as well as foot keypoints, labelled 19 to 24, that we do not consider
                        continue
                    openpose_coordinates = [int(right_openpose_dict[image][skeleton][joint][index]) for index in [0, 1]]
                    openpose_confidence = right_openpose_dict[image][skeleton][joint][2]
                    label = openpose_to_annotation_dict[int(joint)]  # corresponding joint label in annotation
                    annotated_coordinates: object = right_annot_dict[image].get(str(label))  # We use the .get()
                    # method to handle the cases where the annotation does not have a matching joint, aka,
                    # a joint false positive

                    if annotated_coordinates:
                        error = round(math.sqrt(
                            math.pow(openpose_coordinates[0] - annotated_coordinates[0], 2) +
                            math.pow(openpose_coordinates[1] - annotated_coordinates[1], 2)), 3)
                        skeleton_dict[label] = [error, openpose_confidence]  # for each joint, we save its error and
                        # confidence score (so that we can later plot them both)
                        error_total += error
                    else:
                        #  There is no matching joint in the annotation, this is a "false" positive joint.
                        skeleton_dict[label] = ['fp', openpose_confidence]  # fp = false positive
                        fp_joint_total += 1

                    joint_counter_total += 1

                # Check if any annotated joints are missing from this skeleton (false negatives)
                for label in right_annot_dict[image]:
                    if int(label) in skeleton_dict:
                        continue
                    else:
                        skeleton_dict[label] = ['fn', 0]
                        fn_joint_total += 1

                # Save in this skeleton's dictionary:
                skeleton_dict['joint_counter_total'] = joint_counter_total
                # Calculate the Mean Per Joint Position Error (in pixels) of this skeleton
                if joint_counter_total != 0:
                    mpjpe = round(error_total / joint_counter_total, 4)
                    skeleton_dict['mpjpe'] = mpjpe
                    skeleton_dict['fp_joint_total'] = fp_joint_total
                    skeleton_dict['fn_joint_total'] = fn_joint_total

                if mpjpe_threshold > mpjpe > 0:  # We include the mpjpe > 0 condition in order to not match false
                    # positive skeletons (which would have error exactly equal to 0 since that is the initial value
                    # of error_total)
                    matching_skeleton_total += 1
                    matching_skeleton_dict[skeleton] = skeleton_dict

        image_dict['openpose_skeleton_total'] = openpose_skeleton_total
        image_dict['matching_skeleton_total'] = matching_skeleton_total
        image_dict['matching_skeletons'] = matching_skeleton_dict

        # Calculate the metrics of this image:
        joint_image_total = 0
        mpjpe_image_total = 0
        mpjpe_image_average = 0
        fp_joint_image_total = 0
        fn_joint_image_total = 0
        if len(matching_skeleton_dict) != 0:
            for matching_skeleton in matching_skeleton_dict:
                joint_image_total += matching_skeleton_dict[matching_skeleton]['joint_counter_total']
                mpjpe_image_total += matching_skeleton_dict[matching_skeleton]['mpjpe']
                fp_joint_image_total += matching_skeleton_dict[matching_skeleton]['fp_joint_total']
                fn_joint_image_total += matching_skeleton_dict[matching_skeleton]['fn_joint_total']
            mpjpe_image_average = round(mpjpe_image_total / len(matching_skeleton_dict), 3)

        # Save to image metrics to its dictionary
        image_dict['joint_image_total'] = joint_image_total
        image_dict['mpjpe_image_average'] = mpjpe_image_average
        image_dict['fp_joint_image_total'] = fp_joint_image_total
        image_dict['fn_joint_image_total'] = fp_joint_image_total

        # Add to variables that will determine overall metrics for this dataset
        joint_total_right_openpose += joint_image_total
        mpjpe_right_openpose += mpjpe_image_average
        fp_joint_total_right_openpose += fp_joint_image_total
        fn_joint_total_right_openpose += fn_joint_image_total

        results_right_openpose[image] = image_dict

# Overall dataset metrics:
image_total = right_openpose_dict['Total images']
results_right_openpose['joint_total_average_per_image'] = round(joint_total_right_openpose / image_total, 3)
results_right_openpose['mpjpe_average_per_image'] = \
    round(mpjpe_right_openpose / image_total, 3)
results_right_openpose['fp_joint_total_average_per_image'] = round(fp_joint_total_right_openpose / image_total, 3)
results_right_openpose['fn_joint_total_average_per_image'] = round(fn_joint_total_right_openpose / image_total, 3)

if output_flag:
    with open(output_path + '/results_right_openpose.json', 'w', encoding='utf-8') as f:
        json.dump(results_right_openpose, f, ensure_ascii=False, indent=4)

print()
print('Right OpenPose Results json built successfully')
