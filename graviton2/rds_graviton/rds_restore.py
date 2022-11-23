# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import aws_cdk.aws_ssm as ssm
import os

class CdkRdsRestoreStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id=vpc_id)

        snapshot_id = ssm.StringParameter.value_for_string_parameter(self ,"graviton_rds_lab_snapshot")
        g2_db_mysql8 = rds.DatabaseInstanceFromSnapshot(self, "GravitonMySQL",
                                             engine=rds.DatabaseInstanceEngine.mysql(
                                                 version=rds.MysqlEngineVersion.VER_8_0_23
                                             ),
                                             instance_type=ec2.InstanceType("m6g.4xlarge"),
                                             snapshot_identifier=snapshot_id,
                                             vpc=vpc,
                                             multi_az=False,
                                             publicly_accessible=True,
                                             allocated_storage=100,
                                             storage_type=rds.StorageType.GP2,
                                             cloudwatch_logs_exports=["error", "general", "slowquery"],
                                             enable_performance_insights=True,
                                             deletion_protection=False,
                                             delete_automated_backups=True,
                                             backup_retention=cdk.Duration.days(0),
                                             vpc_subnets={
                                                 "subnet_type": ec2.SubnetType.PUBLIC
                                             },
                                             parameter_group=rds.ParameterGroup.from_parameter_group_name(
                                                 self, "para-group-mysql",
                                                 parameter_group_name="default.mysql8.0"
                                             )
                                             )

        g2_db_mysql8.connections.allow_default_port_from(ec2.Peer.ipv4("10.0.0.0/16"), "Cloud9 MySQL Access")
        cdk.CfnOutput( self, "G2MySQL8RDSInstanceId", value = g2_db_mysql8.instance_identifier)
