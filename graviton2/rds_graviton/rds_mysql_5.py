# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import os

class CdkRds5Stack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id=vpc_id)

        db_mysql5 = rds.DatabaseInstance(self, "MySQL5",
                                             engine=rds.DatabaseInstanceEngine.mysql(
                                                 version=rds.MysqlEngineVersion.VER_5_7_33
                                             ),
                                             instance_type=ec2.InstanceType("m5.4xlarge"),
                                             vpc=vpc,
                                             multi_az=False,
                                             publicly_accessible=True,
                                             allocated_storage=100,
                                             storage_type=rds.StorageType.GP2,
                                             cloudwatch_logs_exports=["audit", "error", "general", "slowquery"],
                                             deletion_protection=False,
                                             enable_performance_insights=True,
                                             delete_automated_backups=True,
                                             backup_retention=cdk.Duration.days(1),
                                             vpc_subnets={
                                                 "subnet_type": ec2.SubnetType.PUBLIC
                                             },
                                             parameter_group=rds.ParameterGroup.from_parameter_group_name(
                                                 self, "para-group-mysql",
                                                 parameter_group_name="default.mysql5.7"
                                             )
                                             )
        db_mysql5.connections.allow_default_port_from(ec2.Peer.ipv4("10.0.0.0/16"), "Cloud9 MySQL Access")

        cdk.CfnOutput( self, "MySQL5RDSInstanceId", value = db_mysql5.instance_identifier)
        cdk.CfnOutput( self, "MySQL5SecretArn", value = db_mysql5.secret.secret_arn)
