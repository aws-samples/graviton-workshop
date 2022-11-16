# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3

import os
import aws_cdk as cdk
from graviton2.rds_graviton.rds_mysql_5 import CdkRds5Stack
from graviton2.rds_graviton.rds_mysql_8 import CdkRds8Stack
from graviton2.rds_graviton.rds_restore import CdkRdsRestoreStack
from graviton2.cs_graviton.ecs_graviton2 import CdkEcsStack
from graviton2.cs_graviton.pipeline_graviton2 import CdkPipelineStack
from graviton2.cs_graviton.pipeline_netcore_graviton2 import CdkPipelineDotNetStack
from graviton2.elasticsearch_graviton.es import CdkElasticsearchStack
#from graviton2.emr_graviton.emr_graviton2 import CdkEmrStack


class GravitonID(cdk.App):

        def __init__(self, vpc_id: str, es_domain: str, es_endpoint: str, **kwargs):
            super().__init__(**kwargs)

            env = cdk.Environment(
                account=os.environ['CDK_DEPLOY_ACCOUNT'],
                region=os.environ['CDK_DEPLOY_REGION']
            )

            self.stack_name = "GravitonID"
            self.rds_5_module = CdkRds5Stack(self, self.stack_name + "-rds-5", env=env, vpc_id=vpc_id)
            self.rds_8_module = CdkRds8Stack(self, self.stack_name + "-rds-8", env=env, vpc_id=vpc_id)
            self.restore_module = CdkRdsRestoreStack(self, self.stack_name + "-rds-restore", env=env, vpc_id=vpc_id)
            self.ecs_module = CdkEcsStack(self, self.stack_name + "-ecs", env=env, vpc_id=vpc_id)
            self.pipeline_module = CdkPipelineStack(self, self.stack_name + "-pipeline", env=env)
            self.pipeline_dotnet_module = CdkPipelineDotNetStack(self, self.stack_name + "-pipeline-dotnet", env=env)
#            self.emr_module = CdkEmrStack(self, self.stack_name + "-emr", self.base_module.vpc, env=env)
            self.es_module =  CdkElasticsearchStack(self, self.stack_name + "-es", env=env, vpc_id=vpc_id, es_domain=es_domain, es_endpoint=es_endpoint)


if __name__ == '__main__':
    app = GravitonID(
        vpc_id=os.environ['VPC_ID'],
        es_domain=os.environ['ES_DOMAIN_NAME'],
        es_endpoint=os.environ['ES_ENDPOINT'],
    )
    app.synth()
