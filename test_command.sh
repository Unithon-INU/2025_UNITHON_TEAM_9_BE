# 실행할거면 말하고 실행요망
curl -v -X POST \
  -F "img1=@CatVTON/my_test/wonyeong.png" \
  -F "img2=@CatVTON/my_test/cloth12.png" \
  https://home.goldenmine.kr/chakbootdirect/predict/ > received_image.png