# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
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
            container_insights=True
        )
        
        ecs_security_group = ec2.SecurityGroup(
            self, "EcsSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        ecs_security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/16'),
            ec2.Port.all_traffic()
        )
        
        ecs_role = iam.Role(
            self,
            "Ec2ExecutionRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="The instance's permissions (HOST of the container)",
        )

        ecs_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"))
        ecs_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedEC2InstanceDefaultPolicy"))
    
        ec2_user_data = ec2.UserData.for_linux() 

        launch_template = ec2.LaunchTemplate(
            self,
            "LaunchTemplate",
            instance_type=ec2.InstanceType("m6g.2xlarge"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2023(ecs.AmiHardwareType.ARM),
            user_data=ec2_user_data,
            require_imdsv2=True,
            role=ecs_role,
            security_group=ecs_security_group
        )

        auto_scaling_group = autoscaling.AutoScalingGroup(
            self,
            "Asg",
            vpc=vpc,
            launch_template=launch_template,
            min_capacity=1,
            max_capacity=2,
            new_instances_protected_from_scale_in=False,
        )

        capacity_provider = ecs.AsgCapacityProvider(
            self,
            "AsgCapacityProvider",
            auto_scaling_group=auto_scaling_group,
            enable_managed_termination_protection=False,
            enable_managed_draining=False,
        )
        
        cluster.add_asg_capacity_provider(capacity_provider)
        cluster.add_default_capacity_provider_strategy([
            ecs.CapacityProviderStrategy(capacity_provider=capacity_provider.capacity_provider_name)
        ])
        
        task_definition = ecs.Ec2TaskDefinition(
            self, "TaskDef")

        container_uri = ssm.StringParameter.value_for_string_parameter(self ,"graviton_lab_container_uri")
        
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
            host_port=8888,
            protocol=ecs.Protocol.TCP
        )

        container.add_port_mappings(port_mapping)

        # Create Service
        service = ecs.Ec2Service(
            self, "Service",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            min_healthy_percent=0,
            max_healthy_percent=100,
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
