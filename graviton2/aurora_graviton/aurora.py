import aws_cdk as cdk
from constructs import Construct
from aws_cdk import Stack, aws_rds as rds, aws_ec2 as ec2, aws_iam as iam, Duration
import os

default_vpc_cidr = os.environ["DefaultRouteCidr"]


class CdkAuroraStack(Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Security Group
        security_group = ec2.SecurityGroup(
            self,
            "AuroraPostgresSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
            description="Security Group for Aurora PostgreSQL",
            security_group_name="AuroraPostgresSecurityGroup",
        )

        # Add inbound rule to allow pgbench client to connect
        security_group.add_ingress_rule(
            ec2.Peer.ipv4(default_vpc_cidr), ec2.Port.all_traffic()
        )

        # Aurora PostgreSQL Cluster
        cluster = rds.DatabaseCluster(
            self,
            "AuroraPostgresCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_15_2
            ),
            writer=rds.ClusterInstance.provisioned(
                "writer",
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.R5, ec2.InstanceSize.XLARGE2
                ),
                enable_performance_insights=True,
                instance_identifier="lab-intel-based-instance-1"
            ),
            cluster_identifier="lab-intel-based"
            monitoring_interval=Duration.minutes(1),
            security_groups=[security_group],
            vpc=vpc,
            storage_encrypted=True,
            default_database_name="postgres",
        )

        cdk.CfnOutput(
            self,
            "AURORA_WRITER_ENDPOINT",
            value=cluster.cluster_endpoint.hostname,
            description="The endpoint of the Aurora cluster",
        )
        cdk.CfnOutput(
            self,
            "AURORA_SECRET_NAME",
            value=cluster.secret.secret_name,
            description="Aurora PostgreSQL database secret name",
        )
