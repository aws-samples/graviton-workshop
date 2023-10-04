# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_opensearchservice as open_search
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonFunction
import os

c9_ip = os.environ["C9_HOSTNAME"] + '/32'

class CdkOpenSearchStack(cdk.Stack):
    """A stack containing a basic Amazon Elasticsearch domain running on the
    x86 architecture."""

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        es_security_group = ec2.SecurityGroup(
            self, "ESSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )

        es_security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/16'),
            ec2.Port.all_traffic()
        )
        es_security_group.add_ingress_rule(
            ec2.Peer.ipv4(c9_ip),
            ec2.Port.all_traffic()
        )
        es_domain = open_search.Domain(self,
                              "Domain",
                              version=open_search.EngineVersion.OPENSEARCH_1_0,
                              vpc=vpc,
                              capacity={
                                  'data_node_instance_type': 'm5.large.search',
                                  'data_nodes': 2,
                                  'master_nodes': 0,
                                  'warm_nodes': 0
                              },
                              zone_awareness= open_search.ZoneAwarenessConfig(
                                  availability_zone_count=2
                              ),
                              vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)],
                              security_groups=[es_security_group],
                              removal_policy=cdk.RemovalPolicy.DESTROY
                              )

        insert_fn = PythonFunction(self,
                       "InsertIntoIndexFunction",
                       entry="graviton2/opensearch_graviton/lambdas",
                       index="insert_into_index.py",
                       handler="handler",
                       runtime=_lambda.Runtime.PYTHON_3_8,
                       vpc=vpc,
                       environment={
                           "ES_ENDPOINT": es_domain.domain_endpoint
                       },
                       timeout=cdk.Duration.minutes(1))

        es_domain.grant_write(insert_fn.grant_principal)

        scheduled_rule = events.Rule(self,
                                      "ScheduledIndexInsertionRule",
                                      schedule=events.Schedule.expression('cron(* * ? * * *)'))
        scheduled_rule.add_target(events_targets.LambdaFunction(insert_fn))

        cdk.CfnOutput(self, "LambdaName",value=insert_fn.function_name)
        cdk.CfnOutput(self, "DomainEndpoint", value=es_domain.domain_endpoint)
        cdk.CfnOutput(self, "DomainName", value=es_domain.domain_name)
