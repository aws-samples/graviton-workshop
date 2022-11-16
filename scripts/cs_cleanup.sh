#!/bin/bash -xe
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

for name in graviton_net_container_uri graviton_lab_container_uri; do
    if aws ssm get-parameter --name "$name" >/dev/null 2>&1; then
        aws ssm delete-parameter --name "$name"
    fi
done

for namespace in aspnet multiarch; do
    kubectl delete all --all -n "$namespace"
done

for name in graviton2-pipeline-lab graviton2-aspnet-lab; do
    if aws ecr describe-repositories --repository-name "$name" >/dev/null 2>&1; then
        aws ecr delete-repository --repository-name "$name" --force
    fi
done

for stack in GravitonID-ecs GravitonID-pipeline-dotnet GravitonID-pipeline; do
    cdk destroy "$stack" -f
done