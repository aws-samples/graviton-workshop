# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash

cd ~/environment/graviton2-labs/
aws ssm delete-parameter --name "graviton_net_container_uri"
kubectl delete all --all -n aspnet
kubectl delete all --all -n multiarch
aws ecr delete-repository --repository-name graviton2-pipeline-lab --force
aws ecr delete-repository --repository-name graviton2-aspnet-lab --force

cdk destroy GravitonID-eks -f
cdk destroy GravitonID-ecs -f
cdk destroy GravitonID-pipeline-dotnet -f
cdk destroy GravitonID-pipeline -f
