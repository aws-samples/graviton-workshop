# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_elasticache as elasticache
import os

c9_ip = os.environ["C9_HOSTNAME"] + '/32'

class CdkRedisStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
                
        instance = self.create_bastion_instance(vpc)        
        
        redis_security_group = ec2.SecurityGroup(self, "RedisSG", 
                                                    vpc=vpc, 
                                                    allow_all_outbound = True,
                                                    description = "Security Group for Redis cluster"
                                                )
        redis_security_group.add_ingress_rule(ec2.Peer.ipv4(instance.instance_private_ip+"/32"), 
                                                ec2.Port.tcp(6379), 
                                                "Allow incoming traffic from Cloud9 instance"
                                            )
                                            
        subnet_group =  elasticache.CfnSubnetGroup(self,"RedisSubnetGroup",
                                                    description="Subnet Group for Redis ElastiCache Cluster",
                                                    subnet_ids=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnet_ids
                                                )                                           
        
        redis_elasticache = elasticache.CfnReplicationGroup(self,"MyRedisCache",
                                                        replication_group_description="Redis Cluster for Graviton2 Workshop",
                                                        cache_node_type="cache.r5.large",
                                                        engine="redis",
                                                        automatic_failover_enabled=True,
                                                        auto_minor_version_upgrade=False,
                                                        security_group_ids=[redis_security_group.security_group_id],
                                                        cache_subnet_group_name=subnet_group.ref,
                                                        multi_az_enabled=True,
                                                        num_cache_clusters=2
                                                        )
                                                        
        core.CfnOutput( self, "MyBastionHostDNS", value = instance.instance_public_dns_name)
        core.CfnOutput( self, "MyRedisClusterHost", value = redis_elasticache.attr_primary_end_point_address)                                                        
        core.CfnOutput( self, "MyRedisClusterPort", value = redis_elasticache.attr_primary_end_point_port)
        core.CfnOutput( self, "MyRedisClusterSecurityGroup", value = redis_security_group.security_group_id)
        core.CfnOutput( self, "MyRedisClusterSubnetGroup", value = subnet_group.ref)

    def create_bastion_instance(self, vpc):
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
                                                        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                                                        edition=ec2.AmazonLinuxEdition.STANDARD,
                                                        virtualization=ec2.AmazonLinuxVirt.HVM,
                                                        storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
                                                        )

        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        
        bastion_security_group = ec2.SecurityGroup(self, "BastionSG", 
                                                    vpc=vpc, 
                                                    allow_all_outbound = True,
                                                    description = "Security Group for Bastion Host"
                                                )
        bastion_security_group.add_ingress_rule(ec2.Peer.ipv4(c9_ip), 
                                                ec2.Port.tcp(22), 
                                                "Allow incoming traffic from Cloud9 instance"
                                            )
        
        instance = ec2.Instance(self, "Instance",
                                instance_type=ec2.InstanceType("t3.nano"),
                                machine_image=amzn_linux,
                                vpc = vpc,
                                role = role,
                                key_name = "graviton2key",
                                vpc_subnets = ec2.SubnetSelection(subnets = (vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnets)),
                                security_group = bastion_security_group
                            )
                            
        userdata_file = open("scripts/redis-cli-install.sh", "r")
        userdata = userdata_file.read()
        instance.add_user_data(userdata)
                            
        return instance
        