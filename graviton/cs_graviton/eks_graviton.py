# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
import aws_cdk as cdk
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_eks as eks
import aws_cdk.aws_iam as iam
import os
from aws_cdk.lambda_layer_kubectl_v31 import KubectlV31Layer

class CdkEksStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create SecurityGroup for the Control Plane ENIs
        eks_security_group = ec2.SecurityGroup(
            self, "EKSSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )

        eks_security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/16'),
            ec2.Port.all_traffic()
        )
        
        clusterAdminRole = iam.Role(self, 'ClusterAdmin',
            assumed_by= iam.AccountRootPrincipal()
        )
        clusterAdminRole.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=[
                "eks:Describe*",
                "eks:List*",
                "eks:AccessKubernetesApi",
                "ssm:GetParameter",
                "iam:ListRoles"
            ],
        ))


        # Managed Node Group Instance Role
        managed_node_managed_policies = (
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSWorkerNodePolicy'),
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKS_CNI_Policy'),
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly'),
            iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchAgentServerPolicy'), 
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'), 
        )
        managed_node_role = iam.Role(self,'NodeInstanceRole',
            path='/',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=list(managed_node_managed_policies),
        )

        self.cluster = eks.Cluster(self, "EKSGraviton",
            version=eks.KubernetesVersion.V1_31,
            default_capacity=0,
            output_cluster_name=True,
            masters_role=clusterAdminRole,
            output_config_command=True,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            vpc=vpc,
            security_group=eks_security_group,
            kubectl_layer=KubectlV31Layer(self, 'KubectlV31Layer')

        )

        self.ng_x86 = self.cluster.add_nodegroup_capacity("x86-node-group",
            instance_types=[ec2.InstanceType("m5.large")],
            desired_size=2,
            node_role = managed_node_role,
            min_size=1,
            max_size=3
        )

        self.ng_arm64 = self.cluster.add_nodegroup_capacity("arm64-node-group",
            instance_types=[ec2.InstanceType("m6g.large")],
            desired_size=2,
            node_role = managed_node_role,
            min_size=1,
            max_size=3
        )

