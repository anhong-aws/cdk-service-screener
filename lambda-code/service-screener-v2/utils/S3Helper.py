import boto3
import os
from botocore.exceptions import ClientError

class S3Helper:
    def __init__(self, bucket_name):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    # 生成下载对象的签名 URL
    def generate_presigned_url_download(self, object_name, expiration=3600):
        """生成一个允许下载对象的签名 URL"""
        response = self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )

        return response
    def upload_file(self, file_path, object_name):
        """Upload a file to an S3 bucket

        :param file_path: File to upload
        :param object_name: S3 object name
        :return: True if file was uploaded, else False
        """
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
        except ClientError as e:
            print(e)
            return False
        return True

    def generate_presigned_url(self, object_name, expiration=3600):
        """Generate a presigned URL to share an S3 object

        :param object_name: S3 object name
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
        except ClientError as e:
            print(e)
            return None

        return response

    def download_file(self, object_name, file_path):
        """Download an S3 object to a file

        :param object_name: S3 object name
        :param file_path: File path to download the object
        :return: True if file was downloaded, else False
        """
        try:
            self.s3_client.download_file(self.bucket_name, object_name, file_path)
        except ClientError as e:
            print(e)
            return False
        return True
