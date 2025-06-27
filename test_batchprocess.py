from pathlib import Path
from PIL import Image
import requests
from tqdm import tqdm


def convert_jpg_to_png(folder):
    for img_path in folder.rglob('*'):
        if img_path.suffix.lower() in ['.jpg', '.jpeg']:
            img = Image.open(img_path)
            png_path = folder / (img_path.stem + '.png')
            img.save(png_path)
            print(f'변환 완료: {img_path} -> {png_path}')


def main():
    model_folder = Path('model')
    cloth_folder = Path('cloth')
    result_folder = Path('result')
    result_folder.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 생성

    # api가 png만 지원하므로 png 생성
    convert_jpg_to_png(model_folder)
    convert_jpg_to_png(cloth_folder)

    # batch process
    model_files = list(model_folder.rglob('*.png'))
    cloth_files = list(cloth_folder.rglob('*.png'))

    for model_file, cloth_file in (pg_bar := tqdm([(m, c) for m in model_files for c in cloth_files], desc='Batch Progress', ncols=150)):
        # set description
        result_file = result_folder / (model_file.stem + '_' + cloth_file.stem + '.png')
        pg_bar.set_description(result_file.name)

        # fetch result
        request(model_file, cloth_file, result_file)


def request(model_file, cloth_file, result_file):
    url = 'https://home.goldenmine.kr/chakbootdirect/predict/'

    files = {
        'img1': open(model_file, 'rb'),
        'img2': open(cloth_file, 'rb')
    }

    response = requests.post(url, files=files)

    # 받은 이미지를 저장
    with open(result_file, 'wb') as f:
        f.write(response.content)


if __name__ == '__main__':
    main()