# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import os

default_vpc_cidr = os.environ["DefaultRouteCidr"] 

class CdkPerfStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ec2_type = "m6g.medium"
        ec2_type_client = "m5.large"
        amzn_linux= ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.ARM_64)
        amzn_linux_x86_64= ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.X86_64)
        key_pair = ec2.KeyPair.from_key_pair_name(self, "KeyPair", "gravitonKey")
 
        # Create a placement group with the CLUSTER strategy
        #pg = ec2.PlacementGroup(self, "ec2_module_PlacementGroup",strategy=ec2.PlacementGroupStrategy.CLUSTER)
        pg = ec2.CfnPlacementGroup(self, 'ec2_module_PlacementGroup', strategy='cluster')
        ec2_security_group = ec2.SecurityGroup(
            self, "Ec2SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        ec2_security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/16'),
            ec2.Port.all_traffic()
        )
        ec2_security_group.add_ingress_rule(
            ec2.Peer.ipv4(default_vpc_cidr),
            ec2.Port.all_traffic()
        )
        
        user_data = self.get_user_data("client")
        client = ec2.Instance(self, "Client",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_type_client),
                            instance_name="Perf_Client",
                            machine_image=amzn_linux_x86_64,
                            vpc=vpc,
                            key_pair=key_pair,
                            security_group=ec2_security_group,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            user_data=ec2.UserData.custom(user_data)
                            )
        client.instance.add_property_override('PlacementGroupName', pg.ref)

        user_data = self.get_user_data("sut_1")
        sut_1 = ec2.Instance(self, "SUT1",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_type),
                            instance_name="Perf_SUT1",
                            machine_image=amzn_linux,
                            vpc=vpc,
                            key_pair=key_pair,
                            security_group=ec2_security_group,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            user_data=ec2.UserData.custom(user_data)
                            )
                            
 
        user_data = self.get_user_data("sut_2")
        sut_2 = ec2.Instance(self, "SUT2",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_type),
                            instance_name="Perf_SUT2",
                            machine_image=amzn_linux,
                            vpc=vpc,
                            key_pair=key_pair,
                            security_group=ec2_security_group,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            user_data=ec2.UserData.custom(user_data)
                            )

        cdk.CfnOutput( self, "Client_IP", value = client.instance_private_ip) 
        cdk.CfnOutput( self, "SUT1_IP", value = sut_1.instance_private_ip) 
        cdk.CfnOutput( self, "SUT2_IP", value = sut_2.instance_private_ip) 

    def get_user_data(self, filename):
        with open('./scripts/' + filename) as f:
            user_data = f.read()
        return user_data
