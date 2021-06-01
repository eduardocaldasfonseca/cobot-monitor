import sys
import cv2
import argparse
from timeit import default_timer as timer

# === Import Openpose === #
try:
    sys.path.append('/home/eduardocaldasfonseca/openpose/build/python')  # change this path accordingly
    from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Check if path is correct.')
    raise e

try:
    # === Flags === #
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default="/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/test")  #
    # change this path accordingly
    parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
    args = parser.parse_known_args()

    # === Custom Parameters (refer to /include/openpose/flags.hpp for more parameters) === #
    params = dict()
    params["model_folder"] = "/home/eduardocaldasfonseca/openpose/models/"
    params["number_people_max"] = -1  # This parameter will limit the maximum number of people detected, by keeping
    # the people with the top scores (based on person area over the image, body part score, and joint score.
    # The default -1 keeps them all.
    params["fps_max"] = -1  # Maximum processing frame rate. By default (-1), will process frames as fast as possible.
    params["model_pose"] = "BODY_25"  # Model to be used: 'BODY_25' (fastest, most accurate and includes foot
    # keypoints), `COCO` (18 keypoints), `MPI` (15 keypoints, least accurate model but fastest on CPU)
    params["net_resolution"] = "-1x368"  # Default. Increasing will potentially increase accuracy. Decreasing will
    # increase speed
    # params["display"] = 0  # No display since visual output is not required. (-1 is default for automatic selection)

    # === Output Parameters === #
    params["write_images"] = "/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/openpose_output"  # Directory
    # to write rendered frames
    params["write_images_format"] = "jpg"
    params["write_json"] = "/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/openpose_output"  # .json output

    # === Add other images from directory === #
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

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Read frames on directory
    imagePaths = op.get_images_on_directory(args[0].image_dir)
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
        print("Total time: " + str(end - start) + " seconds")

        # print("Body keypoints: \n" + str(datum.poseKeypoints))

        # if not args[0].no_display:
        #     cv2.imshow("OpenPose 1.7.0 - Python API Test", datum.cvOutputData)
        #     key = cv2.waitKey(15)
        #     if key == 27: break

    end_total = timer()
    print("OpenPose demo successfully finished. Total time: " + str(end_total - start_total) + " seconds")

except Exception as e:
    print(e)
    sys.exit(-1)
