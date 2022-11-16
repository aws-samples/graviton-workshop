#!/bin/bash -xe
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

snapshot_uuid=`cat /dev/urandom | tr -dc 'a-z' | fold -w 16 | head -n 1`

parameter="graviton_rds_lab_snapshot"

if aws ssm get-parameter --name "$parameter" >/dev/null 2>&1; then
    aws ssm delete-parameter --name "$parameter"
fi

echo "Saving snapshot id using AWS Systems Manager Parameter Store"

aws ssm put-parameter --name "$parameter" --value $snapshot_uuid  --type String

echo "Creating RDS database snapshot"

aws rds create-db-snapshot \
    --db-instance-identifier `aws cloudformation describe-stacks --stack-name GravitonID-rds-8 --query "Stacks[0].Outputs[1].OutputValue" --output text` \
    --db-snapshot-identifier $snapshot_uuid \
    --query 'DBSnapshot.Status' \
    --output text

echo -e "Your snapshot id : \e[1;32m $snapshot_uuid \e[0m"
