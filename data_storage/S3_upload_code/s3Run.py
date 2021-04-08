import os
import boto3
import time


#AWS_CONFIG_FILE = "/Users/ME/.aws/config"
#AWS_CREDENTIALS_FILE = "/Users/ME/.aws/credentials"

class s3Service:
    def __init__(self):
        self.session = boto3.Session(profile_name= 'default')
        self.client = self.session.client('s3')

    def download(self, bucket, obj, local_file_path):
        self.client.download_file(bucket, obj, local_file_path)

    def upload(self, local_file_path, bucket, obj):
        self.client.upload_file(local_file_path, bucket, obj)

    def makePublicRead(self, bucket, key):
        self.client.put_object_acl(ACL = 'public-read', Bucket = bucket, Key = key)

    def listingFiles(self):
        response = self.session.resource('s3')

        for bucket in response.buckets.all():
            print(bucket.name)


