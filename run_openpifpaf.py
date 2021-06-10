from PIL import Image
import glob
import openpifpaf
import json
from timeit import default_timer as timer

# === Run Variables (change these accordingly): === #
run_number = 17
model = 'shufflenetv2k16'  # pre-trained models available: resnet50, shufflenetv2k16 (chosen) and shufflenetv2k30
# (performance metrics are available in the introduction page of the OpenPifPaf guide)
dataset = 'left-small'
create_images = False
controlled_setup = True

# Additional path variables
dataset_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/' + dataset
file_extension = '/*.jpg'  # type of file (change accordingly)
output_path = '/home/eduardocaldasfonseca/Desktop/cobot-monitor-dataset/openpifpaf_output/run' + str(run_number)

# dictionary to build meta json that contains execution times and other information about the run
meta = {'Run Number': run_number,
        'OpenPifPaf version': str(openpifpaf.__version__),
        'Model': model,
        'Dataset': dataset,
        'With image creation?': create_images,
        'Controlled setup?': controlled_setup}

# === Create list containing all images of dataset: === #
image_list = []  # empty list for all the images in dataset_path
for file in glob.glob(dataset_path + file_extension):
    im = Image.open(file)
    image_list.append(im)

# === Initialize OpenPifPaf Predictor and timers === #
predictor = openpifpaf.Predictor(checkpoint=model)#, json_data=not create_images)  # the flag json_data changes the
# predictions list to be json data instead of the annotations object (preventing the use of the annotation painter)
start_total = timer()  # start total timer (includes additional operations so it's not very accurate)
times = {}

for image in image_list:
    output_filename = image.filename.replace(dataset_path, '')
    start = timer()  # start timer for this image
    predictions, gt_anns, image_meta = predictor.pil_image(image)
    end = timer()  # end timer for this image
    times[output_filename] = str(end - start)  # saves execution time for this image in meta json

    with open(output_path + output_filename + '_pifpaf_run' + str(run_number) + '_keypoints.json', 'w',
              encoding='utf-8') as f:
        json.dump([ann.json_data() for ann in predictions], f, ensure_ascii=False, indent=4)

    if create_images:  # outputs images with skeleton overlayed
        annotation_painter = openpifpaf.show.AnnotationPainter()
        with openpifpaf.show.image_canvas(image, output_path + output_filename + '_pifpaf_run' + str(run_number) + '_rendered.jpg') as ax:
            annotation_painter.annotations(ax, predictions)


end_total = timer()  # end total timer
meta['Times'] = times
meta['Total time'] = str(end_total - start_total)
with open(output_path + '/pifpaf_run' + str(run_number) + '_meta.json', 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=4)
