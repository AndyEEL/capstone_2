from s3Run import s3Service
import sys
import os
import glob
from PIL import Image

#1. 터미널 실행 - 패키지 설치
#   pip install SDK
#   pip install boto3
#   pip install pillow
#   pip install image
#   pip install glob

#2. 이미지 폴더 경로 입력
#   ** 주의 : 끝에 / 이 들어가면 안됨! **
#   예) /Users/ME/Desktop/Crawling_result

#img_root_dir = "[YOUR PATH]"
#img_root_dir = "/Users/ME/Desktop/awsTest"

#3. 이니셜 입력 예) 오주봉 -> jb
username = "Jun"

if len(sys.argv) < 2:
    print("Need 2 parameters to run. "
          "첫번째 : [upload / resize / download], "
          "두번째 : 해당 파일 경로 " )
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


def checkRoot(file_path):
    subfolder_list = os.listdir(file_path)
    folder = file_path.split(os.path.sep)

    print("작업 예정 폴더 : " + folder[-1])
    print("리사이징 대상 폴더들 : ")
    if len(subfolder_list) > 10:
        for i in range(0,10):
            print(subfolder_list[i])
    else:
        print(subfolder_list)

    ans = input("진행하시겠습니까? (Y/N)")

    if ans.lower() == "n":
        sys.exit()



''' ------- main ------ '''


#파일 크기 줄이기

command = sys.argv[1]
img_root_dir = sys.argv[2]

if command.lower() != "resize":
    print("현재는 resize만 가능합니다.")
    sys.exit()
else:
    checkRoot(sys.argv[2])
    imgResize(img_root_dir)


'''

s3 = s3Service()
bucket = "capstone-proj"
key_dir = "FoodImages/"
obj_upload_dir = "FoodImages/"
obj_download_dir = "/Users/ME/Desktop/awsTest_download/"

error_folder = []
error_file = {}


#upload files

folder_list = os.listdir(img_root_dir)
floder_list = folder_list[1:]

print("파일 업로드를 시작합니다. ")
for folder in folder_list:
    print(folder + " 폴더 업로드 시작..")
    try:
        file_list = os.listdir(img_root_dir + "/" + folder)

        for filename in file_list:
            file = os.path.splitext(filename)[0] + "_" + username + os.path.splitext(filename)[1]
            local_file_path = img_root_dir + "/" + folder + "/" + filename
            upload_file_path = obj_upload_dir + folder + "/" + filename

            try:
                s3.upload(local_file_path, bucket, upload_file_path)
            except:
                print("s3 파일 upload error : " + folder + "/" + filename)
                if folder in error_file:
                    error_file[folder].append(filename)
                else:
                    error_file[folder] = [filename]

    except NotADirectoryError as e:
        print(folder + "is not a directory ERROR. 폴더를 건너 뜁니다.")
        error_folder.append(folder)
        continue

    except:
        print(folder + " unknown ERROR. 폴더를 건너 뜁니다.")
        error_folder.append(folder)
        continue

    print(folder + " 작업완료\n")

print("upload all the file success.")


#버킷 파일 목록 확인하기
#s3.listingFiles()

# make the file public
 #   if int(sys.argv[2]) == 1:
 #       s3.makePublicRead(bucket, key_dir + filename)


# download files

if int(sys.argv[2]) == 1:
    try:
        for filename in file_list:
            local_file_path = img_root_dir + filename
            s3.download(bucket, obj_upload_dir + filename, obj_download_dir + filename)

        print("download all the files success.")
    except:
        print("download failed.")


# error file & folder 텍스트 파일로 올리기
if len(error_folder) > 0 or len(error_file) > 0:
    with open("error_list.txt", mode = "wt", encoding= "utf-8") as o:
        o.write("--- 업로드 실패한 폴더 리스트 ---\n")
        for folder in error_folder:
            o.write(folder +"\n")

        o.write("\n\n--- 업로드 실패한 파일 리스트 ---\n")
        for folder, file in error_file.items():
            o.write(folder + "/" + file + "\n")

'''