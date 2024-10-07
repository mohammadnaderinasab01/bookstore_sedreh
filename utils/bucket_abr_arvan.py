from django.conf import settings
import requests, boto3


AWS_LOCAL_STORAGE_BOOKS = './books'

class BooksBucket:
    def __init__(self):
        print("books bucket init... ")
        try:
            self.s3_client = boto3.client(
                settings.AWS_SERVICE_NAME,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as exc:
            print(exc)

    def DownloadFile(self, src_file_path, dest_file_name):

        object_name =f'{AWS_LOCAL_STORAGE_BOOKS}{dest_file_name}'

        file = requests.get(src_file_path, allow_redirects=True)

        self.s3_client.put_object(
                ACL='public-read',
                Body=file.content,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=object_name
        )


    def UploadFile(self, src_file_path, filename):
        object_name =f'books/{filename}'
        self.s3_client.put_object(
                ACL='private',
                Body=src_file_path,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=object_name
        )


    def GetDownloadLink(self, filename, ex_in = 3600):
        object_name =f'books/{filename}'
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': object_name
                },
                ExpiresIn=ex_in
            )
            return response
        except:
            print("error")
            return None


    def deleteFile(self, file_name):
        try:
            self.s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=f'books/{file_name}'
            )
        except Exception as e:
            print(e)