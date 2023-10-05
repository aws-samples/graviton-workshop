# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#
# This lambda function inserts random data into an index named "people" within 
# an Amazon OpenSearch cluster specified by the user. The function will do
# several insertions before exiting.

import argparse
import os
import sys
import time


import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import ConnectionTimeout
from faker import Faker
from requests_aws4auth import AWS4Auth


endpoint = os.environ['OS_ENDPOINT']
region = os.environ['AWS_REGION']


def handler(event, context):
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
    
    attempts = 20
    print("Will insert %s items into the index" % attempts)
    for i in range(attempts):
        document = fake.profile()
        
        try:
            result = es.index(index="people", doc_type="_doc", body=document)
            print("Indexed with ID '%s'" % result['_id'])
    
        except ConnectionTimeout as e:
            print("Connection to the OS cluster timed out: %s" % str(e))
        
        except Exception as e:
            print("Unexpected exception caught: %s" % str(e))
        
        time.sleep(2)
