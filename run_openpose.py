import sys
import cv2
import argparse
import json
from timeit import default_timer as timer

# === Import Openpose === #
try:
    sys.path.append('/home/eduardocaldasfonseca/openpose/build/python')  # change this path accordingly
    from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Check if path is correct.')
    raise e

# === Run Variables (change these accordingly): === #
run_number = 14
model = 'BODY_25'  # pre-trained models available: 'BODY_25' (fastest, most accurate and includes foot keypoints),
# `COCO` (18 keypoints), `MPI` (15 keypoints, least accurate model but fastest on CPU)
dataset = 'right-small'
create_images = False
controlled_setup = True
max_n_people = -1
net_resolution = '-1x368'  # Default number -1x368

# Additional path variables
dataset_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/' + dataset
file_extension = 'jpg'  # type of file (change accordingly)
output_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/openpose_output/run' + str(run_number)

# dictionary to build meta json that contains execution times and other information about the run
meta = {'Run Number': run_number,
        'OpenPose version': 'check individual json files',
        'Model': model,
        'Dataset': dataset,
        'With image creation?': create_images,
        'Controlled setup?': controlled_setup,
        'Number people max flag': max_n_people,
        'Net resolution flag': net_resolution}

try:
    # === Flags === #
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default=dataset_path)
    parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
    args = parser.parse_known_args()

    # === Custom Parameters (refer to /include/openpose/flags.hpp for more parameters) === #
    params = dict()
    params["model_folder"] = "/home/eduardocaldasfonseca/openpose/models/"
    params["number_people_max"] = max_n_people  # This parameter will limit the maximum number of people detected,
    # by keeping the people with the top scores (based on person area over the image, body part score, and joint score.
    # The default -1 keeps them all.
    params["fps_max"] = -1  # Maximum processing frame rate. By default (-1), will process frames as fast as possible.
    params["model_pose"] = model  # Model to be used
    params["net_resolution"] = net_resolution  # Increasing may increase accuracy. Decreasing will increase speed
    # params["display"] = 0  # No display since visual output is not required. (-1 is default for automatic selection)

    # === Output Parameters === #
    if create_images:
        params["write_images"] = output_path  # Directory to write rendered frames
        params["write_images_format"] = file_extension
    params["write_json"] = output_path  # .json output

    # === Add images from directory === #
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1]) - 1:
            next_item = args[1][i + 1]
        else:
            next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-', '')
            if key not in params:
                params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-', '')
            if key not in params:
                params[key] = next_item

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Read frames on directory
    imagePaths = op.get_images_on_directory(args[0].image_dir)
    times = {}  # dictionary to build execution times json
    start_total = timer()

    # Process and display images
    for imagePath in imagePaths:
        datum = op.Datum()
        imageToProcess = cv2.imread(imagePath)
        datum.name = imagePath.replace(args[0].image_dir, '')  # defines the name of the outputs using the original
        # file name
        datum.cvInputData = imageToProcess
        start = timer()
        opWrapper.emplaceAndPop(op.VectorDatum([datum]))
        end = timer()
        times[str(datum.name)] = str(end - start)
        # print("Total time: " + str(end - start) + " seconds")
        # print("Body keypoints: \n" + str(datum.poseKeypoints))

    # print("OpenPose demo successfully finished. Total time: " + str(end_total - start_total) + " seconds")
    end_total = timer()
    meta['Times'] = times
    meta['Total time'] = str(end_total - start_total)
    with open(output_path + '/openpose_run' + str(run_number) + '_meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)

except Exception as e:
    print(e)
    sys.exit(-1)
