# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash

snapshot_uuid=`cat /dev/urandom | tr -dc 'a-z' | fold -w 16 | head -n 1`


aws ssm delete-parameter --name "graviton_rds_pg_lab_snapshot" >/dev/null 2>&1

echo "Saving snapshot id using AWS Systems Manager Parameter Store"

aws ssm put-parameter --name "graviton_rds_pg_lab_snapshot" --value $snapshot_uuid  --type String  

echo "Creating RDS database snapshot"

aws rds create-db-snapshot --db-instance-identifier `aws cloudformation describe-stacks --stack-name GravitonID-rds-pg14 --query "Stacks[0].Outputs[1].OutputValue" --output text` --db-snapshot-identifier $snapshot_uuid >& /dev/null

echo -e "Your snapshop id : \e[1;32m $snapshot_uuid \e[0m"