from s3Run import s3Service
import sys
import os
import glob
from PIL import Image

#1. 터미널 실행 - 패키지 설치
#   pip install pillow
#   pip install image
#   pip install glob

#2. 이미지 폴더 경로 입력
#   ** 주의 : 끝에 / 이 들어가면 안됨! **
#   예) /Users/ME/Desktop/Crawling_result

img_root_dir = "[YOUR PATH]"



if len(sys.argv) <= 2:
    print("Need 3 parameters to run. "
          "첫번째 : 파일 업로드, "
          "두번째 : 파일 다운로드, "
          "세번째 : 이미지 사이즈 줄일거야? ")
    sys.exit()


def imgResize(img_root_dir):
    img_file_list = os.listdir(img_root_dir)

    for menu in img_file_list:
        files = glob.glob(img_root_dir + "/" + menu + "/*.jpg")
        print(menu + " 사진들을 리사이징합니다. ")
        for f in files:
            title, ext = os.path.splitext(f)
            if ext in ['.jpg', '.png']:
                try:
                    img = Image.open(f)
                    img = img.convert("RGB")
                    img_resize = img.resize((int(img.width / 2), int(img.height / 2)))
                    while img_resize.width > 700 and img_resize.height > 700:
                        img_resize = img_resize.resize((int(img_resize.width / 2), int(img_resize.height / 2)))
                    title, ext = os.path.splitext(f)
                    img_resize.save(title + ext)

                except OSError as e:
                    pass
        print(menu + " 리사이징 성공.")


#파일 크기 줄이기

if sys.argv[3] == 1:
    imgResize(img_root_dir)



s3 = s3Service()
bucket = "capstone-khu"
key_dir = "2021/04-05/"
obj_upload_dir = "2021/04-05/"
obj_download_dir = "/Users/ME/Desktop/awsTest/"


#upload files
#/Users/ME/Desktop/Works/Major/Business/Capston Project/git/capstone_2/Crawling_result
if sys.argv[1] == 1:
    file_list = os.listdir(img_root_dir)

    print("파일 업로드를 시작합니다. ")
    for filename in file_list:
        print(filename + " 폴더 업로드 시작..")

        ''' 여기 더 손 봐야함 '''
        local_file_path = img_root_dir + filename
        s3.upload(local_file_path, bucket, obj_upload_dir + filename)

        # make the file public
        if int(sys.argv[2]) == 1:
            s3.makePublicRead(bucket, key_dir + filename)

        print("upload all the file success.")


# download files
if int(sys.argv[2]) == 1:
    try:
        for filename in file_list:
            local_file_path = img_root_dir + filename
            s3.download(bucket, obj_upload_dir + filename, obj_download_dir + filename)

        print("download all the files success.")
    except:
        print("download failed.")


