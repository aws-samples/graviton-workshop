# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
import aws_cdk.aws_ssm as ssm
import os


class CdkEcsStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id=vpc_id)

        cluster = ecs.Cluster(
            self, 'ECSGraviton2',
            vpc=vpc,
            container_insights=True
        )

        task_definition = ecs.Ec2TaskDefinition(
            self, "TaskDef")

        container_uri = ssm.StringParameter.value_for_string_parameter(self ,"graviton_lab_container_uri")

        ecs_ami = ecs.EcsOptimizedImage.amazon_linux2(ecs.AmiHardwareType.ARM)

        cluster.add_capacity("G2AutoScalingGroup",
                         instance_type=ec2.InstanceType("m6g.2xlarge"),
                         machine_image=ecs_ami

        )

        container = task_definition.add_container(
            "web",
            image=ecs.ContainerImage.from_registry(container_uri),
            memory_limit_mib=512,
            logging=ecs.LogDrivers.firelens(
                options={
                    "Name": "cloudwatch",
                    "log_key": "log",
                    "region": "us-east-1",
                    "delivery_stream": "my-stream",
                    "log_group_name": "firelens-fluent-bit",
                    "auto_create_group": "true",
                    "log_stream_prefix": "from-fluent-bit"}
            )
        )
        port_mapping =  ecs.PortMapping(
            container_port=3000,
            host_port=8080,
            protocol=ecs.Protocol.TCP
        )

        container.add_port_mappings(port_mapping)

        # Create Service
        service = ecs.Ec2Service(
            self, "Service",
            cluster=cluster,
            task_definition=task_definition
        )

        # Create ALB
        lb = elbv2.ApplicationLoadBalancer(
            self, "LB",
            vpc=vpc,
            internet_facing=True
        )

        listener = lb.add_listener(
            "PublicListener",
            port=80,
            open=True
        )

        # Attach ALB to ECS Service
        listener.add_targets(
            "ECS",
            port=80,
            targets=[service]
        )

        cdk.CfnOutput(
            self, "LoadBalancerDNS",
            value=lb.load_balancer_dns_name
        )
