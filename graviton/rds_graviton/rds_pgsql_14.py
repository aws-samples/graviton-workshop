# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import os

default_vpc_cidr = os.environ["DefaultRouteCidr"] 

class CdkPgSQLStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        Pgsqlsecgroup = ec2.SecurityGroup(self, id="Pgsqlsecgroup", vpc=vpc)
        pgsql_db = rds.DatabaseInstance(self, "PgSQL14",
                                             engine=rds.DatabaseInstanceEngine.postgres(
						 version=rds.PostgresEngineVersion.VER_14_19
                                             ),
                                             instance_type=ec2.InstanceType("m5.4xlarge"),
                                             vpc=vpc,
                                             multi_az=False,
                                             publicly_accessible=False,
                                             allocated_storage=100,
                                             storage_type=rds.StorageType.GP2,
                                             cloudwatch_logs_exports=["postgresql"],
                                             deletion_protection=False,
                                             enable_performance_insights=True,
                                             delete_automated_backups=True,
                                             backup_retention=cdk.Duration.days(0),
					                         security_groups=[Pgsqlsecgroup],
                                             parameter_group=rds.ParameterGroup.from_parameter_group_name(
                                                 self, "para-group-pgsql",
                                                 parameter_group_name="default.postgres14"
                                             )
                                             )
        pgsql_db.connections.allow_default_port_from(ec2.Peer.ipv4(default_vpc_cidr), "Cloud9 PgSQL Access")

        cdk.CfnOutput( self, "PgSQL14RDSInstanceId", value = pgsql_db.instance_identifier)
        cdk.CfnOutput( self, "PgSQL14SecretArn", value = pgsql_db.secret.secret_arn)