import io
import numpy as np
import PIL
import openpifpaf
import requests
import torch
import IPython

print('OpenPifPaf version', openpifpaf.__version__)
print('PyTorch version', torch.__version__)

#

image_response = requests.get('https://raw.githubusercontent.com/openpifpaf/openpifpaf/main/docs/coco/000000081988.jpg')
pil_im = PIL.Image.open(io.BytesIO(image_response.content)).convert('RGB')
im = np.asarray(pil_im)

predictor = openpifpaf.Predictor(checkpoint='shufflenetv2k16')
predictions, gt_anns, image_meta = predictor.pil_image(pil_im)

annotation_painter = openpifpaf.show.AnnotationPainter()
with openpifpaf.show.image_canvas(im) as ax:
    annotation_painter.annotations(ax, predictions)
