# 유니톤 9팀 착!붙 - 백엔드

폴더 구성

CatVTON - ML 코드 폴더

ChakBootBackend - 추론 기능 외 url 공유 기능 등 백엔드 기능

ChakBootInferenceServer - AI 추론 기능만 담당

# AI 추론 데모

실행할시 말하고 실행요망

```
curl -v -X POST \
  -F "img1=@CatVTON/my_test/wonyeong.png" \
  -F "img2=@CatVTON/my_test/cloth12.png" \
  https://home.goldenmine.kr/chakbootdirect/predict/ > received_image.png
```
