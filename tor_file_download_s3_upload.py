#!/usr/bin/env python3

""" 
***Requirements***
apt-get install tor/brew install tor
sudo service tor start/brew services start tor
python3 -m pip install requests
python3 -m pip install 'requests[socks]'
python3 -m pip install 'requests[security]'
python3 -m pip install pysocks
python3 -m pip install boto3
python3 -m pip install botocore-python3
"""

import requests
import argparse
import boto3
import logging
from botocore.exceptions import ClientError
from fake_useragent import UserAgent

def download_file(url, filename, session):
    # Open in binary mode
    with open(filename, "wb") as file:
        # Get the file
        try:
            response = session.get(url)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        # Write to file and return True
        file.write(response.content)
        return True

def upload_file_s3(filename, bucket, object_name=None):
    
    if object_name is None:
        object_name = filename

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(filename, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    # Parse provided arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--uid", required=True, type=str, help="Provide UID/name for the file.")
    parser.add_argument("--url", required=True, nargs='*', type=str, help="The URL(s) of the file you wish to download.")
    args = parser.parse_args()

    # UID (Name of file)
    uid = args.uid

    # URL(s) (URL(s) of file to download)
    urls = args.url

    # S3 Bucket for storage
    bucket = "S3-BUCKET_NAME"

    # Create session for requests, add proxy + headers
    session = requests.session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    headers = {}
    ua = UserAgent()
    headers['User-agent'] = ua.chrome

    # Count files to append numbers to handle multiple file upload
    count = 0
    for url in urls:
        if count > 0:
            uid = uid + "_" + str(count)
        # Download the file
        if download_file(url, uid, session):
            print("File downloaded successfully!")
        else:
            print("File could not be downloaded.")
            count += 1

        # Upload the file
        if upload_file_s3(uid, bucket):
            print("File uploaded successfully!")
            count += 1
        else:
            print("File was not uploaded.")
            count += 1

if __name__ == "__main__":
    main()
