import traceback
from io import BytesIO

import torch
import os
import time

from PIL import Image
from .image_correction import enhance
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

            # img1 = make_square_advanced(img1)
            img1 = enhance(img1)
            
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


# import traceback
# from io import BytesIO

# import os
# import time
# from PIL import Image

# from .image_correction import enhance  # ← 오타 수정 주의: correctcion → correction
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from util.image_util import convert_multipart_to_pillow

# LOCK_FILE = "/tmp/inference_lock.lock"
# LOCK_TIMEOUT = 3  # 락 획득 시도 최대 시간 (초)


# @csrf_exempt
# def inference_catvton(request):
#     if request.method == 'POST':
#         lock_acquired = False
#         try:
#             # 락 획득 시도
#             start_time = time.time()
#             while time.time() - start_time < LOCK_TIMEOUT:
#                 try:
#                     fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL)
#                     os.close(fd)
#                     lock_acquired = True
#                     break
#                 except FileExistsError:
#                     time.sleep(0.1)

#             if not lock_acquired:
#                 return HttpResponse('Another inference is currently running. Please try again later.', status=429)

#             img1_file = request.FILES.get('img1')

#             if not img1_file:
#                 return HttpResponse('img1 is required.', status=400)

#             img1 = convert_multipart_to_pillow(img1_file)
#             img1 = enhance(img1)  # 보정만 적용

#             buffer = BytesIO()
#             img1.save(buffer, format='PNG')  # 보정된 img1 저장
#             buffer.seek(0)

#             return HttpResponse(buffer, content_type='image/png')

#         except Exception as e:
#             traceback.print_exc()
#             return HttpResponse(f'Error: {str(e)}', status=500)
#         finally:
#             if lock_acquired and os.path.exists(LOCK_FILE):
#                 os.remove(LOCK_FILE)

#     return HttpResponse('Only POST allowed.', status=405)


# def hello_world(request):
#     return HttpResponse("Hello, World!")


# 고급 버전 - 배경색 및 이미지 모드 옵션 추가
def make_square_advanced(img_input, bg_color='white'):
    """
    이미지를 정사각형으로 만드는 고급 함수
    
    Args:
        img_input (str or PIL.Image): 이미지 경로 또는 PIL Image 객체
        bg_color (str or tuple): 배경색 ('white', 'black' 또는 RGB 튜플)
        
    Returns:
        PIL.Image: 1:1 비율로 변환된 이미지 객체
    """
    # 입력이 문자열(경로)인 경우 이미지 열기
    if isinstance(img_input, str):
        img = Image.open(img_input)
    else:
        img = img_input.copy()  # 원본 보존을 위해 복사
    
    width, height = img.size
    
    # 더 긴 쪽을 기준으로 정사각형 크기 결정
    square_size = max(width, height)
    
    # 새로운 정사각형 이미지 생성
    # RGBA 모드로 생성 후 배경색 설정
    if img.mode == 'RGBA':
        if bg_color == 'white':
            bg_color = (255, 255, 255, 255)
        elif bg_color == 'black':
            bg_color = (0, 0, 0, 255)
        square_img = Image.new('RGBA', (square_size, square_size), bg_color)
    else:
        square_img = Image.new('RGB', (square_size, square_size), bg_color)
    
    # 원본 이미지를 중앙에 배치
    x_offset = (square_size - width) // 2
    y_offset = (square_size - height) // 2
    
    # 투명도가 있는 이미지의 경우 알파 채널 고려
    if img.mode == 'RGBA':
        square_img.paste(img, (x_offset, y_offset), img)
    else:
        square_img.paste(img, (x_offset, y_offset))
    
    print(f"변환 완료: {width}x{height} → {square_size}x{square_size}")
    return square_img