# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_eks as eks
import os

c9_ip = os.environ["C9_HOSTNAME"] + '/32'

class CdkEksStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
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
        eks_security_group.add_ingress_rule(
            ec2.Peer.ipv4(c9_ip),
            ec2.Port.all_traffic()
        )  

        
        self.cluster = eks.Cluster(self, "EKSGraviton2",
            version=eks.KubernetesVersion.V1_20,
            default_capacity=0,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            vpc=vpc,
            security_group=eks_security_group

        )

        self.ng_x86 = self.cluster.add_nodegroup_capacity("x86-node-group",
            instance_types=[ec2.InstanceType("m5.large")],
            desired_size=2,
            min_size=1,
            max_size=3
        )
        
        self.ng_arm64 = self.cluster.add_nodegroup_capacity("arm64-node-group",
            instance_types=[ec2.InstanceType("m6g.large")],
            desired_size=2,
            min_size=1,
            max_size=3
        )
 
