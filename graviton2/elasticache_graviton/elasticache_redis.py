# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_elasticache as elasticache
import socket

c9_ip = socket.gethostbyname(socket.gethostname()) + "/32"

class CdkRedisStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        redis_security_group = ec2.SecurityGroup(self, "RedisSG", 
                                                    vpc=vpc, 
                                                    allow_all_outbound = True,
                                                    description = "Security Group for Redis cluster"
                                                )
        redis_security_group.add_ingress_rule(ec2.Peer.ipv4(c9_ip), 
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
                                                        
        core.CfnOutput( self, "MyRedisClusterHost", value = redis_elasticache.attr_primary_end_point_address)                                                        
        core.CfnOutput( self, "MyRedisClusterPort", value = redis_elasticache.attr_primary_end_point_port)
        core.CfnOutput( self, "MyRedisClusterSecurityGroup", value = redis_security_group.security_group_id)
        core.CfnOutput( self, "MyRedisClusterSubnetGroup", value = subnet_group.ref)

