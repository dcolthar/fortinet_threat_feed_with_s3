import json
import boto3
from botocore.vendored import requests

class S3_Manipulation():
    def __init__(self, new_ip='169.254.1.1/32'):
        self.ip_list = []
        self.bucket_name = 'name_of_the_bucket_you_want_to_use'
        self.object_name = 'name_of_the_file_you_want_in_s3'
        # the object_url is the full url including object of the dynamic threat feed list you want to use
        # this is used to pull in the existing list and append to it when the API hits, if the file does not exist
        # then the object will be created based on the bucket name and object name
        self.object_url = 'https://full_url_of_the_bucket_and_object_to_pull_from'
        # in case this gets called with no event body we set it previously 169.254.1.1/32
        self.new_ip = new_ip

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
        :return: status_code
        '''
        # need to pull in the ip info into a list
        results = requests.get(self.object_url)

        # now need to do things depending on if we have a list or not, if we get a 200 file exists already
        if results.status_code == 200:
            # split the results into our list
            self.ip_list = results.text.split('\n')
            # append the new IP to the list
            self.ip_list.append(self.new_ip)
            # return the status code
            return
        # 403 should mean file not found so needs created but no existing list to iterate through
        elif results.status_code == 403:
            print(results.status_code)
            # we don't have a file already so need to just create one anyhow
            # append the new IP to the list
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
