#!/usr/bin/env python

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#
# This script performs a search on an index called "people" within an Amazon 
# Elasticsearch domain specificed by the user.

import argparse
import os
import sys


import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def main(endpoint, search_term):
    if 'AWS_REGION' not in os.environ:
        print("The AWS_REGION environment variable has not been set.")
        sys.exit(1)
    
    region = os.environ['AWS_REGION']
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    es = Elasticsearch(
        hosts = [{'host': endpoint, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    search_body = {
        "query": {
            "match": {
                "job": search_term
            }
        }
    }
    
    result = es.search(index="people", body=search_body)
    
    if not len(result['hits']['hits']):
        print("Your search produced no results.")
    else:
        print("Your search produced %d results: \n" % len(result['hits']['hits']))
        
        for hit in result['hits']['hits']:
            print(" - Name: %s\n   Job: %s\n   Score: %s" % (hit['_source']['name'], hit['_source']['job'], hit['_score']))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Performs a search on an Amazon Elasticsearch domain, on the "people" index by job title')
    parser.add_argument('endpoint',
                        help='the domain endpoint (e.g., "vpc-foo-123456789abcdefghijklmnopq.eu-west-1.es.amazonaws.com")')
    parser.add_argument('search_term',
                        help='the term to search')
                        
    args = parser.parse_args()

    main(args.endpoint, args.search_term)
    