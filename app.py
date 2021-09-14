# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3

from aws_cdk import core
from graviton2.rds_graviton.rds_mysql_5 import CdkRds5Stack
from graviton2.rds_graviton.rds_mysql_8 import CdkRds8Stack
from graviton2.rds_graviton.rds_restore import CdkRdsRestoreStack
from graviton2.vpc_base.vpc import CdkVpcStack
from graviton2.cs_graviton.eks_graviton2 import CdkEksStack
from graviton2.cs_graviton.ecs_graviton2 import CdkEcsStack
from graviton2.cs_graviton.pipeline_graviton2 import CdkPipelineStack
from graviton2.cs_graviton.pipeline_netcore_graviton2 import CdkPipelineDotNetStack
from graviton2.elasticsearch_graviton.es import CdkElasticsearchStack
from graviton2.elasticache_graviton.elasticache_redis import CdkRedisStack
#from graviton2.emr_graviton.emr_graviton2 import CdkEmrStack


class GravitonID(core.App):

        def __init__(self, **kwargs): 
            super().__init__(**kwargs)

            self.stack_name = "GravitonID"
            self.base_module = CdkVpcStack(self, self.stack_name + "-base")
            self.rds_5_module = CdkRds5Stack(self, self.stack_name + "-rds-5", self.base_module.vpc)
            self.rds_8_module = CdkRds8Stack(self, self.stack_name + "-rds-8", self.base_module.vpc)
            self.restore_module = CdkRdsRestoreStack(self, self.stack_name + "-rds-restore",self.base_module.vpc)
            self.eks_module = CdkEksStack(self, self.stack_name + "-eks", self.base_module.vpc)
            self.ecs_module = CdkEcsStack(self, self.stack_name + "-ecs", self.base_module.vpc)
            self.pipeline_module = CdkPipelineStack(self, self.stack_name + "-pipeline", self.base_module.vpc)
            self.pipeline_dotnet_module = CdkPipelineDotNetStack(self, self.stack_name + "-pipeline-dotnet", self.base_module.vpc)
            self.redis_elasticache = CdkRedisStack(self, self.stack_name + "-redis-elasticache", self.base_module.vpc)
#            self.emr_module = CdkEmrStack(self, self.stack_name + "-emr", self.base_module.vpc)
            self.es_module =  CdkElasticsearchStack(self, self.stack_name + "-es", self.base_module.vpc)


if __name__ == '__main__':
    app = GravitonID()
    app.synth()
