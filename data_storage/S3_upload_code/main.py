from s3Run import s3Service
import sys
import os
import glob


if len(sys.argv) <= 2:
    print("Need 3 parameters to run. "
          "첫번째 : local file path"
          "두번째 : whether to upload the file from s3"
          "세번째 : whether to upload the file from s3")

    sys.exit()

s3 = s3Service()
bucket = "capstone-khu"
key_dir = "2021/04-05/"
obj_upload_dir = "2021/04-05/"
obj_download_dir = "/Users/ME/Desktop/awsTest/"

#upload files

path_dir = sys.argv[1] # "/Users/ME/Desktop/awsTest"
file_list = os.listdir(path_dir)

for filename in file_list:
    local_file_path = path_dir + filename
    s3.upload(local_file_path, bucket, obj_upload_dir + filename)

    # make the file public
    if int(sys.argv[2]) == 1:
        s3.makePublicRead(bucket, key_dir + filename)

    print("upload all the file success.")


# download files
if int(sys.argv[3]) == 1:
    try:
        for filename in file_list:
            local_file_path = path_dir + filename
            s3.download(bucket, obj_upload_dir + filename, obj_download_dir + filename)

        print("download all the files success.")
    except:
        print("download failed.")
