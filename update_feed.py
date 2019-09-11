import json
import boto3
from botocore.exceptions import ClientError

class S3_Manipulation():
    def __init__(self, new_ip='169.254.1.1/32'):
        self.ip_list = []
        self.bucket_name = 'name_of_the_bucket_you_want_to_use'
        # object name is the key that will be used to pull and/or create (if non existent) the object in the S3 bucket
        self.object_name = 'name_of_the_file_you_want_in_s3'
        # in case this gets called with no event body we set it previously 169.254.1.1/32
        self.new_ip = new_ip
        # create the s3 object to use in pull and push
        self.s3 = boto3.resource("s3")

    def do_work(self):
        '''
        calls the things and gets it done
        :return:
        '''
        self.download_file()
        self.upload_file()

    def download_file(self):
        '''
        Pulls existing s3 object and gets info from it
        '''
        try:
            # need to pull in the ip info into a list
            object = self.s3.Object(self.bucket_name, self.object_name)
            self.ip_list = object.get()['Body'].read().decode('utf-8').split('\n')
            # do a little cleanup of blank objects
            for i in self.ip_list:
                if i == '':
                    self.ip_list.remove(i)
            # append the new item
        except ClientError as ce:
            print('no such key {key} so this will be created'.format(key=self.object_name))
        finally:
            self.ip_list.append(self.new_ip)

    def upload_file(self):
        '''
        Uploads the file after the new ip is added to the list
        :return:
        '''
        # need to get list objects into a long string to encode it
        ip_list_string = ''
        for ip in self.ip_list:
            ip_list_string += '{ip}\n'.format(ip=ip)
        # then convert to utf-8
        encoded_string = ip_list_string.encode("utf-8")

        s3 = boto3.resource("s3")
        s3.Bucket(self.bucket_name).put_object(Key=self.object_name, Body=encoded_string,
                                               ContentType='text/plain')


def lambda_handler(event, context):
    # create an instance of the class and do the work!
    src_ip = event['data']['rawlog']['srcip']
    s3_client_work = S3_Manipulation(src_ip)
    s3_client_work.do_work()
    return {
        'statusCode': 200
    }
