import os
from io import BytesIO

import torch
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from CatVTON.inference_one import inference_model

# 모델 로딩
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../MY_MODEL/model.pt'))
model = torch.load(MODEL_PATH, map_location=DEVICE)
model.eval()


@csrf_exempt
def inference_catvton(request):
    if request.method == 'POST':
        try:
            img1_file = request.FILES.get('img1')
            img2_file = request.FILES.get('img2')

            if not img1_file or not img2_file:
                return HttpResponse('Both img1 and img2 are required.', status=400)

            img1 = Image.open(img1_file)
            img2 = Image.open(img2_file)

            with torch.no_grad():
                output = inference_model(
                    img1,
                    img2,
                )

            buffer = BytesIO()
            output.save(buffer, format='JPG')
            buffer.seek(0)

            return HttpResponse(buffer, content_type='image/jpeg')
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)

    return HttpResponse('Only POST allowed.', status=405)


def hello_world(request):
    return HttpResponse("Hello, World!")
