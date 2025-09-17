# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ec2 as ec2
import os

default_vpc_cidr = os.environ["DefaultRouteCidr"] 

class CdkEC2Stack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        current_region = self.region
        ec2_test_client = "c5.4xlarge"
        ec2_gv2_type = "c6g.xlarge"
        ec2_gv3_type = "c7g.xlarge"
        ec2_x86_type = "c5.xlarge"
        
        # Create a placement group with the CLUSTER strategy, we want all instances to be in same placement group for performance reasons
        #
        #pg = ec2.CfnPlacementGroup(self, 'ec2_module_PlacementGroup', strategy='cluster')
        
        amzn_linux_arm= ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.ARM_64)
        amzn_linux_x86_64= ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.X86_64)
        key_pair = ec2.KeyPair.from_key_pair_name(self, "KeyPair", "gravitonKey")
        
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
        
        # Define the IAM policy for the SUT machines so the test application (shortenURL) on them to have right access
        sut_policy_statement = iam.PolicyStatement(
            actions=["cloudformation:*","dynamodb:*"],
            resources=["*"],
            effect=iam.Effect.ALLOW
        )
        sut_policy_document = iam.PolicyDocument(statements=[sut_policy_statement])

        # Create the IAM role for SUT machines
        sut_role = iam.Role(
            self, 'ec2_module_IAM_Role_SUT_machines',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            inline_policies={'ec2_module_SUT_machines_Policy': sut_policy_document}
        )
        
        # Define the IAM policy for the Client machines so they can access the cloudformation to get the SUTs IPs
        client_policy_statement = iam.PolicyStatement(
            actions=["cloudformation:*"],
            resources=["*"],
            effect=iam.Effect.ALLOW
        )
        client_policy_document = iam.PolicyDocument(statements=[client_policy_statement])

        # Create the IAM role for client machine
        client_role = iam.Role(
            self, 'ec2_module_IAM_Role_Client_machines',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            inline_policies={'ec2_module_Client_machines_Policy': client_policy_document}
        )

        # create a dynamodb table for the test application to use
        urls_table = dynamodb.Table(
            self, "GravitonWorkshopDdbUrlsTable",
            partition_key=dynamodb.Attribute(
                name="short_url",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        
        user_data = self.get_user_data("ec2_module_test_client")
        client1 = ec2.Instance(self, "Client-1",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_test_client),
                            instance_name="EC2_Module_Test_Client1_for_SUT1",
                            machine_image=amzn_linux_x86_64,
                            vpc=vpc,
                            key_pair=key_pair,
                            security_group=ec2_security_group,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            user_data=ec2.UserData.custom(user_data),
                            role=client_role # Attach the IAM role to the client instance
                            )
        # add to placement group with the CLUSTER strategy                            
        #client1.instance.add_property_override('PlacementGroupName', pg.ref)
        
        # client2 = ec2.Instance(self, "Client-2",
        #                     instance_type=ec2.InstanceType(
        #                         instance_type_identifier=ec2_test_client),
        #                     instance_name="EC2_Module_Test_Client2_for_SUT2",
        #                     machine_image=amzn_linux_x86_64,
        #                     vpc=vpc,
        #                     key_name=key_name,
        #                     security_group=ec2_security_group,
        #                     vpc_subnets=ec2.SubnetSelection(
        #                         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        #                     user_data=ec2.UserData.custom(user_data),
        #                     role=client_role # Attach the IAM role to the client instance
        #                     )
        # # add to placement group with the CLUSTER strategy                            
        #client2.instance.add_property_override('PlacementGroupName', pg.ref)
        
        # client3 = ec2.Instance(self, "Client-3",
        #                     instance_type=ec2.InstanceType(
        #                         instance_type_identifier=ec2_test_client),
        #                     instance_name="EC2_Module_Test_Client3_for_SUT3",
        #                     machine_image=amzn_linux_x86_64,
        #                     vpc=vpc,
        #                     key_name=key_name,
        #                     security_group=ec2_security_group,
        #                     vpc_subnets=ec2.SubnetSelection(
        #                         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        #                     user_data=ec2.UserData.custom(user_data),
        #                     role=client_role # Attach the IAM role to the client instance
        #                     )
                            
        # add to placement group with the CLUSTER strategy                            
        #client3.instance.add_property_override('PlacementGroupName', pg.ref)
        
        user_data = self.get_user_data("ec2_module_sut_1")
        sut_1 = ec2.Instance(self, "SUT1",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_x86_type),
                            instance_name="EC2_Module_SUT1_x86",
                            machine_image=amzn_linux_x86_64,
                            vpc=vpc,
                            key_pair=key_pair,
                            security_group=ec2_security_group,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            user_data=ec2.UserData.custom(user_data),
                            role=sut_role  # Attach the IAM role to the SUT instance
                            )
                            
        # add to placement group with the CLUSTER strategy                            
        #sut_1.instance.add_property_override('PlacementGroupName', pg.ref)
 
        user_data = self.get_user_data("ec2_module_sut_2")
        sut_2 = ec2.Instance(self, "SUT2",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_gv2_type),
                            instance_name="EC2_Module_SUT2_GV2",
                            machine_image=amzn_linux_arm,
                            vpc=vpc,
                            key_pair=key_pair,
                            security_group=ec2_security_group,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            user_data=ec2.UserData.custom(user_data),
                            role=sut_role  # Attach the IAM role to the SUT instance
                            )
        
        # add to placement group with the CLUSTER strategy                            
        #sut_2.instance.add_property_override('PlacementGroupName', pg.ref)                    
                            
        user_data = self.get_user_data("ec2_module_sut_3")
        sut_3 = ec2.Instance(self, "SUT3",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_gv3_type),
                            instance_name="EC2_Module_SUT3_GV3",
                            machine_image=amzn_linux_arm,
                            vpc=vpc,
                            key_pair=key_pair,
                            security_group=ec2_security_group,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            user_data=ec2.UserData.custom(user_data),
                            role=sut_role  # Attach the IAM role to the SUT instance
                            )

        # add to placement group with the CLUSTER strategy                            
        #sut_3.instance.add_property_override('PlacementGroupName', pg.ref)

        cdk.CfnOutput( self, "Client1_IP", value = client1.instance_private_ip)
        #cdk.CfnOutput( self, "Client2_IP", value = client2.instance_private_ip) 
        #cdk.CfnOutput( self, "Client3_IP", value = client3.instance_private_ip) 
        cdk.CfnOutput( self, "SUT1_IP", value = sut_1.instance_private_ip) 
        cdk.CfnOutput( self, "SUT2_IP", value = sut_2.instance_private_ip)
        cdk.CfnOutput( self, "SUT3_IP", value = sut_3.instance_private_ip)
        cdk.CfnOutput( self, "EC2-Module-DynamoDB-Table", value =urls_table.table_name)
        # Output the current region
        cdk.CfnOutput(self, "CurrentRegionOutput", value=current_region)

    def get_user_data(self, filename):
        with open('./scripts/' + filename) as f:
            user_data = f.read()
        return user_data
