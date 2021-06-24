#!/usr/bin/env python

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#
# This script inserts random data into an index named "people" within an Amazon
# Elasticsearch cluster specified by the user. The script runs in an 
# uninterrupted fashion until stopped.

import argparse
import os
import sys
import time


import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import ConnectionTimeout
from faker import Faker
from requests_aws4auth import AWS4Auth


def main(endpoint):
    if 'AWS_REGION' not in os.environ:
        print("The AWS_REGION environment variable has not been set.")
        sys.exit(1)
    
    region = os.environ['AWS_REGION']
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    fake = Faker()
    
    es = Elasticsearch(
        hosts = [{'host': endpoint, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    while True:
        document = fake.profile()
        
        try:
            result = es.index(index="people", doc_type="_doc", body=document)
            print("Indexed with ID '%s'" % result['_id'])
            time.sleep(0.25)

        except ConnectionTimeout as e:
            print("Connection to the ES cluster timed out: %s" % str(e))
            time.sleep(2)
        
        except Exception as e:
            print("Unexpected exception caught: %s" % str(e))
            time.sleep(2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Inserts random data into an Amazon Elasticsearch domain')
    parser.add_argument('endpoint',
                        help='the domain endpoint (e.g., "vpc-foo-123456789abcdefghijklmnopq.eu-west-1.es.amazonaws.com")')
                        
    args = parser.parse_args()

    main(args.endpoint)
    