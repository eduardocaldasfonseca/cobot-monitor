import cv2
import glob


# images = [cv2.imread(file) for file in glob.glob("path/to/files/*.png")]

# Path to directory
left_path = glob.glob("/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/left/*.jpg")
right_path = glob.glob("/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/right/*.jpg")

# Image Arrays:
left_dataset, right_dataset = [], []
left_small_dataset, right_small_dataset = [], []

# Loading original image datasets (3840 x 2160)
for img in left_path:
    n = cv2.imread(img)
    left_dataset.append(n)

    # Resize images to one third of the resolution (1280 × 720) - we keep the same aspect ratio
    new = cv2.resize(n, (0, 0), fx=(1 / 3), fy=(1 / 3))
    left_small_dataset.append(new)

print('Left folder loaded and resized')

for img in right_path:
    n = cv2.imread(img)
    right_dataset.append(n)

    # Resize images to one third of the resolution (1280 × 720) - we keep the same aspect ratio
    new = cv2.resize(n, (0, 0), fx=(1 / 3), fy=(1 / 3))
    right_small_dataset.append(new)

print('Right folder loaded and resized')

i = 1
for n in left_small_dataset:
    cv2.imwrite('/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/left-small/left-small' + str(i) + '.jpg', n)
    i += 1

i = 1
for n in right_small_dataset:
    cv2.imwrite('/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/right-small/right-small' + str(i) + '.jpg', n)
    i += 1

print("Images printed. Done.")
