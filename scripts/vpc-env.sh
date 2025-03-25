#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash
metadata_service="http://169.254.169.254/latest/meta-data"
TOKEN=$(curl -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600')
interface=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s $metadata_service/network/interfaces/macs/ | head -n1 | tr -d '/')
export DefaultRouteCidr=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s $metadata_service/network/interfaces/macs/$interface/vpc-ipv4-cidr-block/)
echo "export DefaultRouteCidr=${DefaultRouteCidr}" | tee -a ~/.bash_profile
