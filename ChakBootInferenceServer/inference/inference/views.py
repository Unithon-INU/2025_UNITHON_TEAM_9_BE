import traceback
from io import BytesIO

import torch
import os
import time
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from inference_one import inference_model
from util.image_util import convert_multipart_to_pillow

LOCK_FILE = "/tmp/inference_lock.lock"
LOCK_TIMEOUT = 3  # 락 획득 시도 최대 시간 (초)


@csrf_exempt
def inference_catvton(request):
    if request.method == 'POST':
        lock_acquired = False
        try:
            # 락 획득 시도
            start_time = time.time()
            while time.time() - start_time < LOCK_TIMEOUT:
                try:
                    # 파일이 없으면 생성 (O_CREAT | O_EXCL 조합으로 원자적 생성 보장)
                    fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL)
                    os.close(fd)
                    lock_acquired = True
                    break
                except FileExistsError:
                    time.sleep(0.1)  # 잠시 대기 후 재시도

            if not lock_acquired:
                return HttpResponse('Another inference is currently running. Please try again later.', status=429)  # Too Many Requests

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
        finally:
            # 락 해제
            if lock_acquired and os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

    return HttpResponse('Only POST allowed.', status=405)


def hello_world(request):
    return HttpResponse("Hello, World!")
