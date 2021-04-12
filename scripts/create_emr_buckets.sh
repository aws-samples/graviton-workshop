# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash

export emr_s3_uuid=`cat /dev/urandom | tr -dc 'a-z' | fold -w 32 | head -n 1`
export emr_s3_name=graviton-emr-lab-$emr_s3_uuid

echo "Creating S3 Bucket for EMR"


aws s3 mb s3://$emr_s3_name
echo "Blocking public access"
aws s3api put-public-access-block --bucket $emr_s3_name --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "Creating folders"
aws s3api put-object --bucket $emr_s3_name --key input/
aws s3api put-object --bucket $emr_s3_name --key output/
aws s3api put-object --bucket $emr_s3_name --key files/
aws s3api put-object --bucket $emr_s3_name --key logs/

aws s3 cp ~/environment/graviton2-workshop/scripts/tripdata.csv s3://$emr_s3_name/input/
