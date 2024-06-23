# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import os

c9_ip = os.environ["C9_HOSTNAME"] + '/32'

class CdkRdsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        db_mysql = rds.DatabaseInstance(self, "MySQL",
                                             engine=rds.DatabaseInstanceEngine.mysql(
                                                 version=rds.MysqlEngineVersion.VER_5_0_30
                                             ),
                                             instance_type=ec2.InstanceType("m5.4xlarge"),
                                             vpc=vpc,
                                             multi_az=False,
                                             publicly_accessible=True,
                                             allocated_storage=100,
                                             storage_type=rds.StorageType.GP2,
                                             cloudwatch_logs_exports=["audit", "error", "general", "slowquery"],
                                             deletion_protection=False,
                                             delete_automated_backups=False,
                                             backup_retention=core.Duration.days(7),
                                             parameter_group=rds.ParameterGroup.from_parameter_group_name(
                                                 self, "para-group-mysql",
                                                 parameter_group_name="default.mysql5.7"
                                             )
                                             )
        db_mysql.connections.allow_default_port_from(ec2.Peer.ipv4(c9_ip), "Cloud9 MySQL Access")

        core.CfnOutput( self, "RDSInstanceId", value = db_mysql.instance_identifier)
