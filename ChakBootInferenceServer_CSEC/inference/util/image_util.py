from PIL import Image
from io import BytesIO


def convert_multipart_to_pillow(multipart_image):
    multipart_image.seek(0)  # 반드시 필요
    # InMemoryUploadedFile → BytesIO로 래핑
    image = Image.open(BytesIO(multipart_image.read()))
    image = image.convert('RGB')  # PNG나 기타 포맷 대비
    return image
