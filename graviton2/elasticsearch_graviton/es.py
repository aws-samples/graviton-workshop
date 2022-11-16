# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticsearch as es
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonFunction


class CdkElasticsearchStack(cdk.Stack):
    """Creates a scheduled Lambda function that inserts documents into the supplied
    ElasticSearch domain."""

    def __init__(self, scope: Construct, id: str, vpc_id: str, es_domain: str, es_endpoint: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id=vpc_id)

        es_domain = es.Domain.from_domain_attributes(self, 'Domain',
            domain_arn=cdk.Stack.of(self).format_arn(
                service='es',
                resource='domain',
                resource_name=es_domain
            ),
            domain_endpoint=es_endpoint)

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
                       timeout=cdk.Duration.minutes(1))

        es_domain.grant_write(insert_fn.grant_principal)

        scheduled_rule = events.Rule(self,
                                      "ScheduledIndexInsertionRule",
                                      schedule=events.Schedule.expression('cron(* * ? * * *)'))
        scheduled_rule.add_target(events_targets.LambdaFunction(insert_fn))

        cdk.CfnOutput(self, "LambdaName",value=insert_fn.function_name)
