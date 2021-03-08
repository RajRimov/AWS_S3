#!/usr/bin/env python
import re
import os
import sys
import logging
import datetime as dt
import time
import threading
from botocore.client import Config
from botocore.exceptions import EndpointConnectionError, ClientError
import boto3
import argparse

def output_Log(message, debugMode = False):
    if debugMode:
        logging.error(message)
    else:
        print message

parser = argparse.ArgumentParser(description='Logging Mode')
parser.add_argument('--debug_mode', dest='mode', action='store_false', default=False)
parser.add_argument('--log_mode', dest='mode', action='store_true', default=False)
# get Logging Mode
args = parser.parse_args()
AWS_ACCESS_KEY = 'AKIAVAS7IRGDICP3DB7S'
AWS_ACCESS_SECRET_KEY = '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'


bucket_name = 'myjpgbucket1'

root_dir = os.getcwd()
image_path = "Image"
image_path = os.path.join(root_dir, image_path)
log_path = "log"
log_path = os.path.join(root_dir, log_path)

if not os.path.exists(image_path):
    os.makedirs(image_path)
if not os.path.exists(log_path):
    os.makedirs(log_path)
LOG_FILE = os.path.join(log_path, dt.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d %H_%M_%S') + ".log")

if args.mode:
    logFormatter = logging.Formatter("%(levelname)s %(asctime)s %(message)s")
    fileHandler = logging.FileHandler("{0}".format(LOG_FILE))
    fileHandler.setFormatter(logFormatter)
    rootLogger = logging.getLogger()
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(logging.INFO)

output_Log("Script Started", args.mode)
config = Config(connect_timeout=5, retries={'max_attempts': 1})
s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY,  aws_secret_access_key= AWS_ACCESS_SECRET_KEY, config=config)
try:
    response = s3_client.head_bucket(Bucket=bucket_name)
    output_Log('Connected the bucket', args.mode)
except EndpointConnectionError as e:
    output_Log('Connection Error', args.mode)
    output_Log(e, args.mode)
except ClientError as e:
    output_Log('Connection Failed', args.mode)
    output_Log(e, args.mode)
    
# display the percentage of the upload progress.
class ProgressPercentage(object):
    
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


while True:
    filenames = [f for f in os.listdir(image_path) if re.match(r'[0-9]{10}.jpg', f.lower())]
    file_counts = len(filenames)
    if file_counts > 0:
        logging.info("\nJPG File Counts: {0}".format(file_counts))
    filenames = sorted(filenames,reverse = True)
    for filename in filenames:
        file_path = os.path.join(image_path, filename)
        key = filename
        # upload the file
        try: 
            response = s3_client.upload_file(file_path, bucket_name, filename, 
                                             Callback=ProgressPercentage(file_path))
            logging.info("\n{0} Upload Successfully".format(filename))
            #remove the file
            os.remove(file_path)

        except ClientError as e:  # handle aws s3 exceptions
            msg = e.kwargs.get('error').message
            print 'Failed to copy to S3 bucket:\n', msg
            logging.error("\nFailed to copy to S3 bucket: {0}\n".format(msg))
        except EndpointConnectionError as e:
            msg = e.kwargs.get('error').message
            print 'Failed to copy to S3 bucket:\n', msg
            logging.error("\nFailed to copy to S3 bucket: {0}\n".format(msg))
    time.sleep(1)
    
