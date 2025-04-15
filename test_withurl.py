import requests
import base64


def main():
    url = "https://home.goldenmine.kr/chakboot/ai/predict"
    image_path1 = "CatVTON/my_test/wonyeong.png"  # 실제 이미지 파일 경로로 변경
    image_path2 = "CatVTON/my_test/cloth12.png"  # 실제 이미지 파일 경로로 변경

    try:
        with open(image_path1, 'rb') as img_file1:
            img_content1 = img_file1.read()

        with open(image_path2, 'rb') as img_file2:
            img_content2 = img_file2.read()

        files = {
            'img1': (image_path1.split('/')[-1], img_content1, 'image/png'),
            'img2': (image_path2.split('/')[-1], img_content2, 'image/png')
        }

        response = requests.post(url, files=files)
        response.raise_for_status()  # 응답 상태 코드가 200번대가 아니면 예외 발생

        data = response.json()
        base64_image = data['imageBase64']
        returned_url = data['url']

        if base64_image:
            # Base64 디코딩
            img_data = base64.b64decode(base64_image)

            # 이미지 파일로 저장
            with open("received_image.png", "wb") as f:
                f.write(img_data)
            print("이미지 저장 완료: received_image.png")
        else:
            print("응답에 imageBase64 데이터가 없습니다.")

        if returned_url:
            print(f"URL: https://home.goldenmine.kr/chakboot/ai/url/{returned_url}")
        else:
            print("응답에 url 데이터가 없습니다.")

    except FileNotFoundError as e:
        print(f"파일을 찾을 수 없습니다: {e}")
    except requests.exceptions.RequestException as e:
        print(f"요청 오류: {e}")
    except Exception as e:
        print(f"기타 오류 발생: {e}")


if __name__ == '__main__':
    main()
