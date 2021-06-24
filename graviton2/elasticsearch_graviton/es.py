# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticsearch as es
import aws_cdk.aws_iam as iam
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

        core.CfnOutput(self, "DomainEndpoint", value=es_domain. domain_endpoint)

