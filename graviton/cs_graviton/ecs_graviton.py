# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import Duration
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_ecs_patterns as ecs_patterns
import aws_cdk.aws_ssm as ssm
import aws_cdk.aws_autoscaling as autoscaling
import aws_cdk.aws_iam as iam
import os


class CdkEcsStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        cluster = ecs.Cluster(
            self, 'ECSGraviton',
            vpc=vpc,
            container_insights=True,
            enable_fargate_capacity_providers=True
        )
        
        ecs_exec_role = iam.Role(
            self,
            "ECSExecRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="ECSExecRole",
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "ECSTaskExecutionRolePolicy",
                    managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
                )
            ],
        )

        container_uri = ssm.StringParameter.value_for_string_parameter(self ,"graviton_lab_container_uri")
        
        fargate_service =ecs_patterns.ApplicationLoadBalancedFargateService(self, "FargateService",
            cluster=cluster,            
            cpu=256,                    
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(container_uri), 
                container_port=3000,
                execution_role=ecs_exec_role,
            ),  
            memory_limit_mib=512,
            public_load_balancer=True,  
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
                cpu_architecture=ecs.CpuArchitecture.ARM64
                ),
        ) 
        
        cdk.CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name

        )