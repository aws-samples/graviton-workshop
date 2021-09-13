# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticsearch as es
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as _lambda
from aws_cdk.aws_lambda_python import PythonFunction
import os

c9_ip = os.environ["C9_HOSTNAME"] + '/32'

class CdkElasticsearchStack(core.Stack):
    """A stack containing a basic Amazon Elasticsearch domain running on the 
    x86 architecture."""

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        access_policy = iam.PolicyStatement(actions=['es:*'],
                                            principals=[iam.AccountPrincipal(self.account)])
        es_domain = es.Domain(self,
                              "Domain",
                              version=es.ElasticsearchVersion.V7_9,
                              vpc=vpc,
                              # Since we only have 1 node, let's use the first private subnet in our VPC.
                              vpc_subnets=[ec2.SubnetSelection(subnets=[vpc.private_subnets[0]])],
                              capacity={
                                  'data_node_instance_type': 'm5.large.elasticsearch',
                                  'data_nodes': 1,
                                  'master_nodes': 0,
                                  'warm_nodes': 0
                              },
                              access_policies=[access_policy])
        es_domain.connections.allow_from_any_ipv4(ec2.Port.all_traffic())

        insert_fn = PythonFunction(self,
                       "InsertIntoIndexFunction",
                       entry="graviton2/elasticsearch_graviton/lambdas",
                       index="insert_into_index.py",
                       handler="handler",
                       runtime=_lambda.Runtime.PYTHON_3_8,
                       vpc=vpc,
                       environment={
                           "ES_ENDPOINT": es_domain.domain_endpoint
                       },
                       timeout=core.Duration.minutes(1))
        es_domain.grant_write(insert_fn.grant_principal)

        scheduled_rule = events.Rule(self,
                                      "ScheduledIndexInsertionRule",
                                      schedule=events.Schedule.expression('cron(* * ? * * *)'))
        scheduled_rule.add_target(events_targets.LambdaFunction(insert_fn))

        core.CfnOutput(self, "DomainEndpoint", value=es_domain.domain_endpoint)
        core.CfnOutput(self, "DomainName", value=es_domain.domain_name)
