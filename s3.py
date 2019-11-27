import boto3
from uuid import uuid4
from werkzeug.utils import secure_filename


def s3_upload(file,base_file_name):
    bucket_name = 'dhcba'
    s3 = boto3.resource(
        's3',
        aws_access_key_id='AKIAJD76T7P7ECXLHHBA',
        aws_secret_access_key='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'
    ).Bucket(bucket_name)
    data = file.stream.read()
    s3.put_object(Key=base_file_name, Body=data)
    return True


def s3_delete(base_file_name):
    bucket_name = 'dhcba'
    s3 = boto3.client(
        's3',
        aws_access_key_id='AKIAJD76T7P7ECXLHHBA',
        aws_secret_access_key='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'
    )
    s3.delete_object(Bucket=bucket_name,Key=base_file_name)
    return True
