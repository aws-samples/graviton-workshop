# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash

aws ssm delete-parameter --name "graviton_net_container_uri"
aws ssm delete-parameter --name "graviton_lab_container_uri"
kubectl delete all --all -n aspnet
kubectl delete all --all -n multiarch
aws ecr delete-repository --repository-name graviton-pipeline-lab --force
aws ecr delete-repository --repository-name graviton-aspnet-lab --force

cdk destroy GravitonID-eks -f
cdk destroy GravitonID-ecs -f
cdk destroy GravitonID-pipeline-dotnet -f
cdk destroy GravitonID-pipeline -f
