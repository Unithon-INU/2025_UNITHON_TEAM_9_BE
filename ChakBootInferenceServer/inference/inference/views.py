import traceback
from io import BytesIO

import torch
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from inference_one import inference_model
from util.image_util import convert_multipart_to_pillow


@csrf_exempt
def inference_catvton(request):
    if request.method == 'POST':
        try:
            img1_file = request.FILES.get('img1')
            img2_file = request.FILES.get('img2')

            if not img1_file or not img2_file:
                return HttpResponse('Both img1 and img2 are required.', status=400)

            img1 = convert_multipart_to_pillow(img1_file)
            img2 = convert_multipart_to_pillow(img2_file)

            with torch.no_grad():
                output = inference_model(
                    img1,
                    img2,
                    num_inference_steps=25,
                )

            buffer = BytesIO()
            output.save(buffer, format='PNG')
            buffer.seek(0)

            return HttpResponse(buffer, content_type='image/png')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse(f'Error: {str(e)}', status=500)

    return HttpResponse('Only POST allowed.', status=405)


def hello_world(request):
    return HttpResponse("Hello, World!")
